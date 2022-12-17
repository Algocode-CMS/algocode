import os
from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver


def get_main_file_path(instance, filename):
    return 'main_{0}/{1}'.format(instance.id, filename)


def get_course_file_path(instance, filename):
    return 'course_{0}/{1}'.format(instance.course.label, filename)


def get_statements_file_path(instance, filename):
    return 'course_{0}/{1}'.format(instance.course.label, filename)


def get_blitz_statements_file_path(instance, filename):
    return 'course_{0}/{1}'.format(instance.contest.course.label, filename)


def get_contest_file_path(instance, filename):
    return 'course_{0}/{1}'.format(instance.contest.course.label, filename)


def get_photo_path(instance, filename):
    return 'photos/{0}'.format(filename)


class ContestType:
    ACM = "AC"
    OLYMP = "OL"
    BATTLESHIP = "BS"
    BLITZ = "BT"

    TYPES = (
        (ACM, "Acm"),
        (OLYMP, "Olympiad"),
        (BATTLESHIP, "Battleship"),
        (BLITZ, "Blitz"),
    )


class Teacher(models.Model):
    name = models.TextField()
    description = models.TextField(blank=True)
    photo = models.FileField(upload_to=get_photo_path, blank=True)
    vk_id = models.TextField(blank=True)
    telegram_id = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    label = models.TextField(unique=True)
    title = models.TextField(blank=True)
    subtitle = models.TextField(blank=True)
    template = models.TextField(default='course.html')
    ejudge_url = models.TextField(blank=True)
    codeforces_url = models.TextField(default="https://codeforces.com")

    def __str__(self):
        return "{} ({})".format(self.title, self.id)


class Main(models.Model):
    title = models.TextField(blank=True)
    subtitle = models.TextField(blank=True)
    courses = models.ManyToManyField(Course)
    courses_text = models.TextField(default="Курсы")

    def __str__(self):
        return self.title


class Contest(models.Model, ContestType):
    EJUDGE = 'EJ'
    CODEFORCES = 'CF'
    INFORMATICS = 'IN'
    JUDGES = (
        (EJUDGE, 'Ejudge'),
        (CODEFORCES, 'Codeforces'),
        (INFORMATICS, 'Informatics'),
    )

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='contests')
    date = models.DateField()
    title = models.TextField()
    statements = models.FileField(upload_to=get_statements_file_path, blank=True)
    show_statements = models.BooleanField(default=False)
    duration = models.IntegerField(default=0)
    coefficient = models.FloatField(default=1.0)
    contest_type = models.CharField(max_length=2, choices=ContestType.TYPES, default=ContestType.ACM)
    judge = models.CharField(max_length=2, choices=JUDGES, default=EJUDGE)
    contest_id = models.IntegerField(blank=True, null=True)
    external_group_id = models.TextField(blank=True)
    other_link = models.TextField(blank=True)
    contest_info = models.TextField(default="{}")
    score_latest = models.BooleanField(default=False)
    score_only_finished = models.BooleanField(default=False)

    def __str__(self):
        return '[{}] {}'.format(self.course.label, self.title)


class ContestStandingsHolder(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='standings_holder')
    problems = models.TextField()
    runs_list = models.TextField()


class ContestLink(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='links')
    text = models.TextField()
    file = models.FileField(upload_to=get_contest_file_path, blank=True)
    link = models.TextField(blank=True)
    new_tab = models.BooleanField(default=False)
    priority = models.IntegerField(default=0)


class CourseLink(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='links')
    text = models.TextField()
    file = models.FileField(upload_to=get_course_file_path, blank=True)
    link = models.TextField(blank=True)
    hidden = models.BooleanField(default=False)
    new_tab = models.BooleanField(default=False)
    priority = models.IntegerField(default=0)


class TeacherInCourse(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='teachers')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='courses')
    note = models.TextField(blank=True)
    priority = models.IntegerField(default=0)


class MainLink(models.Model):
    main = models.ForeignKey(Main, on_delete=models.CASCADE, related_name='links')
    text = models.TextField()
    file = models.FileField(upload_to=get_main_file_path, blank=True)
    link = models.TextField(blank=True)
    hidden = models.BooleanField(default=False)
    new_tab = models.BooleanField(default=False)
    priority = models.IntegerField(default=0)


