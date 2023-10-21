import os
import json

from algocode.settings import PCMS_STANDINGS
from courses.models import Participant

from courses.judges.common_verdicts import EJUDGE_OK, EJUDGE_WA


def load_pcms_contest(c, users):
    standings_file = os.path.join(PCMS_STANDINGS, c.external_group_id)
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

                time = problem["time"] / 1000
                if c.contest_type != c.OLYMP and "run" in problem:
                    for attempt in problem["run"]:
                        if attempt["accepted"] == "yes":
                            verdict = EJUDGE_OK
                            score = 1
                        elif attempt["accepted"] == "no":
                            verdict = EJUDGE_WA
                            score = 0
                        else:
                            continue
                        runs_list.append({
                            'user_id': user_id,
                            'status': verdict,
                            'time': attempt["time"] / 1000,
                            'utc_time': attempt["time"] / 1000,
                            'prob_id': prob_id,
                            'score': score,
                        })
                else:
                    if "score" in problem:
                        score = problem["score"]
                    else:
                        score = 1
                    runs_list.append({
                        'user_id': user_id,
                        'status': EJUDGE_OK,
                        'time': time,
                        'utc_time': time,
                        'prob_id': prob_id,
                        'score': score,
                    })

    return [problems, runs_list]