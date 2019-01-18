import untangle
import os
from algocode.settings import JUDGES_DIR


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


def load_ejudge_contest(contest, users):
    ejudge_id = '{:06d}'.format(contest.contest_id)
    try:
        data = untangle.parse(os.path.join(JUDGES_DIR, ejudge_id, 'var/status/dir/external.xml'))
    except:
        return None
    ejudge_ids = {}
    for user in users:
        ejudge_ids[user.ejudge_id] = user.id

    contest_users_start = {}
    for user in data.runlog.users.children:
        contest_users_start[user['id']] = 0

    problems = [{
        'id': problem['id'],
        'long': problem['long_name'],
        'short': problem['short_name'],
        'index': index,
    } for index, problem in enumerate(data.runlog.problems.children)]

    user_info = {}
    for user in users:
        user_info[user.id] = [{
            'score': 0,
            'penalty': 0,
            'verdict': None,
        } for _ in range(len(problems))]

    for run in data.runlog.runs.children:
        ejudge_id = int(run['user_id'])
        status = run['status']
        time = int(run['time'])
        if status == EJUDGE_VIRTUAL_STOP or ejudge_id not in ejudge_ids:
            continue
        if contest.duration != 0 and time > contest_users_start[ejudge_id] + contest.duration * 60:
            continue
        if status == EJUDGE_VIRTUAL_START:
            contest_users_start[ejudge_id] = time
            continue

        user_id = ejudge_ids[ejudge_id]
        prob_id = int(run['prob_id']) - 1
        score = (1 if status == EJUDGE_OK else 0)
        if contest.is_olymp and status in (EJUDGE_OK, EJUDGE_PT):
            score = int(run['score'])

        info = user_info[user_id][prob_id]
        if info['verdict'] == EJUDGE_OK:
            continue
        if status in EJUDGE_BAD_VERDICTS:
            info['penalty'] += 1
        info['score'] = max(info['score'], score)
        info['verdict'] = status

    return {
        'id': contest.id,
        'date': contest.date,
        'ejudge_id': contest.contest_id,
        'title': contest.title,
        'coefficient': contest.coefficient,
        'problems': problems,
        'users': user_info,
    }
