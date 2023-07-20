import time

from django.core.management.base import BaseCommand

from algocode import settings
from courses.lib.form.table import get_form_columns, get_form_entry_row
from courses.lib.standings.standings_data import get_standings_data
from courses.models import StandingsSheetExport, FormSheetsExport

from apiclient import discovery
from google.oauth2 import service_account

SHEETS_API_DELAY = 1
SHEETS_SCOPES = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/spreadsheets"]


class Command(BaseCommand):
    help = 'Loads data from codeforces'

    def handle(self, *args, **options):


        try:
            credentials = service_account.Credentials.from_service_account_info(settings.GOOGLE_SHEETS_CONFIG, scopes=SHEETS_SCOPES)
            service = discovery.build('sheets', 'v4', credentials=credentials)
        except Exception as e:
            print("Error while connecting to sheets api")
            print(e)
            return

        exports = StandingsSheetExport.objects.all()

        for export in exports:
            try:
                export_contest(export, service)
                print("Updated standings", export.id, export.name, export.standings.title, export.standings.label)
            except Exception as e:
                print("Error while updating", export.id, export.name, export.standings.title, export.standings.label)
                print(e)
            time.sleep(SHEETS_API_DELAY)

        forms_exports = FormSheetsExport.objects.filter(do_update=True)
        for export in forms_exports:
            try:
                export_form(export, service)
                print("Exported form", export.id, export.name, export.form.label, export.form.title)
            except Exception as e:
                print("Error while updations", export.id, export.name, export.form.label, export.form.title)
                print(e)
            time.sleep(SHEETS_API_DELAY)

        print('sheets synced!')


def export_form(export: FormSheetsExport, service):
    entries = list(export.form.entries.filter(id__gt=export.latest_id).order_by("id"))
    if len(entries) == 0:
        return

    columns, column_names = get_form_columns(export.form)

    column_id = get_column_id(len(columns))

    data = [dict(), dict()]
    data[0]["range"] = "{}!A1:{}1".format(
        export.tab,
        column_id,
    )
    data[0]["values"] = [columns]

    data[1]["range"] = "{}!A{}:{}{}".format(
        export.tab,
        export.latest_row + 1,
        column_id,
        export.latest_row + len(entries)
    )
    data[1]["values"] = [get_form_entry_row(entry, column_names) for entry in entries]

    xx = service.spreadsheets().values().batchUpdate(
        spreadsheetId=export.sheet_id,
        body={
            "valueInputOption": 'USER_ENTERED',
            "data": data,
        }
    ).execute()

    export.latest_row += len(entries)
    export.latest_id = entries[-1].id
    export.save()


def export_contest(export: StandingsSheetExport, service):
    standings = export.standings

    users_data, contests = get_standings_data(standings)

    column_ranges = [['A', 'C']]

    header = [
        [["Name", "Group", "Score"]],
        [["", "", ""]],
    ]

    users = dict()
    user_score = dict()
    user_ids = []
    for user in users_data:
        users[user["id"]] = [[user["name"], user["group_short"], 0]]
        user_score[user["id"]] = 0
        user_ids.append(user["id"])

    cid = 4 + export.empty_beginning_columns

    include_penalty = export.include_penalty
    include_verdict = export.include_verdict
    include_time = export.include_time

    problem_extra = 0
    if include_penalty:
        problem_extra += 1
    if include_verdict:
        problem_extra += 1
    if include_time:
        problem_extra += 1

    calc_mark = export.calculate_mark

    for contest in contests[::-1]:
        contest_width = len(contest["problems"]) * (problem_extra + 1)
        header[0].append([contest["title"]])
        header[1].append([])
        for i in contest["problems"]:
            header[1][-1].append(i["short"])
            for j in range(problem_extra):
                header[1][-1].append("")
        header[1][-1].append("Σ")
        if calc_mark:
            header[1][-1].append("Mark")
        column_ranges.append([get_column_id(cid), get_column_id(cid + contest_width + calc_mark)])
        cid += contest_width + export.empty_columns_for_contest + 1 + calc_mark

        contest_info = contest["contest_info"]
        user_scores = []

        for id in user_ids:
            if id not in contest["users"]:
                users[id].append([0] * (contest_width + 1))
                if calc_mark:
                    user_scores.append([0] * len(contest["problems"]))
                continue

            user_row = []
            total_score = 0
            if calc_mark:
                user_scores.append([])

            for prob in contest["users"][id]:
                user_row.append(prob["score"])
                if calc_mark:
                    user_scores[-1].append(prob["score"])
                total_score += prob["score"]
                if include_penalty:
                    user_row.append(prob["penalty"])
                if include_verdict:
                    if prob["verdict"] is not None:
                        user_row.append(prob["verdict"])
                    else:
                        user_row.append("")
                if include_time:
                    user_row.append(prob["time"])

            user_row.append(total_score)
            user_score[id] += total_score
            users[id].append(user_row)

        if calc_mark:
            try:
                ldict = {}
                exec(export.mark_func, locals(), ldict)
                marks = ldict["marks"]

                if len(marks) != len(user_ids):
                    marks = [0] * len(user_ids)
            except:
                marks = [0] * len(user_ids)

            for i, id in enumerate(user_ids):
                users[id][-1].append(marks[i])

    users_list = []

    for id in users:
        users[id][0][2] = user_score[id]
        if export.hide_zero_score and user_score[id] == 0:
            continue
        users_list.append(users[id])
    users_list.sort(key=lambda a: (a[0][1], a[0][0]))

    data = []
    for i in range(len(column_ranges)):
        data.append(dict())
        data[-1]["range"] = "{}!{}1:{}{}".format(
            export.tab,
            column_ranges[i][0],
            column_ranges[i][1],
            len(users_list) + 2
        )
        data[-1]["values"] = [header[0][i], header[1][i]]
        data[-1]["values"] += [users_list[j][i] for j in range(len(users_list))]

    xx = service.spreadsheets().values().batchUpdate(
        spreadsheetId=export.sheet_id,
        body={
            "valueInputOption": 'USER_ENTERED',
            "data": data,
        }
    ).execute()


def get_column_id(k):
    k -= 1
    l = 1
    PW = 26
    while k >= PW ** l:
        k -= PW ** l
        l += 1
    res = ''
    while l > 0:
        l -= 1
        t = 1
        while k >= t * PW ** l:
            t += 1
        t -= 1
        res = res + chr(65 + t)
        k -= t * PW ** l
    return res
