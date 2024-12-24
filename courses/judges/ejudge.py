import datetime
import pytz
import untangle
import os
from algocode.settings import JUDGES_DIR, TIME_ZONE
from courses.judges.common_verdicts import *


def localize_time(time_str):
    try:
        time_dt = datetime.datetime.strptime(time_str, "%Y/%m/%d %H:%M:%S")
    except:
        time_dt = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    time_dt = pytz.timezone(TIME_ZONE).localize(time_dt)
    return time_dt.astimezone(pytz.timezone('UTC')).timestamp()


def load_ejudge_contest(contest, users):
    ejudge_id = '{:06d}'.format(contest.contest_id)
    try:
        data = untangle.parse(os.path.join(JUDGES_DIR, ejudge_id, 'var/status/dir/external.xml'))
    except:
        return None

    start_time = localize_time(data.runlog["start_time"])

    ejudge_ids = {}
    for user in users:
        ejudge_ids[user.ejudge_id] = user.id

    contest_users_start = {}
    for user in data.runlog.users.children:
        contest_users_start[int(user['id'])] = 0
    contest_users_finished = set()

    problems = [{
        'id': problem['id'],
        'long': problem['long_name'],
        'short': problem['short_name'],
        'index': index,
    } for index, problem in enumerate(data.runlog.problems.children)]

    problem_index = {problem['id']: problem['index'] for problem in problems}

    runs_list = []

    deadline = 10 ** 18
    if contest.deadline is not None:
        deadline = contest.deadline.timestamp()

    now_time = datetime.datetime.now()
    now_time = pytz.timezone(TIME_ZONE).localize(now_time)
    now_timestamp = now_time.astimezone(pytz.timezone('UTC')).timestamp()

    if hasattr(data.runlog, "userrunheaders"):
        if data.runlog.userrunheaders is not None:
            for user_header in data.runlog.userrunheaders.children:
                ejudge_id = int(user_header["user_id"])
                if ejudge_id not in ejudge_ids:
                    continue
                if user_header.get_attribute("start_time") is not None:
                    user_start_utc = localize_time(user_header["start_time"])
                    time = user_start_utc - start_time
                    contest_users_start[ejudge_id] = time
                    if contest.duration != 0 and contest.duration + user_start_utc < now_timestamp:
                        contest_users_finished.add(ejudge_id)
                if user_header.get_attribute("stop_time") is not None:
                    contest_users_finished.add(ejudge_id)


    for run in data.runlog.runs.children:
        try:
            ejudge_id = int(run['user_id'])
            if contest.score_only_finished and ejudge_id not in contest_users_finished:
                continue
            status = run['status']
            time = int(run['time'])
            utc_time = start_time + time
            if status == EJUDGE_VIRTUAL_STOP or ejudge_id not in ejudge_ids:
                continue
            if status == EJUDGE_VIRTUAL_START:
                contest_users_start[ejudge_id] = time
                continue
            time -= contest_users_start[ejudge_id]
            if contest.deadline is not None and deadline < utc_time:
                continue
            if contest.duration != 0 and time > contest.duration * 60:
                continue

            user_id = ejudge_ids[ejudge_id]

            prob_id = problem_index[run['prob_id']]
            score = (1 if status == EJUDGE_OK else 0)
            if contest.contest_type == contest.OLYMP and run['score'] is not None:
                score = int(run['score'])
                status = EJUDGE_PT
            if run['status'] == 'DQ':
                score = 0
                status = EJUDGE_DQ

            rn = {
                'user_id': user_id,
                'status': status,
                'time': time,
                'utc_time': utc_time,
                'prob_id': prob_id,
                'score': score,
            }

            if run['group_scores'] is not None:
                rn['groups'] = [int(i) for i in run['group_scores'].split()]
            runs_list.append(rn)
        except:
            pass

    return [problems, runs_list]
