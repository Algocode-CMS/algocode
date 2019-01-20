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
    STANDINGS_TEMPLATE = 'https://informatics.msk.ru/mod/statements/view3.php?id={}&standing&group_id={}'

    def __init__(self, login, password):
        self.login = login
        self.password = password
        self.WAS_AUTHORIZED = False
        self.session = requests.Session()

    def get_html(self, group_id, contest_id):
        if not self.WAS_AUTHORIZED:
            self.session.get(self.LOGIN_PAGE)
            post_data = {'username': self.login, 'password': self.password}
            self.session.post(self.LOGIN_PAGE, post_data)
            self.WAS_AUTHORIZED = True
        url = self.STANDINGS_TEMPLATE.format(contest_id, group_id)
        text = self.session.get(url).text
        return text

    def get_data(self, group_id, contest_id):
        html = self.get_html(group_id, contest_id)
        soup = BeautifulSoup(html, 'lxml')
        table = soup.find_all('table')[1].find_all('table')[1]
        new_table = []

        contest_descriptor_marker = 0
        for contest_descriptor in table.find_all('tr'):
            column_marker = 0
            columns = contest_descriptor.find_all('td')
            new_contest_descriptor = []
            for column in columns:
                if column_marker == 1:
                    text = column
                else:
                    text = column.get_text()
                new_contest_descriptor.append(text)
                column_marker += 1
            contest_descriptor_marker += 1
            new_table.append(new_contest_descriptor)

        results = {}

        problem_names = []
        problems_table = soup.find_all('table')[1].find_all('table')[-1]
        for problem_descriptor in problems_table.find_all('tr'):
            columns = problem_descriptor.find_all('td')
            new_problem_descriptor = []
            for column in columns:
                new_problem_descriptor.append(column.get_text())
            problem_names.append(new_problem_descriptor)

        for contest_descriptor in new_table[1:]:
            contest_descriptor = contest_descriptor[1:-2]
            new_contest_descriptor = []
            user_id = ""
            for j in range(len(contest_descriptor)):
                if j == 0:
                    user_id = int(re.findall(r'user_id=(\d*)', str(contest_descriptor[j]))[0])
                elif contest_descriptor[j].startswith(u'+') or contest_descriptor[j].startswith(u'-'):
                    new_contest_descriptor.append(str(contest_descriptor[j]))
                else:
                    new_contest_descriptor.append(".")
            results[user_id] = new_contest_descriptor

        problem_names = problem_names[1:]
        for i in range(len(problem_names)):
            problem_names[i][0] = problem_names[i][0].rstrip()
            problem_names[i][1] = problem_names[i][1].rstrip()

        return {
            'problems': problem_names,
            'results': results,
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
                print(e)