class MainCourse(models.Model):
    main = models.ForeignKey(Main, on_delete=models.CASCADE, related_name='course_links')
    text = models.TextField()
    course = models.ForeignKey(Course, blank=True, null=True, on_delete=models.CASCADE, related_name='mains')
    url = models.TextField(blank=True)
    priority = models.IntegerField(default=0)


class ParticipantsGroup(models.Model):
    course = models.ForeignKey(Course, related_name="groups", on_delete=models.CASCADE)
    name = models.TextField()
    short_name = models.TextField()

    def __str__(self):
        return '{} ({})'.format(self.name, self.id)


class Battleship(models.Model):
    course = models.ForeignKey(Course, related_name="battleships", on_delete=models.CASCADE)
    name = models.TextField()
    contest = models.ForeignKey(Contest, related_name="battleships", on_delete=models.CASCADE)
    public = models.BooleanField(default=True)

    def __str__(self):
        return '{} ({})'.format(self.name, self.id)


class BattleshipTeam(models.Model):
    name = models.TextField()
    battleship = models.ForeignKey(Battleship, related_name="battleship_teams", on_delete=models.CASCADE)
    groups = models.ManyToManyField(ParticipantsGroup, related_name="battleship_teams", blank=True)

    def __str__(self):
        return '{} - {} ({})'.format(self.battleship, self.name, self.id)


class BattleshipShip(models.Model):
    battleship = models.ForeignKey(Battleship, related_name="ships", on_delete=models.CASCADE)
    team = models.ForeignKey(BattleshipTeam, related_name="ships", on_delete=models.CASCADE)
    x = models.IntegerField()
    y = models.IntegerField()


class Participant(models.Model):
    name = models.TextField(verbose_name='Surname and name')
    group = models.ForeignKey(ParticipantsGroup, related_name='participants', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='participants', on_delete=models.CASCADE)
    has_pass = models.BooleanField(default=False)
    ejudge_id = models.IntegerField(blank=True, null=True)
    informatics_id = models.IntegerField(blank=True, null=True)
    codeforces_handle = models.TextField(blank=True)
    photo = models.FileField(upload_to=get_photo_path, blank=True)
    comment = models.TextField(blank=True)
    email = models.TextField(blank=True)
    telegram_id = models.TextField(blank=True)
    vk_id = models.TextField(blank=True)

    def __str__(self):
        return "{} ()".format(self.name, self.id)


class BattleshipParticipant(models.Model):
    battleship = models.ForeignKey(Battleship, related_name='participants', on_delete=models.CASCADE)
    participant = models.ForeignKey(Participant, related_name='battleships', on_delete=models.CASCADE)
    team = models.ForeignKey(BattleshipTeam, related_name='participants', on_delete=models.CASCADE)
    order = models.IntegerField(blank=True, null=True)


class Standings(models.Model, ContestType):
    title = models.TextField()
    label = models.TextField(unique=True)
    contests = models.ManyToManyField(Contest, related_name="standings", blank=True)
    groups = models.ManyToManyField(ParticipantsGroup, related_name="standings", blank=True)
    course = models.ForeignKey(Course, related_name="standings", on_delete=models.CASCADE)
    olymp = models.BooleanField(default=False)
    contest_type = models.CharField(max_length=2, choices=ContestType.TYPES, default=ContestType.ACM)
    enable_marks = models.BooleanField(default=False)
    js_for_contest_mark = models.TextField(blank=True, default="var newCalculateContestMark = function(\n    total_scores,       // двумерный массив пар балла и времени сдачи задач пользователями\n    user_id,            // номер пользователя\n    contest_info        // информация о контесте\n) {\n    return useOldContestMark(total_scores, user_id)\n};")
    js_for_total_mark = models.TextField(blank=True, default="var calculateTotalMark = function(\n\tmarks,              // массив оценок за контесты\n\tcoefficients,        //  массив коэффициентов контесто\n\ttotal_score,        // суммарный балл за все контесты\n\tcontest_score,      // массив баллов за контесты\n\tcontest_max_score,  // массив максимальных набранных баллов за контесты\n\tproblem_score,      // двумерный массив набранных баллов за задачи\n\tproblem_max_score,  // двумерный массив максимальных набранных баллов за задач\n\ttotal_users,        // общее количество участников\n\tproblem_accepted    // двумерный массив количества ОК по задаче\n){\n\treturn defaultTotalMark(marks, coefficients);\n};")
    js = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Standings"

    def __str__(self):
        return "{} ({})".format(self.label, self.title)


