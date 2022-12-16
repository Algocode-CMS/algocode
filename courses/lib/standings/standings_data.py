from courses.judges.judges import load_contest
from courses.models import Standings


def get_standings_data(standings: Standings):
    group_list = standings.groups.all()
    if len(group_list) == 0:
        group_list = standings.course.groups.all()

    users_data = []
    users = []
    for group in group_list:
        users.extend(group.participants.all())

    for group in group_list:
        for user in group.participants.all():
            users_data.append({
                'id': user.id,
                'name': user.name,
                'group': group.name,
                'group_short': group.short_name,
            })

    contests = standings.contests.order_by('-date', '-id').filter(contest_id__isnull=False)
    contests = [load_contest(contest, users) for contest in contests]
    contests = [contest for contest in contests if contest is not None]

    return [users_data, contests]
