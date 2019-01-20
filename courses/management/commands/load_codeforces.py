import time
import random
import hashlib
import requests
import json
import os

from django.core.management.base import BaseCommand

from algocode import settings
from courses.models import Contest


CODEFORCES_API_DELAY = 0.2


class CodeforcesLoader:
    API_METHOD = 'http://codeforces.com/api/contest.standings'
    COMPLEX_STRING = '{}/contest.standings?apiKey={}&contestId={}&time={}#{}'

    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

    def get_json(self, contest_id):
        cur_time = int(time.time())
        rand = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        complex_string = self.COMPLEX_STRING.format(rand, self.key, contest_id, cur_time, self.secret)

        hash = hashlib.sha512(complex_string.encode('utf-8')).hexdigest()

        response = requests.get(self.API_METHOD,
                                params={
                                    'contestId': contest_id,
                                    'apiKey': self.key,
                                    'time': cur_time,
                                    'apiSig': rand + hash
                                })
        return json.loads(response.text)

    def get_data(self, contest_id):
        json_values = self.get_json(contest_id)
        results = {}
        for contest_descriptor in json_values['result']['rows']:
            new_contest_descriptor = []
            handle = contest_descriptor['party']['members'][0]['handle']
            for problem in contest_descriptor['problemResults']:
                result = int(problem['points'])
                rejected = int(problem['rejectedAttemptCount'])
                if result == 1:
                    if rejected == 0:
                        new_contest_descriptor.append('+')
                    else:
                        new_contest_descriptor.append('+' + str(rejected))
                else:
                    if rejected == 0:
                        new_contest_descriptor.append('.')
                    else:
                        new_contest_descriptor.append('-' + str(rejected))
            results[handle] = new_contest_descriptor

        num_problems = 0
        problem_names = []
        for problem_descriptor in json_values['result']['problems']:
            num_problems += 1
            problem_names.append([problem_descriptor['index'], problem_descriptor['name']])

        return {
            'problems': problem_names,
            'results': results,
        }


class Command(BaseCommand):
    help = 'Loads data from codeforces'

    def handle(self, *args, **options):
        loader = CodeforcesLoader(settings.CODEFORCES_KEY, settings.CODEFORCES_SECRET)
        contests = Contest.objects.filter(judge=Contest.CODEFORCES)
        data_dir = os.path.join(settings.BASE_DIR, 'judges_data', Contest.CODEFORCES)
        os.makedirs(data_dir, exist_ok=True)

        last_query = 0
        for contest in contests:
            while time.time() - last_query < CODEFORCES_API_DELAY:
                time.sleep(0.01)
            last_query = time.time()
            try:
                data = loader.get_data(contest.contest_id)
                with open(os.path.join(data_dir, str(contest.id)), 'w') as file:
                    file.write(json.dumps(data))
                    print('Successfully updated contest {}'.format(contest.contest_id))
            except requests.exceptions.RequestException as e:
                print(e)
