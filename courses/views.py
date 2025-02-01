import csv
import datetime
import json
import os
import re
import random
from time import sleep

import pytz
from django.contrib.auth import logout, authenticate, login
from django.core import mail
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from transliterate import translit

from algocode.settings import EJUDGE_CONTROL, JUDGES_DIR, EJUDGE_URL, EJUDGE_AUTH, DEFAULT_MAIN, DEFAULT_COURSE, \
    DEFAULT_PAGE
from courses.judges.common_verdicts import EJUDGE_OK
from courses.judges.pole_chudes import recalc_pole_chudes_standings
from courses.lib.form.table import get_form_columns, get_form_entry_row
from courses.lib.standings.standings_data import get_standings_data
from courses.lib.participants_group.participants_group import get_participants_group
from courses.models import Course, Main, Standings, Page, Contest, BlitzProblem, BlitzProblemStart, EjudgeRegisterApi, \
    Participant, Battleship, FormBuilder, FormField, FormEntry, PoleChudesTeam, PoleChudesGuess, PoleChudesGame, \
    BattleshipShip, ParticipantsGroup
from courses.judges.judges import load_contest

from django.views import View

from ejudge_registration.ejudge_api_registration import EjudgeApiSession

from ipware import get_client_ip


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
    def get(self, request, course_label=DEFAULT_COURSE):
        try:
            course = Course.objects.get(label=course_label)
        except:
            if course_label == "director" or random.randrange(2) == 0:
                return redirect("https://youtu.be/PkFGBIZWe-8")
            return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        contests_list = course.contests.order_by('-date', '-id')
        links = course.links.filter(hidden=False).order_by("priority")
        contests = []

        for contest in contests_list:
            if contest.enable_start_time and contest.start_time is not None:
                print(datetime.datetime.now(tz=pytz.UTC), contest.start_time, datetime.datetime.now(tz=pytz.UTC) - contest.start_time)
                if datetime.datetime.now(tz=pytz.UTC) < contest.start_time:
                    continue
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

        users_data, contests = get_standings_data(standings)

        return JsonResponse({
            'users': users_data,
            'contests': contests,
        })


class ParticipantsGroupView(View):
    def get(self, request, group_id: int):
        group = get_object_or_404(ParticipantsGroup, id=group_id)
        return JsonResponse(get_participants_group(group))


class PageView(View):
    def get(self, request, page_label=DEFAULT_PAGE):
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
            return HttpResponseBadRequest("Not admin")
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
            return HttpResponseBadRequest("Not admin")
        else:
            os.system(EJUDGE_CONTROL.format('stop'))
            sleep(15)
            os.system(EJUDGE_CONTROL.format('start'))
            return HttpResponse("Restarted ejudge")


class CreateValuer(View):
    @method_decorator(csrf_protect)
    def post(self, request):
        if not request.user.is_superuser:
            return HttpResponseBadRequest("Not admin")
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


def register_user(ejudge_register_api: EjudgeRegisterApi, name: str, cf_login=None):
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
        if cf_login is None:
            Participant.objects.create(
                name=group_name,
                group=group.group,
                course=group.group.course,
                ejudge_id=user["user_id"],
                pcms_login=user["login"],
            )
        else:
            Participant.objects.create(
                name=group_name,
                group=group.group,
                course=group.group.course,
                ejudge_id=user["user_id"],
                codeforces_handle=cf_login
            )
    return user


@method_decorator(csrf_exempt, name='dispatch')
class EjudgeRegister(View):
    def post(self, request):
        register_id = request.POST.get('register_id')
        secret = request.POST.get('secret')
        ejudge_register_api = get_object_or_404(EjudgeRegisterApi, id=register_id)
        if secret != ejudge_register_api.secret:
            return HttpResponseBadRequest("Wrong secret")
        name = request.POST.get('name')
        user = register_user(ejudge_register_api, name)
        return JsonResponse(user)


