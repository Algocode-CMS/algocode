from courses.judges.ejudge import *
from courses.models import Contest, Participant
from datetime import datetime, timezone, timedelta
from courses.lib.mongo import mongo


def load_ejudge_cached_contest(contest: Contest):
    ejudge_id = '{:06d}'.format(contest.contest_id)
    try:
        data = untangle.parse(os.path.join(JUDGES_DIR, ejudge_id, 'var/status/dir/external.xml'))
    except:
        return None

    should_reload = False
    if datetime.now(timezone.utc) - contest.latest_reload_time > timedelta(minutes=15):
        should_reload = True
        contest.latest_reload_time = datetime.now(timezone.utc)
        contest.save()

    cached = mongo.load_ejudge_cache(contest.id)
    if cached is None:
        should_reload = True

    start_time = localize_time(data.runlog["start_time"])

    if not should_reload:
        try:
            ejudge_id_to_user = cached["ejudge_id_to_user"]
            contest_users_start = cached["contest_users_start"]
            contest_users_finished = cached["contest_users_finished"]
            problems = cached["problems"]
            problem_index = cached["problem_index"]
            runs_list = cached["runs_list"]
            latest_loaded_run = cached["latest_loaded_run"]
        except Exception as e:
            should_reload = True

    if should_reload:
        ejudge_id_to_user = dict()

        contest_users_start = dict()
        contest_users_finished = dict()

        problems = [{
            'id': problem['id'],
            'long': problem['long_name'],
            'short': problem['short_name'],
            'index': index,
        } for index, problem in enumerate(data.runlog.problems.children)]

        problem_index = {problem['id']: problem['index'] for problem in problems}

        runs_list = []

        if hasattr(data.runlog, "userrunheaders"):
            if data.runlog.userrunheaders is not None:
                for user_header in data.runlog.userrunheaders.children:
                    ejudge_user_id_str = user_header["user_id"]

                    if user_header.get_attribute("start_time") is None and user_header.get_attribute("stop_time") is None:
                        continue
                    if user_header.get_attribute("start_time") is not None:
                        time = localize_time(user_header["start_time"]) - start_time
                        contest_users_start[ejudge_user_id_str] = time
                    if user_header.get_attribute("stop_time") is not None:
                        contest_users_finished[ejudge_user_id_str] = True

        latest_loaded_run = -1

    for run in data.runlog.runs.children:
        try:
            run_id = int(run['run_id'])
            if run_id <= latest_loaded_run:
                continue
            latest_loaded_run = max(latest_loaded_run, run_id)

            ejudge_user_id_str = run['user_id']
            if contest.score_only_finished and ejudge_user_id_str not in contest_users_finished:
                continue

            status = run['status']
            time = int(run['time'])
            utc_time = start_time + time

            if status == EJUDGE_VIRTUAL_STOP:
                continue
            if status == EJUDGE_VIRTUAL_START:
                contest_users_start[ejudge_user_id_str] = time
                continue

            if ejudge_user_id_str not in contest_users_start:
                contest_users_start[ejudge_user_id_str] = 0
            time -= contest_users_start[ejudge_user_id_str]
            if contest.duration != 0 and time > contest.duration * 60:
                continue

            ejudge_user_id = int(ejudge_user_id_str)

            if ejudge_user_id not in ejudge_id_to_user:
                users = [participant.id for participant in Participant.objects.filter(ejudge_id=ejudge_user_id)]
                ejudge_id_to_user[ejudge_user_id_str] = users

            user_ids = ejudge_id_to_user[ejudge_user_id_str]

            prob_id = problem_index[run['prob_id']]
            score = (1 if status == EJUDGE_OK else 0)
            if contest.contest_type == contest.OLYMP and status in (EJUDGE_OK, EJUDGE_PT):
                score = int(run['score'])

            for user_id in user_ids:
                runs_list.append({
                    'user_id': user_id,
                    'status': status,
                    'time': time,
                    'utc_time': utc_time,
                    'prob_id': prob_id,
                    'score': score,
                })
        except:
            pass

    cached = dict()

    cached["ejudge_id_to_user"] = ejudge_id_to_user
    cached["contest_users_start"] = contest_users_start
    cached["contest_users_finished"] = contest_users_finished
    cached["problems"] = problems
    cached["problem_index"] = problem_index
    cached["runs_list"] = runs_list
    cached["latest_loaded_run"] = latest_loaded_run

    if not mongo.upload_ejudge_cache(contest, cached):
        print("Can not upload cached data to mongo")
        return

    if not mongo.upload_standings(contest, [problems, runs_list]):
        print("Can not upload standings to mongo")
        return

    print("Contest", contest.id, contest.title, "is loaded")

