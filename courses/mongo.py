from algocode.settings import MONGO
from pymongo import MongoClient


def mongo_enabled():
    return "connection_string" in MONGO and MONGO["connection_string"] != ""


def get_db():
    if not mongo_enabled():
        return None
    try:
        client = MongoClient(MONGO["connection_string"])
        return client["algocode"]
    except:
        return None


def upload_standings(contest, standings):
    try:
        db = get_db()
        if db is None:
            return False
        db["standings"].update_one({"id": contest.id}, {"$set": {"standings": standings}}, True)
        db["standings"].create_index("id")
        if contest.standings_holder.count() != 0:
            contest.standings_holder.get().delete()
        return True
    except Exception as e:
        return False


def load_standings(contest_id):
    try:
        client = get_db()
        standings = client["standings"].find_one({"id": contest_id})
        if standings is None:
            return [[], []]
        else:
            return standings["standings"]
    except:
        return [[], []]

