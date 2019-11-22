import datetime

import pytz
import untangle
import os
from algocode.settings import JUDGES_DIR, TIME_ZONE
from courses.models import BlitzProblemStart, BlitzProblem

EJUDGE_VIRTUAL_START = 'VS'
EJUDGE_VIRTUAL_STOP = 'VT'
EJUDGE_OK = 'OK'  # OK
EJUDGE_PT = 'PT'  # Partial score
EJUDGE_WA = 'WA'  # Wrong answer
EJUDGE_RT = 'RT'  # Runtime error
EJUDGE_TL = 'TL'  # Time limit exceeded
EJUDGE_PE = 'PE'  # Presentation error
EJUDGE_ML = 'ML'  # Memory limit exceeded
EJUDGE_SE = 'SE'  # Security violation
EJUDGE_BAD_VERDICTS = [EJUDGE_WA, EJUDGE_RT, EJUDGE_TL, EJUDGE_PE, EJUDGE_ML, EJUDGE_SE, EJUDGE_PT]
BLITZ_PENDING = 'BP'  # Pending submission
BLITZ_TE = 'TE'  # Time exceeded


def load_ejudge_contest(contest, users):
    ejudge_id = '{:06d}'.format(contest.contest_id)
    try:
        data = untangle.parse(os.path.join(JUDGES_DIR, ejudge_id, 'var/status/dir/external.xml'))
    except:
        return None

    start_time = data.runlog["start_time"]
    start_time = datetime.datetime.strptime(start_time, "%Y/%m/%d %H:%M:%S")
    start_time = pytz.timezone(TIME_ZONE).localize(start_time)
    start_time = start_time.astimezone(pytz.timezone('UTC'))

    ejudge_ids = {}
    for user in users:
        ejudge_ids[user.ejudge_id] = user.id

    contest_users_start = {}
    for user in data.runlog.users.children:
        contest_users_start[int(user['id'])] = 0

    problems = [{
        'id': problem['id'],
        'long': problem['long_name'],
        'short': problem['short_name'],
        'index': index,
    } for index, problem in enumerate(data.runlog.problems.children)]

    user_info = {}
    for user in users:
        user_info[user.id] = []
        for i in range(len(problems)):
            user_info[user.id].append({
                'score': 0,
                'penalty': 0,
                'verdict': None,
                'time': 0,
                'bid': 0,
                'initial_bid': 0,
            })

    for run in data.runlog.runs.children:
        try:
            ejudge_id = int(run['user_id'])
            status = run['status']
            time = int(run['time'])
            if status == EJUDGE_VIRTUAL_STOP or ejudge_id not in ejudge_ids:
                continue
            if status == EJUDGE_VIRTUAL_START:
                contest_users_start[ejudge_id] = time
                continue
            time -= contest_users_start[ejudge_id]
            if contest.duration != 0 and time > contest.duration * 60:
                continue

            user_id = ejudge_ids[ejudge_id]
            prob_id = int(run['prob_id']) - 1
            score = (1 if status == EJUDGE_OK else 0)
            if contest.contest_type == contest.OLYMP and status in (EJUDGE_OK, EJUDGE_PT):
                score = int(run['score'])

            if contest.contest_type == contest.BLITZ:
                try:
                    problem = BlitzProblem.objects.get(problem_id=problems[prob_id]['short'], contest=contest)
                    start = BlitzProblemStart.objects.get(problem=problem, participant_id=ejudge_id)
                    time -= (start.time - start_time).total_seconds()
                    print(time, start.time)
                    if time > start.bid * 60:
                        continue
                except:
                    continue

            info = user_info[user_id][prob_id]
            if info['verdict'] == EJUDGE_OK:
                continue
            if status in EJUDGE_BAD_VERDICTS:
                info['penalty'] += 1
            info['score'] = max(info['score'], score)
            info['verdict'] = status
            info['time'] = time
        except:
            pass

    curr_time = curr_time = datetime.datetime.now(datetime.timezone.utc)
    for user in users:
        for i, problem in enumerate(problems):
            if contest.contest_type == contest.BLITZ:
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

    return {
        'id': contest.id,
        'date': contest.date,
        'start_time': start_time.timestamp(),
        'ejudge_id': contest.contest_id,
        'title': contest.title,
        'coefficient': contest.coefficient,
        'problems': problems,
        'users': user_info,
    }
