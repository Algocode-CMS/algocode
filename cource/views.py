import os
import math
import random

import untangle
from django.http import HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.datastructures import MultiValueDict
from django.utils.http import urlencode

from cource.models import Course, Battleship, Main, Contest
from cource.templates import *

# Create your views here.
from django.views import View
from algocode.settings import JUDGES_DIR


def users_cmp(a):
    return (-a['score'], a['penalty'])


def contest_cmp(a):
    contest = get_object_or_404(Contest, ejudge_id=a)
    return contest.id


class MainView(View):
    def get(self, request, main_id):
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
    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        contests_list = course.contests.order_by("-id")
        left_links = course.links.filter(hidden=False)
        contests = []
        standings_links = []
        standings_link_beginning = reverse("standings", args=[course_id])
        if course.proxy_pass_links:
            standings_link_beginning = "/standings/"
        standings_link_beginning = standings_link_beginning + '?'
        for contest_type in course.contest_types.order_by("id"):
            if contest_type.show_standings_left_link:
                standings_link = standings_link_beginning
                for contest in contest_type.contests.order_by("-id"):
                    if contest.show_in_standings:
                        standings_link = standings_link + '&contest_id=' + str(contest.ejudge_id)
                standings_links.append(dict())
                standings_links[-1]['name'] = contest_type.standings_name
                standings_links[-1]['link'] = standings_link

        for contest in contests_list:
            contests.append(dict())
            contests[-1]['contest'] = contest
            contests[-1]['links'] = contest.links.order_by("id")


        return render(
            request,
            'index.html',
            {
                'course': course,
                'contests': contests,
                'links': left_links,
                'standings_links': standings_links,
                'ejudge_url': course.ejudge_url,
            }
        )


marks = [0] * 100

data_for_marks = [0] * 100


class StandingsView(View):
    def get(self, request, course_id):
        global marks, data_for_marks
        course = get_object_or_404(Course, id=course_id)
        contests_ids_str = request.GET.getlist('contest_id')
        contests_ids = []
        contest_type = None
        for contest_id in contests_ids_str:
            contest_id = int(contest_id)
            try:
                contest = course.contests.get(ejudge_id=contest_id)
                if contest.show_in_standings and contest.type.allow_standings and contest.ejudge_id != 0 and (contest_type == None or contest_type == contest.type):
                    contests_ids.append(contest_id)
                    contest_type = contest.type
            except:
                pass
        olymp = 0
        if contest_type is not None:
            olymp = contest_type.olymp
        contests_ids.sort(reverse=True)
        contests = []
        userind = dict()
        users = []
        contest_index = 0
        for contest_id in contests_ids:
            contest_id = int(contest_id)
            contest_id += 1000000
            contest_id = str(contest_id)[1:]
            data = untangle.parse(os.path.join(JUDGES_DIR, contest_id, 'var/status/dir/external.xml'))
            contests.append(dict())
            contest_users_start = dict()
            for user in data.runlog.users.children:
                contest_users_start[user['id']] = 0
                if (user['id'] not in userind) and len(user['name']) > 0 and user['name'][0] != 'X':
                    userind[user['id']] = len(users)
                    users.append(dict())
                    users[-1]['name'] = user['name']
            contests[-1]['problems'] = []
            problem_index = 0
            for problem in data.runlog.problems.children:
                contests[-1]['problems'].append(dict())
                contests[-1]['problems'][-1]['id'] = problem['id']
                contests[-1]['problems'][-1]['long'] = problem['long_name']
                contests[-1]['problems'][-1]['short'] = problem['short_name']
                contests[-1]['problems'][-1]['index'] = problem_index
                problem_index += 1
            contests[-1]['runs'] = []
            contest = course.contests.get(ejudge_id=int(contest_id))
            for run in data.runlog.runs.children:
                if run['status'] == 'VS':
                    contest_users_start[run['user_id']] = int(run['time'])
                    continue
                if run['status'] == 'VT' or (run['user_id'] not in userind) or (int(run['time']) > contest_users_start[run['user_id']] + contest.duration * 60 * 60):
                    continue
                contests[-1]['runs'].append(dict())
                contests[-1]['runs'][-1]['user'] = run['user_id']
                contests[-1]['runs'][-1]['problem'] = int(run['prob_id']) - 1
                contests[-1]['runs'][-1]['time'] = int(run['time'])
                if run['status'] == 'OK':
                    contests[-1]['runs'][-1]['status'] = 1
                else:
                    contests[-1]['runs'][-1]['status'] = 0
                if olymp and run['status'] in "OKPT":
                    contests[-1]['runs'][-1]['status'] = int(run['score'])
            contests[-1]['name'] = course.contests.get(ejudge_id=contest_id).title
            contests[-1]['index'] = contest_index
            contests[-1]['len'] = len(contests[-1]['problems']) + 2 - olymp
            contests[-1]['id'] = contest_id
            contests[-1]['coefficient'] = contest.coefficient
            if int(contest.coefficient) == contest.coefficient:
                contests[-1]['coefficient'] = int(contest.coefficient)
            contest_index += 1
        for i in range(len(users)):
            users[i]['score'] = 0
            users[i]['penalty'] = 0
            users[i]['mark'] = 0
            users[i]['contest_score'] = [0] * contest_index
            users[i]['contest_penalty'] = [0] * contest_index
            users[i]['problem_score'] = [[] for i in range(contest_index)]
            users[i]['problem_penalty'] = [[] for i in range(contest_index)]
            users[i]['contest_mark'] = [0] * contest_index
            users[i]['index'] = i
        coefficient = 0
        random_mark_key = random.randrange(100)
        marks[random_mark_key] = 0
        data_for_marks[random_mark_key] = 0
        for contest in contests:
            contest_ind = contest['index']
            contest_model = course.contests.get(ejudge_id=int(contest['id']))
            coefficient += contest_model.coefficient
            for i in range(len(users)):
                for j in range(len(contest['problems'])):
                    users[i]['problem_score'][contest_ind].append(0)
                    users[i]['problem_penalty'][contest_ind].append(0)
            for run in contest['runs']:
                i = userind[run['user']]
                problem = run['problem']
                if run['status']:
                    users[i]['problem_score'][contest_ind][problem] = max(users[i]['problem_score'][contest_ind][problem], run['status'])
                elif users[i]['problem_score'][contest_ind][problem] == 0:
                    users[i]['problem_penalty'][contest_ind][problem] += 1
            max_reached_score = 0
            num_of_solves_for_problem = [0] * len(contest['problems'])
            for i in range(len(users)):
                for j in range(len(contest['problems'])):
                    if users[i]['problem_score'][contest_ind][j] != 0:
                        num_of_solves_for_problem[j] += 1
                        users[i]['penalty'] += users[i]['problem_penalty'][contest_ind][j]
                        users[i]['contest_penalty'][contest_ind] += users[i]['problem_penalty'][contest_ind][j]
                        users[i]['score'] += users[i]['problem_score'][contest_ind][j]
                        users[i]['contest_score'][contest_ind] += users[i]['problem_score'][contest_ind][j]
                max_reached_score = max(users[i]['contest_score'][contest_ind], max_reached_score)
            if contest_model.type.enable_marks:
                max_possible_score = len(contest['problems'])
                if olymp:
                    max_possible_score *= contest_model.type.max_score_for_olymp_problem
                for i in range(len(users)):
                    problem_score = users[i]['problem_score'][contest_ind]
                    user_id = users[i]['index']
                    user_score = users[i]['contest_score'][contest_ind]
                    num_of_problems = len(contest['problems'])
                    marks[random_mark_key] = 0
                    try:
                        exec(
                            contest_model.type.exec_for_marks,
                            {
                                'user_score': user_score,
                                'max_possible_score': max_possible_score,
                                'max_reached_score': max_reached_score,
                                'num_of_problems': num_of_problems,
                                'user_id': user_id,
                                'problem_score': problem_score,
                                'num_of_solves_for_problem': num_of_solves_for_problem,
                                'users_list': users,
                                'marks': marks,
                                'mark_key': random_mark_key,
                                'data': data_for_marks,
                            },
                        )
                    except:
                        pass
                    try:
                        exec(
                            contest_model.exec_for_marks,
                            {
                                'user_score': user_score,
                                'max_possible_score': max_possible_score,
                                'max_reached_score': max_reached_score,
                                'num_of_problems': num_of_problems,
                                'user_id': user_id,
                                'problem_score': problem_score,
                                'num_of_solves_for_problem': num_of_solves_for_problem,
                                'users_list': users,
                                'marks': marks,
                                'mark_key': random_mark_key,
                                'data': data_for_marks,
                            },
                        )
                    except:
                        pass
                    users[i]['contest_mark'][contest_ind] = round(marks[random_mark_key], 2)
                    users[i]['mark'] += users[i]['contest_mark'][contest_ind] * contest_model.coefficient
        users.sort(key=users_cmp)
        for i in range(len(users)):
            users[i]['index'] = i
            if coefficient != 0:
                users[i]['mark'] /= coefficient
            users[i]['mark'] = round(users[i]['mark'], 2)

        return render(
            request,
            'standings.html',
            {
                'contests': contests,
                'users': users,
                'olymp': not olymp,
                'course': course,
                'enable_marks': contest_type.enable_marks,
            }
        )


