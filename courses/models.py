import os

from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver


def get_main_file_path(instance, filename):
    return 'main_{0}/{1}'.format(instance.id, filename)


def get_course_file_path(instance, filename):
    return 'course_{0}/{1}'.format(instance.course.label, filename)


def get_statements_file_path(instance, filename):
    return 'course_{0}/{1}'.format(instance.course.label, filename)


def get_contest_file_path(instance, filename):
    return 'course_{0}/{1}'.format(instance.contest.course.label, filename)


def get_photo_path(instance, filename):
    return 'photos/{0}'.format(filename)


class Person(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name


class Teacher(models.Model):
    name = models.TextField()
    person = models.ForeignKey(Person, related_name="teachers", blank=True, null=True, on_delete=models.SET_NULL)
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
    url = models.TextField(blank=True)
    name_in_main = models.TextField(blank=True)
    teachers = models.ManyToManyField(Teacher, related_name='courses', blank=True)

    def __str__(self):
        return self.title


class Main(models.Model):
    title = models.TextField(blank=True)
    subtitle = models.TextField(blank=True)
    courses = models.ManyToManyField(Course)

    def __str__(self):
        return self.title


class Contest(models.Model):
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
    is_olymp = models.BooleanField(default=False)
    judge = models.CharField(max_length=2, choices=JUDGES, default=EJUDGE)
    contest_id = models.IntegerField()
    external_group_id = models.TextField(blank=True)
    other_link = models.TextField(blank=True)

    def __str__(self):
        return '[{}] {}'.format(self.course.label, self.title)


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


class MainLink(models.Model):
    main = models.ForeignKey(Main, on_delete=models.CASCADE, related_name='links')
    text = models.TextField()
    file = models.FileField(upload_to=get_main_file_path, blank=True)
    link = models.TextField(blank=True)
    hidden = models.BooleanField(default=False)
    new_tab = models.BooleanField(default=False)
    priority = models.IntegerField(default=0)


class ParticipantsGroup(models.Model):
    course = models.ForeignKey(Course, related_name="groups", on_delete=models.CASCADE)
    name = models.TextField()
    short_name = models.TextField()

    def __str__(self):
        return self.name


class Participant(models.Model):
    name = models.TextField(verbose_name='Surname and name')
    group = models.ForeignKey(ParticipantsGroup, related_name='participants', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='participants', on_delete=models.CASCADE)
    has_pass = models.BooleanField(default=False)
    ejudge_id = models.IntegerField(blank=True, null=True)
    informatics_id = models.IntegerField(blank=True, null=True)
    codeforces_handle = models.TextField(blank=True)
    photo = models.FileField(upload_to=get_photo_path, blank=True)
    person = models.ForeignKey(Person, related_name="participants", blank=True, null=True, on_delete=models.SET_NULL)
    comment = models.TextField(blank=True)
    email = models.TextField(blank=True)
    telegram_id = models.TextField(blank=True)
    vk_id = models.TextField(blank=True)

    def __str__(self):
        return self.name + " - " + self.group.short_name


class Standings(models.Model):
    title = models.TextField()
    contests = models.ManyToManyField(Contest, related_name="standings", blank=True)
    groups = models.ManyToManyField(ParticipantsGroup, related_name="standings", blank=True)
    course = models.ForeignKey(Course, related_name="standings", on_delete=models.CASCADE)
    olymp = models.BooleanField(default=False)
    enable_marks = models.BooleanField(default=False)
    js_for_contest_mark = models.TextField(blank=True, default="var calculateContestMark = function(\n\ttotal_score,        // суммарный балл за контест\n\tproblem_score,      // массив баллов за задачи\n\tproblem_max_score,  // массив максимальных набранных баллов за задачи\n\ttotal_users,        // общее количество участников\n\tproblem_accepted   // массив количества ОК по задаче\n) {\n\treturn defaultContestMark(total_score, problem_score);\n};")
    js_for_total_mark = models.TextField(blank=True, default="var calculateTotalMark = function(\n\tmarks,              // массив оценок за контесты\n\tcoefficients,        //  массив коэффициентов контесто\n\ttotal_score,        // суммарный балл за все контесты\n\tcontest_score,      // массив баллов за контесты\n\tcontest_max_score,  // массив максимальных набранных баллов за контесты\n\tproblem_score,      // двумерный массив набранных баллов за задачи\n\tproblem_max_score,  // двумерный массив максимальных набранных баллов за задач\n\ttotal_users,        // общее количество участников\n\tproblem_accepted    // двумерный массив количества ОК по задаче\n){\n\treturn defaultTotalMark(marks, coefficients);\n};")
    js = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Standings"

    def __str__(self):
        return "{} ({})".format(self.title, self.id)


class Page(models.Model):
    label = models.TextField(unique=True)
    title = models.TextField(blank=True)
    subtitle = models.TextField(blank=True)
    content = models.TextField(blank=True)
    is_raw = models.BooleanField(default=False)


class InformaticsToken(models.Model):
    contest_id = models.TextField()
    group_id = models.TextField()
    token = models.TextField()

    class Meta:
        index_together = [
            ('contest_id', 'group_id'),
        ]


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
def auto_assign_person_for_participant(sender, instance, **kwargs):
    if instance.person is None:
        try:
            person = Person.objects.get(name=instance.name)
        except Person.DoesNotExist:
            person = Person.objects.create(name=instance.name)
            person.save()
        instance.person = person

    if instance.group.course != instance.course:
        instance.course = instance.group.course
