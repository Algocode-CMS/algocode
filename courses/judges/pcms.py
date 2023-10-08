import os
import json

from algocode.settings import PCMS_STANDINGS
from courses.models import Participant

from courses.judges.common_verdicts import EJUDGE_OK


def load_pcms_contest(contest, users):
    standings_file = os.path.join(PCMS_STANDINGS, contest.external_group_id)
    with open(standings_file) as standings_reader:
        data = json.load(standings_reader)

    contest = data["standings"]["contest"][0]

    problems = [{
        'id': str(i),
        'long': problem["name"],
        'short': problem["alias"],
        'index': i,
    } for i, problem in enumerate(contest["challenge"][0]["problem"])]

    problem_index = {problem['short']: problem['index'] for problem in problems}

    runs_list = []

    for session in contest["session"]:
        user_login = session["alias"]
        if user_login not in users:
            users[user_login] = [participant.id for participant in Participant.objects.filter(pcms_login=user_login)]
        for user_id in users[user_login]:
            for problem in session["problem"]:
                attempts = problem["attempts"]
                if attempts == 0:
                    continue

                problem_id = problem["alias"]
                prob_id = problem_index[problem_id]
                score = problem["score"]
                time = problem["time"] / 1000
                runs_list.append({
                    'user_id': user_id,
                    'status': EJUDGE_OK,
                    'time': time,
                    'utc_time': time,
                    'prob_id': prob_id,
                    'score': score,
                })

    return [problems, runs_list]