class Page(models.Model):
    label = models.TextField(unique=True)
    title = models.TextField(blank=True)
    subtitle = models.TextField(blank=True)
    content = models.TextField(blank=True)
    is_raw = models.BooleanField(default=False)
    course = models.ForeignKey(Course, related_name="pages", blank=True, on_delete=models.SET_NULL, null=True)


class StandingsSheetExport(models.Model):
    standings = models.ForeignKey(Standings, related_name="sheets", on_delete=models.CASCADE)
    name = models.TextField(blank=True)
    sheet_id = models.TextField()
    tab = models.TextField()
    hide_zero_score = models.BooleanField(default=True)

    include_penalty = models.BooleanField(default=False)
    include_verdict = models.BooleanField(default=False)
    include_time = models.BooleanField(default=False)

    empty_columns_for_contest = models.IntegerField(default=0)
    empty_beginning_columns = models.IntegerField(default=0)

    calculate_mark = models.BooleanField(default=False)
    mark_func = models.TextField(default='''
def calc_marks_v1(
    user_scores, # 2d array containing all scores for users
    contest_info, # contest info from algocode admin
):
    return [0] * len(user_scores)
    
marks = calc_marks_v1(user_scores, contest_info)
''')


class BlitzProblem(models.Model):
    contest = models.ForeignKey(Contest, related_name="blitz_problems", on_delete=models.CASCADE)
    problem_id = models.TextField()
    description = models.TextField(blank=True)
    statements = models.FileField(upload_to=get_blitz_statements_file_path)


class BlitzProblemStart(models.Model):
    problem = models.ForeignKey(BlitzProblem, related_name="starts", on_delete=models.CASCADE)
    participant_id = models.IntegerField()
    time = models.DateTimeField(auto_now_add=True)
    bid = models.IntegerField(default=0)


class EjudgeRegisterApi(models.Model):
    name = models.TextField()
    secret = models.TextField()
    login = models.TextField()
    use_surname = models.BooleanField(default=False)


class EjudgeRegisterApiGroupAdd(models.Model):
    ejudge_register = models.ForeignKey(EjudgeRegisterApi, related_name="groups", on_delete=models.CASCADE)
    group = models.ForeignKey(ParticipantsGroup, related_name="registers", on_delete=models.CASCADE)
    use_login = models.BooleanField(default=True)


class EjudgeRegisterApiContestAdd(models.Model):
    ejudge_register = models.ForeignKey(EjudgeRegisterApi, related_name="contests", on_delete=models.CASCADE)
    contest_id = models.IntegerField()


class MailAuth(models.Model):
    name = models.TextField()
    mail_host = models.TextField()
    mail_port = models.TextField()
    mail_username = models.TextField()
    mail_password = models.TextField()
    mail_use_tls = models.BooleanField()
    mail_use_ssl = models.BooleanField()

    def __str__(self):
        return "{} ({})".format(self.name, self.id)


class FormBuilder(models.Model):
    label = models.TextField(unique=True)
    title = models.TextField()
    subtitle = models.TextField(blank=True)
    button_text = models.TextField(default="Отправить")
    response_text = models.TextField(blank=True)

    send_mail = models.BooleanField(default=False)
    mail_auth = models.ForeignKey(MailAuth, related_name="forms", blank=True, on_delete=models.SET_NULL, null=True)
    mail_topic = models.TextField(blank=True)
    mail_template = models.TextField(blank=True)

    requests_per_day_limit = models.IntegerField(blank=True, null=True)
    ip_whitelist = models.TextField(blank=True)

    register_api = models.ManyToManyField(EjudgeRegisterApi, related_name="forms", blank=True)
    register_name_template = models.TextField(blank=True)


