from courses.judges.judges import load_contest
from courses.models import Standings, Contest


def get_standings_data(standings: Standings):
    print(standings)
    group_list = standings.groups.all()
    if len(group_list) == 0:
        group_list = standings.course.groups.all()

    users_data = []
    users = []
    for group in group_list:
        users.extend(group.participants.all())

    user_ids = set()

    contests_models = standings.contests.filter(contest_id__isnull=False)
    contests_models |= standings.contests.filter(judge=Contest.PCMS)
    contests_models.order_by('-date', '-id')
    contests = []
    for contest_model in contests_models:
        print("AAAAA")
        contest = load_contest(contest_model, users)
        if contest is None:
            continue

        for user_id in user_ids:
            if user_id not in contest['users']:
                contest['users'][user_id] = contest['empty_row']

        for user_id in contest['users']:
            if user_id not in user_ids:
                user_ids.add(user_id)
                for i in range(len(contests)):
                    contests[i]['users'][user_id] = contests[i]['empty_row']

        contests.append(contest)

    for group in group_list:
        for user in group.participants.all():
            if user.id in user_ids:
                users_data.append({
                    'id': user.id,
                    'name': user.name,
                    'group': group.name,
                    'group_short': group.short_name,
                })

    return [users_data, contests]
