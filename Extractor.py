import urllib.request
import urllib.parse
import http.cookiejar
import json
from lxml import etree
import os
import concurrent.futures
import re


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
    extractor.run()
