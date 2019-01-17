from courses.judges.ejudge import load_ejudge_contest
from courses.judges.external import load_external_contest


def load_contest(contest, users):
    if contest.judge == contest.EJUDGE:
        return load_ejudge_contest(contest, users)
    if contest.judge in (contest.CODEFORCES, contest.INFORMATICS):
        return load_external_contest(contest, users)
    raise NotImplementedError
