import os

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

from algocode.settings import EJUDGE_CONTROL, JUDGES_DIR
from courses.models import Course, Main, Standings, Page
from courses.judges.judges import load_contest

from django.views import View


class MainView(View):
    def get(self, request, main_id=3):
        main = get_object_or_404(Main, id=main_id)
        courses_list = main.courses.order_by("id")
        links = main.links.filter(hidden=False).order_by("priority")
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
        links = course.links.filter(hidden=False).order_by("priority")
        contests = []

        for contest in contests_list:
            contests.append({
                'contest': contest,
                'links': contest.links.order_by('id').order_by("priority"),
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
        if page.is_raw:
            return HttpResponse(page.content)
        return render(
            request,
            'page.html',
            {
                'page': page,
            }
        )


class ServeControl(View):
    def get(self, request):
        user = request.user
        if not user.is_superuser:
            return HttpResponseBadRequest
        else:
            return render(
                request,
                'serve_control.html',
                {},
            )


class RestartEjudge(View):
    @method_decorator(csrf_protect)
    def post(self, request):
        if not request.user.is_superuser:
            return HttpResponseBadRequest
        else:
            print(EJUDGE_CONTROL.format('stop'))
            os.system(EJUDGE_CONTROL.format('stop') + '>/Users/philipgribov/Downloads/ejudge_restart 2>&1')
            os.system(EJUDGE_CONTROL.format('start'))
            return HttpResponse("Restarted ejudge")


class CreateValuer(View):
    @method_decorator(csrf_protect)
    def post(self, request):
        if not request.user.is_superuser:
            return HttpResponseBadRequest
        else:
            contest_id = int(request.POST.get('contest_id'))
            valuer_output_location = os.path.join(JUDGES_DIR, 'valuer_output')
            os.system('(cd {} && {} {:06d} >{} 2>&1)'.format(JUDGES_DIR, os.path.join(JUDGES_DIR, 'valuer.py'), contest_id, valuer_output_location))
            valuer_output = open(valuer_output_location, 'r').read()
            return HttpResponse(valuer_output, content_type="text/plain")


# TODO Battleship