class BattleshipView(View):
    def get(self, request, battleship_id):
        battleship = get_object_or_404(Battleship, id=battleship_id)

        if not battleship.public:
            return HttpResponseBadRequest("Battleship is not public")

        teams = battleship.battleship_teams.all().order_by("id")
        participants = []
        for team in teams:
            participants.extend(team.participants.all())
        users = []
        for participant in participants:
            users.append(participant.participant)
        standings = load_contest(battleship.contest, users, required_users=users)
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
            fields[i]["score"] = 0
            for j, user in enumerate(team.participants.order_by("order", "id")):
                row = fields[i]['field'][j]
                row['name'] = user.participant.name
                row['problems'] = [0] * len(problem_names)
                row['submits'] = 0
                for p, res in enumerate(standings['users'][user.participant.id]):
                    row['submits'] += res['penalty']
                    fields[i]['fail'] += res['penalty']
                    if res['verdict'] == EJUDGE_OK:
                        row['problems'][p] = 1
                        fields[i]['success'] += 1
                        fields[i]['score'] += 1
                    elif res['penalty'] > 0:
                        row['problems'][p] = -1
            for ship in team.ships.all():
                if fields[i]['field'][ship.y]['problems'][ship.x] == 1:
                    fields[i]['field'][ship.y]['problems'][ship.x] = 2
                    fields[i]['ship_success'] += 1
                    fields[i]['score'] += 3
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


class BattleshipAdminView(View):
    def get(self, request, battleship_id):
        if not request.user.is_staff:
            return HttpResponseBadRequest("User is not admin")

        battleship = get_object_or_404(Battleship, id=battleship_id)
        teams = battleship.battleship_teams.all().order_by("id")

        participants = []
        for team in teams:
            participants.extend(team.participants.all())
        users = []
        for participant in participants:
            users.append(participant.participant)
        problem_names = []
        if battleship.problems > 0:
            for i in range(battleship.problems):
                problem_names.append({
                    'id': i + 1,
                    'long': chr(i + ord('A')),
                    'short': chr(i + ord('A')),
                    'index': 0,
                })
        else:
            standings = load_contest(battleship.contest, users, required_users=users)
            problem_names = standings["problems"]

        fields = [
            {
                'name': '',
                'field': [
                    dict()
                    for i in range(len(teams[j].participants.all()))
                ],
                'id': j,
            }
            for j in range(len(teams))
        ]

        for i in range(len(teams)):
            team = teams[i]
            fields[i]["name"] = team.name
            fields[i]["id"] = i
            for j, user in enumerate(team.participants.order_by("order", "id")):
                row = fields[i]['field'][j]
                row['name'] = user.participant.name
                row['problems'] = [[l, j, i, 0] for l in range(len(problem_names))]

            for ship in team.ships.all():
                fields[i]['field'][ship.y]['problems'][ship.x][3] = 1

        return render(
            request,
            'battleship_admin.html',
            {
                'battleship': battleship,
                'fields': fields,
                'problem_names': problem_names,
            }
        )

    @method_decorator(csrf_protect)
    def post(self, request, battleship_id):
        if not request.user.is_staff:
            return HttpResponseBadRequest("User is not admin")

        battleship = get_object_or_404(Battleship, id=battleship_id)
        teams = battleship.battleship_teams.all().order_by("id")
        team_id = int(request.POST.get("team_id"))

        existing = dict()
        t = teams[team_id]
        for ship in t.ships.all():
            existing["ship {} {} {}".format(ship.x, ship.y, team_id)] = ship

        for cell in request.POST:
            if cell.startswith("ship"):
                x, y, team = [int(i) for i in cell.split()[1:]]
                if cell not in existing:
                    BattleshipShip(
                        battleship=battleship,
                        team=teams[team],
                        x=x,
                        y=y,
                    ).save()

        for cell in existing:
            if cell not in request.POST:
                existing[cell].delete()

        return redirect(reverse('battleship_admin', kwargs={'battleship_id': battleship_id}))

