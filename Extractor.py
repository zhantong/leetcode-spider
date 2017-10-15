import urllib.request
import urllib.parse
import http.cookiejar
import json
from lxml import etree
import os
import concurrent.futures
import re
import sqlite3
import codecs
import shutil


class Extractor:
    def __init__(self):
        self.base_url = 'https://leetcode.com/'
        cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        self.opener.addheaders = [
            ('Host', 'leetcode.com'),
            ('User-Agent',
             'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')
        ]
        self.is_logged_in = False

    def login(self, user_name, password):
        if self.is_logged_in:
            return
        with self.opener.open(self.base_url + 'accounts/login/') as f:
            content = f.read().decode('utf-8')
        token = re.findall("name='csrfmiddlewaretoken'\svalue='(.*?)'", content)[0]
        post_data = {
            'csrfmiddlewaretoken': token,
            'login': user_name,
            'password': password
        }
        post_data = urllib.parse.urlencode(post_data)
        self.opener.addheaders.append(('Referer', 'https://leetcode.com/accounts/login/'))
        with self.opener.open(self.base_url + 'accounts/login/', data=post_data.encode()) as f:
            if f.read().decode().find('Successfully signed in') != -1:
                self.is_logged_in = True
                print('Successfully signed in')
            else:
                print('Failed sign in')
        self.opener.addheaders.pop()

    def get_problem_list(self):
        with self.opener.open(self.base_url + 'api/problems/algorithms/') as f:
            content = f.read().decode('utf-8')
        content = json.loads(content)
        return content['stat_status_pairs']

    def get_description(self, slug, is_encoded=True):
        url = self.base_url + 'problems/' + slug + '/description/'
        print(url)
        with self.opener.open(url) as f:
            content = f.read().decode('utf-8')
        root = etree.HTML(content)
        result = root.xpath('//*[@id="descriptionContent"]//div[@class="question-description"]')
        html = etree.tostring(result[0], encoding='utf-8')
        if not is_encoded:
            return html.decode('utf-8')
        return html

    def get_submission_list(self):
        if not self.is_logged_in:
            print('should login first')
            return
        result = []
        offset = 0
        LIMIT = 100
        while True:
            url = self.base_url + 'api/submissions/?offset=' + str(offset) + '&limit=' + str(LIMIT)
            with self.opener.open(url) as f:
                content = f.read().decode('utf-8')
            content = json.loads(content)
            result.extend(content['submissions_dump'])
            if not content['has_next']:
                return result
            offset += LIMIT

    def store_submission_list_to_db(self, submission_list):
        conn = sqlite3.connect('leetcode.db')
        c = conn.cursor()
        c.execute(
            'CREATE TABLE IF NOT EXISTS submission (lang TEXT,title TEXT,url TEXT,downloaded INTEGER DEFAULT 0,path TEXT,PRIMARY KEY(url))')
        for submission in submission_list:
            if submission['status_display'] == 'Accepted':
                c.execute('INSERT OR IGNORE INTO submission (lang,title,url) VALUES (?,?,?)',
                          (submission['lang'], submission['title'], submission['url']))
        conn.commit()
        conn.close()

    def get_submission(self, url, file_path):
        with self.opener.open(url) as f:
            content = f.read().decode('utf-8')
            code = re.findall("submissionCode:\s'(.*?)',", content)[0]
            code = codecs.decode(code, 'unicode-escape')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
        return file_path

    def extract_submissions(self):
        conn = sqlite3.connect('leetcode.db')
        c = conn.cursor()
        c.execute('SELECT url FROM submission WHERE downloaded=0')
        urls = c.fetchall()
        urls = [url[0] for url in urls]
        dir_path = 'submissions/'
        os.makedirs(dir_path, exist_ok=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(self.get_submission, 'https://www.leetcode.com' + url,
                                       os.path.join(dir_path, url.split('/')[-2])): url for url in urls}
            for future in concurrent.futures.as_completed(futures):
                url = futures[future]
                try:
                    file_path = future.result()
                except Exception as e:
                    print('%r generated an exception: %s' % (url, e))
                else:
                    if file_path:
                        c.execute('UPDATE submission SET downloaded=1,path=? WHERE url=?', (file_path, url))
        conn.commit()
        conn.close()

    def output_submissions(self, dir_path='out_submissions/'):
        def lang_to_language(lang):
            if lang == 'python' or lang == 'python3':
                return 'Python'
            if lang == 'java':
                return 'Java'
            if lang == 'cpp':
                return 'C++'

        def lang_to_extension(lang):
            if lang == 'python' or lang == 'python3':
                return '.py'
            if lang == 'java':
                return '.java'
            if lang == 'cpp':
                return '.cpp'

        os.makedirs(dir_path, exist_ok=True)
        conn = sqlite3.connect('leetcode.db')
        c = conn.cursor()
        c.execute('SELECT title FROM submission WHERE downloaded=1 GROUP BY title')
        titles = c.fetchall()
        titles = [title[0] for title in titles]
        print(titles)
        for title in titles:
            problem_dir = os.path.join(dir_path, title)
            os.makedirs(problem_dir, exist_ok=True)
            c.execute('SELECT lang FROM submission WHERE downloaded=1 AND title=?', (title,))
            langs = c.fetchall()
            langs = [lang[0] for lang in langs]
            for lang in langs:
                current_dir = os.path.join(problem_dir, lang_to_language(lang))
                os.makedirs(current_dir, exist_ok=True)
                c.execute('SELECT path FROM submission WHERE downloaded=1 AND title=? AND lang=? ORDER BY url',
                          (title, lang))
                orig_file_paths = c.fetchall()
                orig_file_paths = [orig_file_path[0] for orig_file_path in orig_file_paths]
                shutil.copyfile(orig_file_paths[0], os.path.join(current_dir, 'Submission' + lang_to_extension(lang)))
                for i in range(1, len(orig_file_paths)):
                    shutil.copyfile(orig_file_paths[0],
                                    os.path.join(current_dir, 'Submission ' + 'I' * (i + 1) + lang_to_extension(lang)))

        conn.close()

    def extract(self, problem, dir_path):
        if problem['paid_only']:
            return
        index = str(problem['stat']['question_id'])
        title = problem['stat']['question__title']
        slug = problem['stat']['question__title_slug']
        description = self.get_description(slug)
        file_path = os.path.join(dir_path, index.zfill(3) + '. ' + title + '.html')
        with open(file_path, 'wb') as f:
            f.write(description)

    def run(self, dir_path=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'descriptions'), max_workers=20):
        os.makedirs(dir_path, exist_ok=True)
        problem_list = self.get_problem_list()
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            for problem in problem_list:
                executor.submit(self.extract, problem, dir_path)


if __name__ == '__main__':
    extractor = Extractor()
    extractor.output_submissions()
