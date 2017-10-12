import urllib.request
import http.cookiejar
import json
from lxml import etree
import os
import concurrent.futures


class Extractor:
    def __init__(self):
        self.base_url = 'https://leetcode.com/'
        cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener()
        self.opener.addheaders = [
            ('Host', 'leetcode.com'),
            ('User-Agent',
             'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')
        ]

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
        result = root.xpath('//*[@id="descriptionContent"]/div[1]/div/div[2]')
        html = etree.tostring(result[0], encoding='utf-8')
        if not is_encoded:
            return html.decode('utf-8')
        return html

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