class FormView(View):
    def get(self, request, form_label):
        form = get_object_or_404(FormBuilder, label=form_label)

        fields = []

        for field in form.fields.order_by("id"):
            f = {
                'id': field.id,
                'label': field.label,
                'type': field.type,
                'required': field.required,
                'internal_name': field.internal_name,
                'description': field.description,
            }
            f.update(field.TYPES_DICT)
            if field.type == FormField.SELECT:
                f['options'] = field.select_options.order_by("id")
            fields.append(f)

        print(fields)

        return render(
            request,
            'form.html',
            {
                'form': form,
                'fields': fields,
            }
        )

    @method_decorator(csrf_protect)
    def post(self, request, form_label):
        form = get_object_or_404(FormBuilder, label=form_label)
        fields = form.fields.order_by("id")
        result = dict()

        user_mail = ''
        user_ip, is_routable = get_client_ip(request)

        if form.requests_per_day_limit is not None and \
                form.requests_per_day_limit > 0 and \
                user_ip not in form.ip_whitelist.split():
            day_ago = datetime.datetime.now() - datetime.timedelta(days=1)
            entries = len(form.entries.filter(ip=user_ip, time__gte=day_ago))
            if entries >= form.requests_per_day_limit:
                return HttpResponse("Превышенно максимальное число запросов")

        for field in fields:
            if field.type in [FormField.STR, FormField.MAIL, FormField.PHONE, FormField.LONG, FormField.DATE, FormField.SELECT]:
                result[field.internal_name] = request.POST.get(field.internal_name, '')
                if field.type == FormField.MAIL:
                    user_mail = request.POST.get(field.internal_name, '')

            if field.type == FormField.INTEGER:
                result[field.internal_name] = int(request.POST.get(field.internal_name, 0))

            if field.type == FormField.CHECKBOX:
                result[field.internal_name] = field.internal_name in request.POST

        if len(form.register_api.all()) > 0:
            name = form.register_name_template.format(**result)
            ejudge_register_api = form.register_api.all()[0]
            if "cf_login" in result:
                user_login = register_user(ejudge_register_api, name, result["cf_login"])
            else:
                user_login = register_user(ejudge_register_api, name)
            result["ejudge_login"] = user_login["login"]
            result["ejudge_password"] = user_login["password"]
            result["ejudge_id"] = user_login["user_id"]

        entry = FormEntry.objects.create(form=form, data=json.dumps(result), mail=user_mail, ip=user_ip)
        entry.save()

        if form.send_mail and form.mail_auth:
            auth = form.mail_auth

            with mail.get_connection(
                    host=auth.mail_host,
                    port=auth.mail_port,
                    username=auth.mail_username,
                    password=auth.mail_password,
                    use_tls=auth.mail_use_tls,
                    use_ssl=auth.mail_use_ssl
            ) as connection:
                mail.EmailMessage(
                    form.mail_topic,
                    form.mail_template.format(**result),
                    auth.mail_username,
                    [user_mail],
                    connection=connection
                ).send()

        return HttpResponse(form.response_text.format(**result))


class FormDataView(View):
    def get(self, request):
        user = request.user
        if not user.is_superuser:
            return HttpResponseBadRequest("Not admin")
        forms = FormBuilder.objects.order_by("-id")
        res = []
        for form in forms:
            res.append(dict())
            res[-1]["form"] = form
            res[-1]["entries"] = len(form.entries.all())
            if len(form.exports.all()) > 0:
                res[-1]["gdoc"] = ["https://docs.google.com/spreadsheets/d/" + export.sheet_id for export in form.exports.all()]

        return render(
            request,
            'form_data.html',
            {
                "forms": res
            }
        )


class FormJsonExport(View):
    def get(self, request, form_label):
        user = request.user
        if not user.is_superuser:
            return HttpResponseBadRequest("Not admin")

        form = get_object_or_404(FormBuilder, label=form_label)

        entries = form.entries.order_by("id")

        result = []
        for entry in entries:
            entry_dict = json.loads(entry.data)
            entry_dict["ip"] = entry.ip
            entry_dict["time"] = entry.time.isoformat()
            result.append(entry_dict)

        return JsonResponse(result, safe=False)


class FormCSVExport(View):
    def get(self, request, form_label):
        user = request.user
        if not user.is_superuser:
            return HttpResponseBadRequest("Not admin")

        form = get_object_or_404(FormBuilder, label=form_label)

        response = HttpResponse(
            content_type='text/csv',
        )

        response['Content-Disposition'] = 'attachment; filename="{label}.csv"'.format(label=form.label)
        writer = csv.writer(response)

        columns, column_names = get_form_columns(form)

        writer.writerow(columns)

        entries = form.entries.order_by("id")

        for entry in entries:
            writer.writerow(get_form_entry_row(entry, column_names))

        return response


class PoleChudesTeamsView(View):
    def get(self, request, game_id):
        game = get_object_or_404(PoleChudesGame, id=game_id)

        recalc_pole_chudes_standings(game)

        teams = list(game.teams.order_by("-score", "-problems", "id"))

        return render(
            request,
            'pole_chudes_teams.html',
            {
                'teams': teams,
                'game': game,
            }
        )


