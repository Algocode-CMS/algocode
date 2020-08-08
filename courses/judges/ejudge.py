import datetime
import pytz
import untangle
import os
from algocode.settings import JUDGES_DIR, TIME_ZONE
from courses.judges.common_verdicts import *


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

    problem_index = {problem['id']: problem['index'] for problem in problems}

    runs_list = []

    for run in data.runlog.runs.children:
        try:
            ejudge_id = int(run['user_id'])
            status = run['status']
            time = int(run['time'])
            utc_time = start_time.timestamp() + time
            if status == EJUDGE_VIRTUAL_STOP or ejudge_id not in ejudge_ids:
                continue
            if status == EJUDGE_VIRTUAL_START:
                contest_users_start[ejudge_id] = time
                continue
            time -= contest_users_start[ejudge_id]
            if contest.duration != 0 and time > contest.duration * 60:
                continue

            user_id = ejudge_ids[ejudge_id]

            prob_id = problem_index[run['prob_id']]
            score = (1 if status == EJUDGE_OK else 0)
            if contest.contest_type == contest.OLYMP and status in (EJUDGE_OK, EJUDGE_PT):
                score = int(run['score'])


            runs_list.append({
                'user_id': user_id,
                'status': status,
                'time': time,
                'utc_time': utc_time,
                'prob_id': prob_id,
                'score': score,
            })
        except:
            pass

    return [problems, runs_list]
