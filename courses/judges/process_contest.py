import datetime
import json

from courses.models import BlitzProblemStart, BlitzProblem
from courses.judges.common_verdicts import *


def process_contest(runs_list, problems, contest, users, **kwargs):
    user_info = {}
    save_utc = False
    if 'utc_time' in kwargs and kwargs['utc_time']:
        save_utc = True

    user_ids = {user.id for user in users}

    empty_row = []
    for i in range(len(problems)):
        empty_row.append({
            'score': 0,
            'penalty': 0,
            'verdict': None,
            'time': 0,
        })
        if save_utc:
            empty_row[-1]["utc_time"] = 0

    if 'required_users' in kwargs and kwargs['required_users']:
        for user in kwargs['required_users']:
            user_info[user.id] = []
            for i in range(len(problems)):
                user_info[user.id].append({
                    'score': 0,
                    'penalty': 0,
                    'verdict': None,
                    'time': 0,
                })
                if save_utc:
                    user_info[user.id][-1]["utc_time"] = 0

    for run in runs_list:
        try:
            user_id = run['user_id']

            if user_id not in user_ids:
                continue

            status = run['status']
            time = run['time']
            utc_time = run['utc_time']
            if contest.duration != 0 and time > contest.duration * 60:
                continue

            prob_id = run['prob_id']
            score = run['score']

            if user_id not in user_info:
                user_info[user_id] = []
                for i in range(len(problems)):
                    user_info[user_id].append({
                        'score': 0,
                        'penalty': 0,
                        'verdict': None,
                        'time': 0,
                    })
                    if save_utc:
                        user_info[user_id][-1]["utc_time"] = 0

            info = user_info[user_id][prob_id]

            if contest.contest_type == contest.BLITZ:
                try:
                    problem = BlitzProblem.objects.get(problem_id=problems[prob_id]['short'], contest=contest)
                    start = BlitzProblemStart.objects.get(problem=problem, participant_id=user_id)
                    blitz_time = utc_time - start.time.total_seconds()
                    if blitz_time > start.bid * 60:
                        continue
                    info["blitz_time"] = blitz_time
                except:
                    continue

            if info['verdict'] == EJUDGE_OK and not contest.score_latest:
                continue
            if status in EJUDGE_BAD_VERDICTS:
                info['penalty'] += 1
            if not contest.score_latest:
                info['score'] = max(info['score'], score)
            else:
                info['score'] = score
            info['verdict'] = status
            info['time'] = time
            if save_utc:
                info['utc_time'] = utc_time
        except:
            pass

    if contest.contest_type == contest.BLITZ:
        curr_time = datetime.datetime.now(datetime.timezone.utc)
        for user in users:
            for i, problem in enumerate(problems):
                if contest.contest_type == contest.BLITZ:
                    user_info[user.id][i]['initial_bid'] = 0
                    user_info[user.id][i]['bid'] = 0
                    try:
                        problem = BlitzProblem.objects.get(problem_id=problem['short'], contest=contest)
                        start = BlitzProblemStart.objects.get(participant_id=user.ejudge_id, problem=problem)
                        user_info[user.id][i]['initial_bid'] = start.bid
                        if user_info[user.id][i]['verdict'] == EJUDGE_OK:
                            user_info[user.id][i]['bid'] = start.bid
                            user_info[user.id][i]['score'] = start.bid
                        elif (curr_time - start.time).total_seconds() < start.bid * 60:
                            user_info[user.id][i]['bid'] = (start.bid * 60 - int((curr_time - start.time).total_seconds())) // 60
                            if user_info[user.id][i]['penalty'] == 0:
                                user_info[user.id][i]['verdict'] = BLITZ_PENDING
                        else:
                            user_info[user.id][i]['verdict'] = BLITZ_TE
                    except:
                        pass

    try:
        contest_info = json.loads(contest.contest_info)
    except:
        contest_info = dict()

    return {
        'id': contest.id,
        'date': contest.date,
        'ejudge_id': contest.contest_id,
        'title': contest.title,
        'coefficient': contest.coefficient,
        'problems': problems,
        'users': user_info,
        'contest_info': contest_info,
        'empty_row': empty_row,
    }