class PoleChudesTeamView(View):
    def get(self, request, team_id):
        team = get_object_or_404(PoleChudesTeam, id=team_id)

        if not team.game.finished:
            if request.user.is_anonymous:
                return redirect(reverse('login'))

            if not request.user.is_staff:
                if team.user is None:
                    return HttpResponseBadRequest("Wrong login")
                if team.user != request.user:
                    return HttpResponseBadRequest("Wrong login")

        recalc_pole_chudes_standings(team.game)

        team = get_object_or_404(PoleChudesTeam, id=team_id)

        standings = []

        participants = []

        for participant in team.participants.order_by("id"):
            participants.append(participant.participant)

        contest = load_contest(team.game.contest, participants, required_users=participants)
        prob_letters = ["" for i in range(len(team.game.alphabet))]

        for i in range(len(contest["problems"])):
            if i < len(prob_letters):
                prob_letters[i] = contest["problems"][i]["short"]

        for participant in team.participants.order_by("id"):
            row = dict()
            row["name"] = participant.participant.name
            row["problems"] = [
                {
                    'penalty': 0,
                    'verdict': None,
                } for i in range(len(team.game.alphabet))
            ]

            if participant.participant.id in contest['users']:
                for p, res in enumerate(contest['users'][participant.participant.id]):
                    if p >= len(row["problems"]):
                        continue
                    if res["verdict"] == EJUDGE_OK:
                        res["show"] = '+'
                        if res["penalty"] > 1:
                            res["show"] = '+{}'.format(res["penalty"])
                    elif res["verdict"] is not None:
                        res["show"] = '-{}'.format(res["penalty"])
                    row["problems"][p] = res

            standings.append(row)

        alphabet_to_index = {team.game.alphabet[i]: i for i in range(len(team.game.alphabet))}
        words = []

        for wid, word_model in enumerate(list(team.game.words.order_by("id"))):
            word = dict()
            word["hint"] = word_model.hint
            word["id"] = wid + 1
            word["word"] = [
                {
                    "state": "not guessed",
                    "letter": i,
                } for i in word_model.text
            ]
            word["alphabet"] = [
                {
                    "state": "unknown",
                    "letter": i,
                } for i in team.game.alphabet
            ]
            word["unsuccess"] = []

            for letter in list(team.letters.filter(word_id=wid).all()):
                j = alphabet_to_index[letter.letter.upper()]
                guessed_let = False
                for i, a in enumerate(word_model.text):
                    if a == letter.letter:
                        guessed_let = True
                        word["word"][i]["state"] = "guessed"
                if guessed_let:
                    word["alphabet"][j]["state"] = "yes"
                else:
                    word["alphabet"][j]["state"] = "no"

            guess_word = False

            for guess in list(team.guesses.filter(word_id=wid).order_by("id")):
                if guess.guessed:
                    for i in range(len(word_model.text)):
                        if word["word"][i]["state"] != "guessed":
                            word["word"][i]["state"] = "shown"
                    guess_word = True
                    break
                else:
                    word["unsuccess"].append(guess.guess)

            word["guessed"] = guess_word

            words.append(word)

            if not guess_word:
                break

        words.reverse()

        return render(
            request,
            'pole_chudes_team.html',
            {
                'team': team,
                'standings': standings,
                'prob_letters': prob_letters,
                'words': words,
            }
        )


class PoleChudesGuessView(View):
    @method_decorator(csrf_protect)
    def post(self, request, team_id):
        team = get_object_or_404(PoleChudesTeam, id=team_id)

        if team.game.finished:
            return HttpResponseBadRequest("game finished")

        if request.user.is_anonymous:
            return redirect(reverse('login'))

        if not request.user.is_staff:
            if team.user is None:
                return HttpResponseBadRequest("Wrong login")
            if team.user != request.user:
                return HttpResponseBadRequest("Wrong login")

        word = str(request.POST.get("word", "")).upper()

        curr_word = list(team.game.words.order_by("id"))[team.word_id].text

        if len(word) != len(curr_word):
            return HttpResponse("Вы предложили слово {}, оно не совпадает по длине с загаданным словом".format(word))

        guessed = (word == curr_word)

        guess = PoleChudesGuess.objects.create(
            team=team,
            word_id=team.word_id,
            guess=word,
            guessed=guessed,
            score=team.game.guess_bonus if guessed else -team.game.miss_penalty,
        )

        guess.save()

        return redirect(reverse("pole_chudes_team", kwargs={"team_id": team_id}))