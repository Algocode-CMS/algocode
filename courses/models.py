import os

from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver


def get_main_file_path(instance, filename):
    return filename


def get_course_file_path(instance, filename):
    return 'course_{0}/{1}'.format(instance.course.label, filename)


def get_statements_file_path(instance, filename):
    return 'course_{0}/{1}'.format(instance.course.label, filename)


def get_contest_file_path(instance, filename):
    return 'course_{0}/{1}'.format(instance.contest.course.label, filename)


def get_photo_path(instance, filename):
    return 'photos/{0}'.format(filename)


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
    url = models.TextField(blank=True)
    name_in_main = models.TextField(blank=True)
    teachers = models.ManyToManyField(Teacher, related_name='courses')

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


class CourseLink(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='links')
    text = models.TextField()
    file = models.FileField(upload_to=get_course_file_path, blank=True)
    link = models.TextField(blank=True)
    hidden = models.BooleanField(default=False)
    new_tab = models.BooleanField(default=False)


class MainLink(models.Model):
    main = models.ForeignKey(Main, on_delete=models.CASCADE, related_name='links')
    text = models.TextField()
    file = models.TextField(get_main_file_path, blank=True)
    link = models.TextField(blank=True)
    hidden = models.BooleanField(default=False)
    new_tab = models.BooleanField(default=False)


class ParticipantsGroup(models.Model):
    name = models.TextField()
    short_name = models.TextField()

    def __str__(self):
        return self.name


class Participant(models.Model):
    name = models.TextField()
    ejudge_id = models.IntegerField(blank=True, null=True)
    informatics_id = models.IntegerField(blank=True, null=True)
    codeforces_handle = models.TextField(blank=True)
    groups = models.ManyToManyField(ParticipantsGroup, related_name='participants')

    def __str__(self):
        return self.name


class Standings(models.Model):
    title = models.TextField()
    groups = models.ManyToManyField(ParticipantsGroup)
    contests = models.ManyToManyField(Contest)
    js = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Standings"


class Page(models.Model):
    label = models.TextField(unique=True)
    title = models.TextField()
    subtitle = models.TextField()
    content = models.TextField()


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
def auto_delete_photo_file_on_delete(sender, instance, **kwargs):
    try:
        if instance.photo:
            if os.path.isfile(instance.photo.path):
                os.remove(instance.photo.path)
    except OSError:
        pass


@receiver(models.signals.pre_save, sender=Teacher)
def auto_delete_photo_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = ContestLink.objects.get(pk=instance.pk).photo
    except ContestLink.DoesNotExist:
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
