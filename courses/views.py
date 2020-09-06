import datetime
import os
from time import sleep

from django.contrib.auth import logout, authenticate, login
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, csrf_exempt

from algocode.settings import EJUDGE_CONTROL, JUDGES_DIR, EJUDGE_URL, EJUDGE_AUTH
from courses.models import Course, Main, Standings, Page, Contest, BlitzProblem, BlitzProblemStart, EjudgeRegisterApi, \
    Participant
from courses.judges.judges import load_contest

from django.views import View

from ejudge_registration.ejudge_api_registration import EjudgeApiSession


class MainView(View):
    def get(self, request, main_id=3):
        main = get_object_or_404(Main, id=main_id)
        courses_list = main.course_links.order_by("priority")
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
    def get(self, request, standings_label, contest_id=-1):
        standings = get_object_or_404(Standings, label=standings_label)
        return render(
            request,
            'standings.html',
            {
                'standings': standings,
                'contest_id': contest_id,
            }
        )


class StandingsDataView(View):
    def get(self, request, standings_label):
        standings = get_object_or_404(Standings, label=standings_label)

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
            os.system(EJUDGE_CONTROL.format('stop'))
            sleep(15)
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


class Login(View):
    def get(self, request):
        if request.user.is_authenticated:
            logout(request)
        return render(request, "login.html", {})

    def post(self, request):
        if request.user.is_anonymous:
            username = request.POST['login']
            password = request.POST['password']
            user_tst = authenticate(username=username, password=password)
            if user_tst is not None:
                login(request, user_tst)
                return redirect(reverse('main'))
            else:
                return redirect(reverse('login'))
        return redirect(reverse('main'))


class BlitzView(View):
    def get(self, request, contest_id):
        if request.user.is_anonymous:
            return redirect(reverse('login'))
        user_id = int(request.user.first_name)
        contest = get_object_or_404(Contest, id=contest_id)
        problems = []
        for problem in contest.blitz_problems.order_by('problem_id'):
            problems.append({})
            problems[-1]['problem'] = problem
            problems[-1]['starts_number'] = len(problem.starts.all())
            try:
                user_start = problem.starts.get(participant_id=user_id)
                problems[-1]['started'] = True
                curr_time = datetime.datetime.now(datetime.timezone.utc)
                problems[-1]['bid_time_left'] = datetime.timedelta(minutes=3).seconds - int((curr_time - user_start.time).total_seconds())
                problems[-1]['bid_left'] = max(0, user_start.bid - int((curr_time - user_start.time).total_seconds()) // 60)
                problems[-1]['bid'] = user_start.bid
            except:
                problems[-1]['started'] = False
        return render(
            request,
            "blitz.html",
            {
                "contest": contest,
                "problems": problems
            }
        )


class BlitzOpenProblem(View):
    @method_decorator(csrf_protect)
    def post(self, request, problem_id):
        if request.user.is_anonymous:
            return redirect(reverse('login'))
        user_id = int(request.user.first_name)
        problem = get_object_or_404(BlitzProblem, id=problem_id)
        if len(BlitzProblemStart.objects.filter(participant_id=user_id, problem=problem)) == 0:
            BlitzProblemStart.objects.create(problem=problem, participant_id=user_id)
        return redirect(reverse("blitz_view", kwargs={"contest_id": problem.contest.id}))


class BlitzMakeBid(View):
    @method_decorator(csrf_protect)
    def post(self, request, problem_id):
        if request.user.is_anonymous:
            return redirect(reverse('login'))
        user_id = int(request.user.first_name)
        problem = get_object_or_404(BlitzProblem, id=problem_id)
        start = get_object_or_404(BlitzProblemStart, participant_id=user_id, problem=problem)
        curr_time = datetime.datetime.now(datetime.timezone.utc)
        if datetime.timedelta(minutes=3).seconds > (curr_time - start.time).seconds:
            start.bid = int(request.POST.get("bid", 0))
            start.save()
        return redirect(reverse("blitz_view", kwargs={"contest_id": problem.contest.id}))


@method_decorator(csrf_exempt, name='dispatch')
class EjudgeRegister(View):
    def post(self, request):
        register_id = request.POST.get('register_id')
        secret = request.POST.get('secret')
        ejudge_register_api = get_object_or_404(EjudgeRegisterApi, id=register_id)
        if secret != ejudge_register_api.secret:
            return HttpResponseBadRequest()
        name = request.POST.get('name')
        contests = [contest.contest_id for contest in ejudge_register_api.contests.all()]
        login = ejudge_register_api.login
        api_session = EjudgeApiSession(EJUDGE_AUTH["login"], EJUDGE_AUTH["password"], EJUDGE_URL)
        user = api_session.create_user_and_add_contests(login, name, True, contests)
        for group in ejudge_register_api.groups.all():
            group_name = name
            if group.use_login:
                group_name = user["login"]
            Participant.objects.create(
                name=group_name,
                group=group.group,
                course=group.group.course,
                ejudge_id=user["user_id"]
            )
        return JsonResponse(user)


# TODO Battleship