class FormFieldType:
    STR = "ST"
    INTEGER = "IN"
    MAIL = "ML"
    PHONE = "PH"
    DATE = "DT"
    LONG = "LO"
    CHECKBOX = "CB"
    TEXT = "TX"

    TYPES = (
        (STR, "Small text field"),
        (INTEGER, "Number"),
        (MAIL, "Mail address"),
        (PHONE, "Phone number"),
        (DATE, "Date"),
        (LONG, "Large textarea"),
        (CHECKBOX, "Check box"),
        (TEXT, "Text without field"),
    )


class FormField(models.Model, FormFieldType):
    form = models.ForeignKey(FormBuilder, related_name="fields", on_delete=models.CASCADE)
    label = models.TextField()
    type = models.CharField(max_length=2, choices=FormFieldType.TYPES, default=FormFieldType.STR)
    required = models.BooleanField(default=False)
    internal_name = models.TextField()
    description = models.TextField(blank=True)


class FormEntry(models.Model):
    form = models.ForeignKey(FormBuilder, related_name="entries", on_delete=models.CASCADE)
    data = models.TextField()
    ip = models.TextField(blank=True)
    mail = models.TextField(blank=True)
    time = models.DateTimeField(auto_now_add=True)


class PoleChudesGame(models.Model):
    course = models.ForeignKey(Course, related_name="pole_chudes_games", on_delete=models.CASCADE)
    contest = models.ForeignKey(Contest, related_name="pole_chudes_games", on_delete=models.CASCADE)
    name = models.TextField()
    guess_bonus = models.IntegerField()
    miss_penalty = models.IntegerField()
    accept_bonus = models.IntegerField()
    alphabet = models.TextField(default="АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ", blank=True)
    finished = models.BooleanField(default=False)

    def __str__(self):
        return "{} ({})".format(self.name, self.id)


class PoleChudesWord(models.Model):
    game = models.ForeignKey(PoleChudesGame, related_name="words", on_delete=models.CASCADE)
    text = models.TextField()
    hint = models.TextField()


class PoleChudesTeam(models.Model):
    game = models.ForeignKey(PoleChudesGame, related_name="teams", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="pole_chudes_teams", blank=True, on_delete=models.SET_NULL, null=True)
    name = models.TextField()
    players = models.TextField(blank=True)
    score = models.IntegerField(default=0)
    word_id = models.IntegerField(default=0)
    problems = models.IntegerField(default=0)
    unsuccess = models.IntegerField(default=0)
    coins = models.IntegerField(default=0)


class PoleChudesParticipant(models.Model):
    team = models.ForeignKey(PoleChudesTeam, related_name="participants", on_delete=models.CASCADE)
    participant = models.ForeignKey(Participant, related_name="pole_chudes_participants", on_delete=models.CASCADE)


class PoleChudesGuess(models.Model):
    team = models.ForeignKey(PoleChudesTeam, related_name="guesses", on_delete=models.CASCADE)
    word_id = models.IntegerField()
    guess = models.TextField(default="")
    guessed = models.BooleanField()
    score = models.IntegerField(default=10)
    time = models.DateTimeField(auto_now_add=True)


class PoleChudesLetter(models.Model):
    team = models.ForeignKey(PoleChudesTeam, related_name="letters", on_delete=models.CASCADE)
    word_id = models.IntegerField()
    letter = models.CharField(max_length=1)
    score = models.IntegerField(default=1)
    time = models.DateTimeField(auto_now_add=True)


################################################################################################


@receiver(models.signals.post_delete, sender=ContestLink)
def auto_delete_contest_link_file_on_delete(sender, instance, **kwargs):
    try:
        if instance.file:
            if os.path.isfile(instance.file.path):
                os.remove(instance.file.path)
    except OSError:
        pass


@receiver(models.signals.pre_save, sender=ContestLink)
def auto_delete_contest_link_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = ContestLink.objects.get(pk=instance.pk).file
    except ContestLink.DoesNotExist:
        return False
    if not old_file:
        return False
    try:
        new_file = instance.file
        if not old_file == new_file:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
    except OSError:
        pass


