import time
import datetime
import pytz
import random
import hashlib
import requests
import json
import os

from django.core.management.base import BaseCommand

from algocode import settings
from courses.models import Contest, Participant, ContestStandingsHolder
from courses.judges.common_verdicts import *
from courses import mongo


CODEFORCES_API_DELAY = 0.5


class CodeforcesLoader:
    STATUS_API_METHOD = 'http://codeforces.com/api/contest.status'
    STATUS_COMPLEX_STRING = '{}/contest.status?apiKey={}&contestId={}&time={}#{}'

    STANDINGS_API_METHOD = 'http://codeforces.com/api/contest.standings'
    STANDINGS_COMPLEX_STRING = '{}/contest.standings?apiKey={}&contestId={}&time={}#{}'

    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

    def get_json(self, contest_id, api_method, api_complex_string):
        cur_time = int(time.time())
        rand = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        complex_string = api_complex_string.format(rand, self.key, contest_id, cur_time, self.secret)

        hash = hashlib.sha512(complex_string.encode('utf-8')).hexdigest()

        response = requests.get(api_method,
                                params={
                                    'contestId': contest_id,
                                    'apiKey': self.key,
                                    'time': cur_time,
                                    'apiSig': rand + hash
                                })
        return json.loads(response.text)

    def get_data(self, contest_id):
        standings_json_values = self.get_json(contest_id, self.STANDINGS_API_METHOD, self.STANDINGS_COMPLEX_STRING)
        last_query = time.time()

        num_problems = 0
        problems = []

        for problem_descriptor in standings_json_values['result']['problems']:
            num_problems += 1
            problems.append({
                'id': num_problems,
                'long': problem_descriptor['name'],
                'short': problem_descriptor['index'],
                'index': num_problems - 1,
            })

        problem_index = {problem['short']: problem['index'] for problem in problems}

        while time.time() - last_query < CODEFORCES_API_DELAY:
            time.sleep(0.01)

        status_json_values = self.get_json(contest_id, self.STATUS_API_METHOD, self.STATUS_COMPLEX_STRING)
        runs_list = []

        for submit in status_json_values['result']:
            if 'teamId' not in submit['author']:
                try:
                    handle = submit['author']['members'][0]['handle'].lower()
                    user_ids = Participant.objects.filter(codeforces_handle=handle)
                    status = CODEFORCES_EJUDGE_VERDICTS[submit['verdict']]
                    time_msk = datetime.datetime.fromtimestamp(submit['creationTimeSeconds'])
                    start_time = datetime.datetime.fromtimestamp(submit['author']['startTimeSeconds'])
                    submit_time = int((time_msk - start_time).total_seconds())
                    time_msk = pytz.timezone(settings.TIME_ZONE).localize(time_msk)
                    utc_time = time_msk.astimezone(pytz.timezone('UTC'))
                    prob_id = problem_index[submit['problem']['index']]
                    score = 0
                    if 'points' in submit:
                        score = submit['points']
                    elif status == EJUDGE_OK:
                        score = 1
                    for cur_user in user_ids:
                        user_id = cur_user.id
                        runs_list.append({
                            'user_id': user_id,
                            'status': status,
                            'time': submit_time,
                            'utc_time': int(utc_time.timestamp()),
                            'prob_id': prob_id,
                            'score': score,
                        })
                except:
                    pass

        return [problems, runs_list[::-1]]


def upload_standings(contest, problems, runs_list):
    if not mongo.upload_standings(contest, [problems, runs_list]):
        try:
            standings_holder = contest.standings_holder.get()
        except:
            standings_holder = ContestStandingsHolder(contest=contest)
        standings_holder.problems = json.dumps(problems)
        standings_holder.runs_list = json.dumps(runs_list)
        standings_holder.save()


class Command(BaseCommand):
    help = 'Loads data from codeforces'

    def add_arguments(self, parser):
        parser.add_argument(
            '--today',
            action='store_true',
            help='Import only recent codeforces contests',
        )

        parser.add_argument(
            '--old',
            action='store_true',
            help='Import contests older than month ago',
        )

    def handle(self, *args, **options):
        loaders = []
        for api_info in settings.CODEFORCES:
            loaders.append(CodeforcesLoader(api_info["key"], api_info["secret"]))

        if options['today']:
            date_start = datetime.datetime.now() - datetime.timedelta(days=1)
            contests = Contest.objects.filter(judge=Contest.CODEFORCES, date__gte=date_start)
        elif options['old']:
            contests = Contest.objects.filter(judge=Contest.CODEFORCES)
        else:
            date_start = datetime.datetime.now() - datetime.timedelta(days=31)
            contests = Contest.objects.filter(judge=Contest.CODEFORCES, date__gte=date_start)

        data_dir = os.path.join(settings.BASE_DIR, 'judges_data', Contest.CODEFORCES)
        os.makedirs(data_dir, exist_ok=True)

        last_query = 0
        for contest in contests:
            print("loading ", contest.contest_id)
            for loader in loaders:
                while time.time() - last_query < CODEFORCES_API_DELAY * 3:
                    time.sleep(0.01)
                last_query = time.time()
                try:
                    problems, runs_list = loader.get_data(contest.contest_id)
                    if len(problems) == 0:
                        continue
                    upload_standings(contest, problems, runs_list)
                    print('success')
                    break
                except Exception as e:
                    print('Error, contest {}'.format(contest.contest_id))
                    print(e)

        print('Codeforces loaded!')
