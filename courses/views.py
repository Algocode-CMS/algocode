import datetime
import os
import re
from time import sleep

from django.contrib.auth import logout, authenticate, login
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from transliterate import translit

from algocode.settings import EJUDGE_CONTROL, JUDGES_DIR, EJUDGE_URL, EJUDGE_AUTH, DEFAULT_MAIN
from courses.judges.common_verdicts import EJUDGE_OK
from courses.models import Course, Main, Standings, Page, Contest, BlitzProblem, BlitzProblemStart, EjudgeRegisterApi, \
    Participant, Battleship
from courses.judges.judges import load_contest

from django.views import View

from ejudge_registration.ejudge_api_registration import EjudgeApiSession


class MainView(View):
    def get(self, request, main_id=DEFAULT_MAIN):
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
                'teachers': course.teachers.order_by("priority")
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

        contests = standings.contests.order_by('-date', '-id').filter(contest_id__isnull=False)
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
        int_login = True
        if ejudge_register_api.use_surname:
            surname = translit(name.split()[0], 'ru', reversed=True)
            surname = re.sub(r'\W+', '', surname).lower()
            login = f'{login}{surname}'
            int_login = False
        user = api_session.create_user_and_add_contests(login, name, int_login, contests)
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


class BattleshipView(View):
    def get(self, request, battleship_id):
        battleship = get_object_or_404(Battleship, id=battleship_id)
        teams = battleship.battleship_teams.all()
        users = []
        for team in teams:
            users.extend(team.participants.all())
        standings = load_contest(battleship.contest, users)
        problem_names = standings["problems"]

        fields = [
            {
                'name': '',
                'field': [
                    dict()
                    for i in range(len(teams[j].participants.all()))
                ],
                'success': 0,
                'fail': 0,
                'ship_success': 0,
                'ship_fail': 0,
            }
            for j in range(len(teams))
        ]

        for i in range(len(teams)):
            team = teams[i]
            fields[i]["name"] = team.name
            for j, user in enumerate(team.participants.order_by("id")):
                row = fields[i]['field'][j]
                row['name'] = user.name
                row['problems'] = [0] * len(problem_names)
                row['submits'] = 0
                for p, res in enumerate(standings['users'][user.id]):
                    row['submits'] += res['penalty']
                    fields[i]['fail'] += res['penalty']
                    if res['verdict'] == EJUDGE_OK:
                        row['problems'][p] = 1
                        fields[i]['success'] += 1
            for ship in team.ships.all():
                if fields[i]['field'][ship.x]['problems'][ship.y] == 1:
                    fields[i]['field'][ship.x]['problems'][ship.y] = 2
                    fields[i]['ship_success'] += 1
            fields[i]['ship_fail'] = fields[i]['success'] - fields[i]['ship_success']

        return render(
            request,
            'battleship.html',
            {
                'name': battleship.name,
                'fields': fields,
                'problem_names': problem_names,
            }
        )
        #
        #
        #
        #
        # battleship = get_object_or_404(Battleship, id=battleship_id)
        # course = get_object_or_404(Course, id=course_id)
        # contest_id = battleship.contest
        # contest_id += 1000000
        # contest_id = str(contest_id)[1:]
        # data = untangle.parse(os.path.join(JUDGES_DIR, contest_id, 'var/status/dir/external.xml'))
        # all_users = dict()
        # teams = battleship.teams.all()
        # problem_names = []
        # for problem in data.runlog.problems.children:
        #     problem_names.append(dict())
        #     problem_names[-1]['id'] = problem['id']
        #     problem_names[-1]['long'] = problem['long_name']
        #     problem_names[-1]['short'] = problem['short_name']
        # for user in data.runlog.users.children:
        #     if len(user['name']) > 0:
        #         all_users[int(user['id'])] = dict()
        #         all_users[int(user['id'])]['name'] = user['name']
        #         all_users[int(user['id'])]['problems'] = [0] * len(problem_names)
        #         all_users[int(user['id'])]['submits'] = 0
        # for run in data.runlog.runs.children:
        #     user_id = int(run['user_id'])
        #     problem = int(run['prob_id']) - 1
        #     if run['status'] == 'OK':
        #         all_users[user_id]['problems'][problem] = 1
        #     elif all_users[user_id]['problems'][problem] != 1:
        #         all_users[user_id]['submits'] += 1
        #         all_users[user_id]['problems'][problem] = -1
        #
        # fields = [
        #     {
        #         'name': '',
        #         'field': [
        #             dict()
        #             for i in range(len(teams[j].ids.all()))
        #         ],
        #         'success': 0,
        #         'fail': 0,
        #         'ship_success': 0,
        #         'ship_fail': 0,
        #     }
        #     for j in range(len(teams))
        # ]
        # for i in range(len(teams)):
        #     j = 0
        #     fields[i]['name'] = teams[i].name
        #     for user_id in teams[i].ids.all():
        #         user_id = user_id.user
        #         fields[i]['field'][j] = all_users[user_id]
        #         for score in fields[i]['field'][j]['problems']:
        #             if score > 0:
        #                 fields[i]['success'] += score
        #         fields[i]['fail'] += all_users[user_id]['submits']
        #         j += 1
        #     for ship in teams[i].ships.all():
        #         if fields[i]['field'][ship.x]['problems'][ship.y] == 1:
        #             fields[i]['field'][ship.x]['problems'][ship.y] = 2
        #             fields[i]['ship_success'] += 1
        #     fields[i]['ship_fail'] = fields[i]['success'] - fields[i]['ship_success']
        # return render(
        #     request,
        #     'battleship.html',
        #     {
        #         'name': battleship.name,
        #         'fields': fields,
        #         'problem_names': problem_names,
        #     }
        # )