import requests
from bs4 import BeautifulSoup
import re
import os
import json

from django.core.management.base import BaseCommand

from algocode import settings
from courses.models import Contest


class InformaticsLoader:
    LOGIN_PAGE = 'https://informatics.msk.ru/login/index.php'
    CONTEST_TEMPLATE = 'https://informatics.msk.ru/mod/statements/view3.php?id={}'
    SUBMISSIONS_TEMPLATE = 'https://informatics.msk.ru/py/problem/0/filter-runs?' + \
                           'problem_id=0&from_timestamp=-1&to_timestamp=-1&' + \
                           'user_id=0&with_comment=&lang_id=-1&status_id=-1&' + \
                           'page={}&statement_id={}&group_id={}&count=100'

    def __init__(self, login, password):
        self.login = login
        self.password = password
        self.WAS_AUTHORIZED = False
        self.session = requests.Session()

    def get_html(self, url):
        if not self.WAS_AUTHORIZED:
            self.session.get(self.LOGIN_PAGE)
            post_data = {'username': self.login, 'password': self.password}
            self.session.post(self.LOGIN_PAGE, post_data)
            self.WAS_AUTHORIZED = True
        return self.session.get(url).text

    def get_submission_page_json(self, page_id, group_id, contest_id):
        url = self.SUBMISSIONS_TEMPLATE.format(page_id, contest_id, group_id)
        text = self.get_html(url)
        return json.loads(text)

    def get_problems(self, contest_id):
        url = self.CONTEST_TEMPLATE.format(contest_id)
        contest_html = self.get_html(url)
        soup = BeautifulSoup(contest_html, 'lxml')
        result = []
        statements = soup.find_all("div", class_='statements_toc_alpha')[0]
        for problem_part in statements.find_all('li'):
            problem_name = problem_part.get_text()
            problem_id = int(re.search(r'chapterid=(\d+)',
                problem_part.find_all('a')[0]['href']).group(1))
            result.append([problem_name[7:8], problem_name[10:], problem_id])
        return result

    def get_data(self, group_id, contest_id):
        problems = self.get_problems(contest_id)
        num_problems = len(problems)
        problem_id_to_order_id = {x[2]: i for i, x in enumerate(problems)}

        first_page = self.get_submission_page_json(1, group_id, contest_id)
        num_pages = first_page['metadata']['page_count']

        user_stat = {}
        for page_id in range(1, num_pages + 1):
            if page_id == 1:
                page_data = first_page
            else:
                page_data = self.get_submission_page_json(page_id, group_id, contest_id)
            for submission in page_data['data']:
                user_id = submission['user']['id']
                problem_id = submission['problem']['id']
                problem_order_id = problem_id_to_order_id[problem_id]
                if user_id not in user_stat:
                    user_stat[user_id] = {'ok': [0 for _ in range(num_problems)],
                                          'wrong_tries': [0 for _ in range(num_problems)]}
                if (submission['ejudge_status'] == 0):
                    user_stat[user_id]['ok'][problem_order_id] = 1
                    user_stat[user_id]['wrong_tries'][problem_order_id] = 0
                if (submission['ejudge_score'] is not None and \
                    submission['ejudge_score'] < 100):
                    user_stat[user_id]['wrong_tries'][problem_order_id] += 1

        results = {}
        for user_id, user_data in user_stat.items():
            user_line = []
            for ok, wrong_tries in zip(user_data['ok'], user_data['wrong_tries']):
                if ok:
                    if wrong_tries:
                        user_line.append('+{}'.format(wrong_tries))
                    else:
                        user_line.append('+')
                else:
                    if wrong_tries:
                        user_line.append('-{}'.format(wrong_tries))
                    else:
                        user_line.append('.')
            results[user_id] = user_line
        problem_names = [[x[0], x[1]] for x in problems]

        return {
            'problems': problem_names, # [["A", "Название"], ...]
            'results': results, # словарь user_id: ["+4", ".", ...]
        }


class Command(BaseCommand):
    help = 'Loads data from informatics'

    def handle(self, *args, **options):
        loader = InformaticsLoader(settings.INFORMATICS_LOGIN, settings.INFORMATICS_PASSWORD)
        contests = Contest.objects.filter(judge=Contest.INFORMATICS)
        data_dir = os.path.join(settings.BASE_DIR, 'judges_data', Contest.INFORMATICS)
        os.makedirs(data_dir, exist_ok=True)

        for contest in contests:
            try:
                data = loader.get_data(contest.external_group_id, contest.contest_id)
                with open(os.path.join(data_dir, str(contest.id)), 'w') as file:
                    file.write(json.dumps(data))
                    print('Successfully updated contest {}'.format(contest.contest_id))
            except Exception as e:
                print('Error, contest {}'.format(contest.contest_id))
                print(e)

        print('Informatics loaded!')