@receiver(models.signals.post_delete, sender=CourseLink)
def auto_delete_course_link_file_on_delete(sender, instance, **kwargs):
    try:
        if instance.file:
            if os.path.isfile(instance.file.path):
                os.remove(instance.file.path)
    except OSError:
        pass


@receiver(models.signals.pre_save, sender=CourseLink)
def auto_delete_course_link_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = CourseLink.objects.get(pk=instance.pk).file
    except CourseLink.DoesNotExist:
        return False
    if not old_file:
        return False
    try:
        new_file = instance.file
        if not old_file == new_file:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
    except OSError:
        pass


@receiver(models.signals.post_delete, sender=MainLink)
def auto_delete_main_link_file_on_delete(sender, instance, **kwargs):
    try:
        if instance.file:
            if os.path.isfile(instance.file.path):
                os.remove(instance.file.path)
    except:
        pass


@receiver(models.signals.pre_save, sender=MainLink)
def auto_delete_main_link_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = MainLink.objects.get(pk=instance.pk).file
    except MainLink.DoesNotExist:
        return False
    if not old_file:
        return False
    try:
        new_file = instance.file
        if not old_file == new_file:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
    except OSError:
        pass


@receiver(models.signals.post_delete, sender=Contest)
def auto_delete_statement_file_on_delete(sender, instance, **kwargs):
    if instance.statements:
        try:
            os.remove(instance.statements.path)
        except OSError:
            pass


@receiver(models.signals.pre_save, sender=Contest)
def auto_delete_statement_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_statements = Contest.objects.get(pk=instance.pk).statements
    except Contest.DoesNotExist:
        return False
    if not old_statements:
        return False
    try:
        new_statements = instance.statements
        if not old_statements == new_statements:
            if os.path.isfile(old_statements.path):
                os.remove(old_statements.path)
    except OSError:
        pass


@receiver(models.signals.post_delete, sender=Teacher)
def auto_delete_teacher_photo_file_on_delete(sender, instance, **kwargs):
    try:
        if instance.photo:
            if os.path.isfile(instance.photo.path):
                os.remove(instance.photo.path)
    except OSError:
        pass


@receiver(models.signals.pre_save, sender=Teacher)
def auto_delete_teacher_photo_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = Teacher.objects.get(pk=instance.pk).photo
    except Teacher.DoesNotExist:
        return False
    if not old_file:
        return False
    try:
        new_file = instance.photo
        if not old_file == new_file:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
    except OSError:
        pass


@receiver(models.signals.post_delete, sender=Participant)
def auto_delete_participant_photo_file_on_delete(sender, instance, **kwargs):
    try:
        if instance.photo:
            if os.path.isfile(instance.photo.path):
                os.remove(instance.photo.path)
    except OSError:
        pass


@receiver(models.signals.pre_save, sender=Participant)
def auto_delete_participant_photo_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = Participant.objects.get(pk=instance.pk).photo
    except Participant.DoesNotExist:
        return False
    if not old_file:
        return False
    try:
        new_file = instance.photo
        if not old_file == new_file:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
    except OSError:
        pass


@receiver(models.signals.pre_save, sender=Participant)
def auto_fix_participant(sender, instance, **kwargs):
    instance.codeforces_handle = instance.codeforces_handle.lower()

    if instance.group.course != instance.course:
        instance.course = instance.group.course


@receiver(models.signals.post_delete, sender=BlitzProblem)
def auto_delete_blitz_statement_file_on_delete(sender, instance, **kwargs):
    if instance.statements:
        try:
            os.remove(instance.statements.path)
        except OSError:
            pass


@receiver(models.signals.pre_save, sender=BlitzProblem)
def auto_delete_blitz_statement_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_statements = BlitzProblem.objects.get(pk=instance.pk).statements
    except BlitzProblem.DoesNotExist:
        return False
    if not old_statements:
        return False
    try:
        new_statements = instance.statements
        if not old_statements == new_statements:
            if os.path.isfile(old_statements.path):
                os.remove(old_statements.path)
    except OSError:
        pass