class BattleshipView(View):
    def get(self, request, course_id, battleship_id):
        battleship = get_object_or_404(Battleship, id=battleship_id)
        course = get_object_or_404(Course, id=course_id)
        contest_id = battleship.contest
        contest_id += 1000000
        contest_id = str(contest_id)[1:]
        data = untangle.parse(os.path.join(JUDGES_DIR, contest_id, 'var/status/dir/external.xml'))
        all_users = dict()
        teams = battleship.teams.all()
        problem_names = []
        for problem in data.runlog.problems.children:
            problem_names.append(dict())
            problem_names[-1]['id'] = problem['id']
            problem_names[-1]['long'] = problem['long_name']
            problem_names[-1]['short'] = problem['short_name']
        for user in data.runlog.users.children:
            if len(user['name']) > 0:
                all_users[int(user['id'])] = dict()
                all_users[int(user['id'])]['name'] = user['name']
                all_users[int(user['id'])]['problems'] = [0] * len(problem_names)
                all_users[int(user['id'])]['submits'] = 0
        for run in data.runlog.runs.children:
            user_id = int(run['user_id'])
            problem = int(run['prob_id']) - 1
            if run['status'] == 'OK':
                all_users[user_id]['problems'][problem] = 1
            elif all_users[user_id]['problems'][problem] != 1:
                all_users[user_id]['submits'] += 1
                all_users[user_id]['problems'][problem] = -1

        fields = [
            {
                'name': '',
                'field': [
                    dict()
                    for i in range(len(teams[j].ids.all()))
                ],
                'success': 0,
                'fail': 0,
                'ship_success': 0,
                'ship_fail': 0,
            }
            for j in range(len(teams))
        ]
        for i in range(len(teams)):
            j = 0
            fields[i]['name'] = teams[i].name
            for user_id in teams[i].ids.all():
                user_id = user_id.user
                fields[i]['field'][j] = all_users[user_id]
                for score in fields[i]['field'][j]['problems']:
                    if score > 0:
                        fields[i]['success'] += score
                fields[i]['fail'] += all_users[user_id]['submits']
                j += 1
            for ship in teams[i].ships.all():
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