import json

from algocode import settings


def load_external_contest(contest):
    try:
        standings = contest.standings_holder.get()
        return [
            json.loads(standings.problems),
            json.loads(standings.runs_list),
        ]
    except:
        return [[], []]


