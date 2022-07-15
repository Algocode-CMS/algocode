import json

from algocode import settings
from courses import mongo


def load_from_db(contest):
    standings = [[], []]
    try:
        standings = contest.standings_holder.get()
        standings = [
            json.loads(standings.problems),
            json.loads(standings.runs_list),
        ]
    except:
        pass

    if mongo.upload_standings(contest, standings):
        try:
            contest.standings_holder.get().delete()
        except:
            pass

    return standings


def load_external_contest(contest):
    if contest.standings_holder.count() > 0 or "connection_string" not in settings.MONGO:
        return load_from_db(contest)
    else:
        return mongo.load_standings(contest.id)

