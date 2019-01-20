import os
import json

from algocode import settings


def load_external_contest(contest, users):
    file_path = os.path.join(settings.BASE_DIR, 'judges_data', contest.judge, str(contest.id))
    if not os.path.exists(file_path):
        return None

    with open(file_path) as file:
        data = json.loads(file.read())

    problems = [{
        'id': index,
        'long': problem[1],
        'short': problem[0],
        'index': index,
    } for index, problem in enumerate(data['problems'])]

    user_info = {}
    external_ids = {}
    for user in users:
        user_info[user.id] = [{
            'score': 0,
            'penalty': 0,
            'verdict': None,
        } for _ in range(len(problems))]

        if contest.judge == contest.INFORMATICS and user.informatics_id:
            external_ids[str(user.informatics_id)] = user.id
        if contest.judge == contest.CODEFORCES and user.codeforces_handle:
            external_ids[user.codeforces_handle] = user.id

    for external_id, result in data['results'].items():
        if external_id not in external_ids:
            continue
        user_id = external_ids[external_id]
        for prob_id, status in enumerate(result):
            score = 0
            penalty = 0
            verdict = None

            if len(status) > 1 and status[0] in ('+', '-'):
                try:
                    penalty = int(status[1:])
                except ValueError:
                    pass

            if status.startswith('+'):
                verdict = 'OK'
                score = 1
            elif status.startswith('-'):
                verdict = 'BAD'

            user_info[user_id][prob_id] = {
                'score': score,
                'penalty': penalty,
                'verdict': verdict,
            }

    return {
        'id': contest.id,
        'date': contest.date,
        'external_id': contest.contest_id,
        'title': contest.title,
        'coefficient': contest.coefficient,
        'problems': problems,
        'users': user_info,
    }


