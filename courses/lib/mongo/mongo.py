import pymongo

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


RUNS_BATCH_SIZE = 50 * 1000


def upload_run_list(collection, contest_id, run_list):
    batch = 0
    while batch * RUNS_BATCH_SIZE < len(run_list):
        collection.update_one(
            {"id": contest_id, "batch": batch},
            {"$set": {"runs": run_list[batch * RUNS_BATCH_SIZE:min((batch + 1) * RUNS_BATCH_SIZE, len(run_list))]}},
            True
        )
        batch += 1
    collection.create_index([("id", pymongo.ASCENDING), ("batch", pymongo.ASCENDING)])


def load_run_list(collection, contest_id):
    run_list = []
    batches = collection.find(filter={"id": contest_id}, sort=[("id", pymongo.ASCENDING), ("batch", pymongo.ASCENDING)])
    for batch in batches:
        run_list.extend(batch["runs"])
    return run_list


def upload_standings(contest, standings):
    try:
        db = get_db()
        if db is None:
            return False

        if len(standings[1]) > RUNS_BATCH_SIZE:
            upload_run_list(db["standings_runs"], contest.id, standings[1])
            standings = standings[:1]

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
            result = standings["standings"]
            if len(result) == 1:
                result.append(load_run_list(client["standings_runs"], contest_id))
            return result
    except:
        return [[], []]


def upload_ejudge_cache(contest, data):
    try:
        db = get_db()
        if db is None:
            return False
        db["ejudge_cache"].update_one({"id": contest.id}, {"$set": {"data": data}}, True)
        db["ejudge_cache"].create_index("id")
        return True
    except Exception as e:
        return False


def load_ejudge_cache(contest_id):
    try:
        client = get_db()
        data_holder = client["ejudge_cache"].find_one({"id": contest_id})
        if data_holder is None:
            return dict()
        else:
            return data_holder["data"]
    except:
        return dict()
