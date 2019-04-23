import requests
import os
import json

from django.core.management.base import BaseCommand

from algocode import settings
from courses.models import Contest, InformaticsToken


class InformaticsLoader:
    LOGIN_PAGE = 'https://informatics.msk.ru/login/index.php'
    STANDINGS_TEMPLATE = 'https://informatics.msk.ru/py/monitor/{}'
    GET_NEW_TOKEN_TEMPLATE = 'https://informatics.msk.ru/py/monitor?group_id={}&contest_id={}'

    def __init__(self, login, password):
        self.login = login
        self.password = password
        self.WAS_AUTHORIZED = False
        self.session = requests.Session()

    def authorize(self):
        if not self.WAS_AUTHORIZED:
            self.session.get(self.LOGIN_PAGE)
            post_data = {
                'username': self.login,
                'password': self.password
            }
            self.session.post(self.LOGIN_PAGE, post_data)
            self.WAS_AUTHORIZED = True

    def get_json_data(self, url):
        self.authorize()
        return json.loads(self.session.get(url).text)

    def get_contest_data(self, token):
        problems = self.get_json_data(self.STANDINGS_TEMPLATE.format(token))
        problems.sort(key=lambda x: x['problem']['rank'])
        num_problems = len(problems)

        user_stat = {}
        for problem_id, problem in enumerate(problems):
            for run in reversed(problem['runs']):
                user_id = run['user']['id']
                if user_id not in user_stat:
                    user_stat[user_id] = {
                        'ok': [0 for _ in range(num_problems)],
                        'wrong_tries': [0 for _ in range(num_problems)]
                    }
                if run['ejudge_status'] == 0:
                    user_stat[user_id]['ok'][problem_id] = 1
                    user_stat[user_id]['wrong_tries'][problem_id] = 0
                if run['ejudge_score'] is not None and run['ejudge_score'] < 100:
                    user_stat[user_id]['wrong_tries'][problem_id] += 1

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
            results[str(user_id)] = user_line

        problem_names = [[chr(ord('A') + x['problem']['rank'] - 1),
                          x['problem']['name']] for x in problems]
        return {
            'problems': problem_names,  # [["A", "Название"], ...]
            'results': results,  # словарь user_id: ["+4", ".", ...]
        }

    def get_new_token(self, group_id, contest_id):
        self.authorize()
        url = self.GET_NEW_TOKEN_TEMPLATE.format(group_id, contest_id)
        return json.loads(self.session.post(url).text)


class Command(BaseCommand):
    help = 'Loads data from informatics'

    def handle(self, *args, **options):
        loader = InformaticsLoader(settings.INFORMATICS_LOGIN, settings.INFORMATICS_PASSWORD)
        contests = Contest.objects.filter(judge=Contest.INFORMATICS)
        data_dir = os.path.join(settings.BASE_DIR, 'judges_data', Contest.INFORMATICS)
        os.makedirs(data_dir, exist_ok=True)

        for contest in contests:
            try:
                token = InformaticsToken.objects.filter(
                    group_id=contest.external_group_id,
                    contest_id=contest.contest_id
                ).first()
                if token is None:
                    token = loader.get_new_token(contest.external_group_id, contest.contest_id)['link']
                    InformaticsToken.objects.create(group_id=contest.external_group_id,
                                                    contest_id=contest.contest_id,
                                                    token=token)
            except Exception as e:
                print('Error with getting token for contest {}'.format(contest.contest_id))
                print(e)
                continue

            try:
                contest_data = loader.get_contest_data(token.token)
            except Exception as e:
                print('Error with loading data for contest {}'.format(contest.contest_id))
                print(e)
                continue

            try:
                with open(os.path.join(data_dir, str(contest.id)), 'w') as file:
                    file.write(json.dumps(contest_data))
                    print('Successfully updated contest {}'.format(contest.contest_id))
            except Exception as e:
                print('Error with saving data for contest {}'.format(contest.contest_id))
                print(e)
                continue

        print('Informatics loaded!')
