from courses.judges.ejudge import load_ejudge_contest
from courses.judges.external import load_external_contest
from courses.judges.process_contest import process_contest


def load_contest(contest, users, **kwargs):
    try:
        if contest.judge == contest.EJUDGE:
            problems, runs_list = load_ejudge_contest(contest, users)
        else:
            problems, runs_list = load_external_contest(contest)
        return process_contest(runs_list, problems, contest, users, **kwargs)
    except:
        return None
