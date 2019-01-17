from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse

from courses.models import Course, Main, Standings, Page
from courses.judges.judges import load_contest

from django.views import View


class MainView(View):
    def get(self, request, main_id=1):
        main = get_object_or_404(Main, id=main_id)
        courses_list = main.courses.order_by("id")
        links = main.links.filter(hidden=False)
        return render(
            request,
            'main.html',
            {
                'main': main,
                'courses': courses_list,
                'links': links,
            }
        )


class CourseView(View):
    def get(self, request, course_label):
        course = get_object_or_404(Course, label=course_label)
        contests_list = course.contests.order_by('-date', '-id')
        links = course.links.filter(hidden=False)
        contests = []

        for contest in contests_list:
            contests.append({
                'contest': contest,
                'links': contest.links.order_by('id'),
            })

        return render(
            request,
            course.template,
            {
                'course': course,
                'contests': contests,
                'links': links,
                'ejudge_url': course.ejudge_url,
                'teachers': course.teachers.all()
            }
        )


class StandingsView(View):
    def get(self, request, standings_id, contest_id=-1):
        standings = get_object_or_404(Standings, id=standings_id)
        return render(
            request,
            'standings.html',
            {
                'standings': standings,
                'contest_id': contest_id,
            }
        )


class StandingsDataView(View):
    def get(self, request, standings_id):
        standings = get_object_or_404(Standings, id=standings_id)

        users = []
        for group in standings.groups.all():
            users.extend(group.participants.all())

        users_data = []
        added_users = set()
        for group in standings.groups.all():
            for user in group.participants.all():
                if user.id in added_users:
                    continue
                added_users.add(user.id)
                users_data.append({
                    'id': user.id,
                    'name': user.name,
                    'group': group.name,
                    'group_short': group.short_name,
                })

        contests = standings.contests.order_by('-date', '-id').all()
        contests = [load_contest(contest, users) for contest in contests]
        contests = [contest for contest in contests if contest is not None]

        return JsonResponse({
            'users': users_data,
            'contests': contests,
        })


class PageView(View):
    def get(self, request, page_label):
        page = get_object_or_404(Page, label=page_label)
        return render(
            request,
            'page.html',
            {
                'page': page,
            }
        )
