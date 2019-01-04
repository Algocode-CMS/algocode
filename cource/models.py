import os

from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver


class Course(models.Model):
    title = models.CharField(max_length=1000, blank=True)
    subtitle = models.TextField(blank=True)
    ejudge_url = models.CharField(max_length=1000, blank=True)
    proxy_pass_links = models.BooleanField(default=False)
    logo = models.FileField(upload_to='docs', blank=True)
    url = models.CharField(max_length=300, blank=True)
    name_in_main = models.CharField(max_length=300, blank=True)
    color = models.CharField(max_length=30, default="#000000")

    def __str__(self):
        return self.title


class Main(models.Model):
    title = models.CharField(max_length=1000, blank=True)
    subtitle = models.TextField(blank=True)
    logo = models.FileField(upload_to='docs', blank=True)
    courses = models.ManyToManyField(Course)

    def __str__(self):
        return self.title


class ContestType(models.Model):
    name = models.CharField(max_length=100)
    standings_name = models.CharField(max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='contest_types')
    olymp = models.BooleanField(default=False)
    max_score_for_olymp_problem = models.IntegerField(default=100)
    enable_marks = models.BooleanField(default=False)
    show_standings_left_link = models.BooleanField(default=False)
    allow_standings = models.BooleanField(default=True)
    exec_for_marks = models.TextField(default="# variables: user_score, max_possible_score, max_reached_score, num_of_problems, user_id\n# arrays: problem_score, num_of_solves_for_problem (problems are zero-numerated)\n# should assign mark to variable: marks[mark_key]")

    def __str__(self):
        return self.name


class Contest(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='contests')
    date = models.DateField()
    title = models.CharField(max_length=300)
    ejudge_id = models.IntegerField()
    type = models.ForeignKey(ContestType, on_delete=models.CASCADE, related_name="contests", blank=True, null=True)
    statements = models.FileField(upload_to='docs', blank=True)
    show_statements_link = models.BooleanField(default=False)
    show_in_standings = models.BooleanField(default=False)
    duration = models.FloatField(default=100000000)
    coefficient = models.FloatField(default=1)
    other_link = models.CharField(max_length=300, blank=True)
    exec_for_marks = models.TextField(default="# variables: user_score, max_possible_score, max_reached_score, num_of_problems, user_id\n# arrays: problem_score, num_of_solves_for_problem (problems are zero-numerated)\n# should assign mark to variable: marks[mark_key]")

    def __str__(self):
        return self.title


class ContestLink(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='links')
    text = models.CharField(max_length=300)
    file = models.FileField(upload_to='docs', blank=True)
    link = models.CharField(max_length=300, blank=True)


class LeftLink(models.Model):
    Course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='links')
    text = models.CharField(max_length=300)
    file = models.FileField(upload_to='docs', blank=True)
    link = models.CharField(max_length=300, blank=True)
    hidden = models.BooleanField(default=False)


class LeftMainLink(models.Model):
    main = models.ForeignKey(Main, on_delete=models.CASCADE, related_name='links')
    text = models.CharField(max_length=300)
    file = models.FileField(upload_to='docs', blank=True)
    link = models.CharField(max_length=300, blank=True)
    hidden = models.BooleanField(default=False)


@receiver(models.signals.post_delete, sender=ContestLink)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    try:
        if instance.file:
            if os.path.isfile(instance.file.path):
                os.remove(instance.file.path)
    except:
        pass


@receiver(models.signals.pre_save, sender=ContestLink)
def auto_delete_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = ContestLink.objects.get(pk=instance.pk).file
    except ContestLink.DoesNotExist:
        return False
    try:
        new_file = instance.file
        if not old_file == new_file:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
    except:
        pass


@receiver(models.signals.post_delete, sender=LeftLink)
def auto_delete_file_on_delete_1(sender, instance, **kwargs):
    try:
        if instance.file:
            if os.path.isfile(instance.file.path):
                os.remove(instance.file.path)
    except:
        pass


@receiver(models.signals.pre_save, sender=LeftLink)
def auto_delete_file_on_change_1(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = LeftLink.objects.get(pk=instance.pk).file
    except LeftLink.DoesNotExist:
        return False
    try:
        new_file = instance.file
        if not old_file == new_file:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
    except:
        pass


@receiver(models.signals.post_delete, sender=LeftMainLink)
def auto_delete_file_on_delete_11(sender, instance, **kwargs):
    try:
        if instance.file:
            if os.path.isfile(instance.file.path):
                os.remove(instance.file.path)
    except:
        pass


@receiver(models.signals.pre_save, sender=LeftMainLink)
def auto_delete_file_on_change_11(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = LeftMainLink.objects.get(pk=instance.pk).file
    except LeftMainLink.DoesNotExist:
        return False
    try:
        new_file = instance.file
        if not old_file == new_file:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
    except:
        pass


@receiver(models.signals.post_delete, sender=Main)
def auto_delete_file_on_delete_12(sender, instance, **kwargs):
    try:
        if instance.logo:
            if os.path.isfile(instance.logo.path):
                os.remove(instance.logo.path)
    except:
        pass


@receiver(models.signals.pre_save, sender=Main)
def auto_delete_file_on_change_12(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = Main.objects.get(pk=instance.pk).logo
    except Main.DoesNotExist:
        return False
    try:
        new_file = instance.logo
        if not old_file == new_file:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
    except:
        pass


@receiver(models.signals.post_delete, sender=Course)
def auto_delete_file_on_delete_13(sender, instance, **kwargs):
    try:
        if instance.logo:
            if os.path.isfile(instance.logo.path):
                os.remove(instance.logo.path)
    except:
        pass


@receiver(models.signals.pre_save, sender=Course)
def auto_delete_file_on_change_13(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = Course.objects.get(pk=instance.pk).logo
    except Course.DoesNotExist:
        return False
    try:
        new_file = instance.logo
        if not old_file == new_file:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
    except:
        pass


@receiver(models.signals.post_delete, sender=Contest)
def auto_delete_file_on_delete_2(sender, instance, **kwargs):
    if instance.statments:
        try:
            os.remove(instance.statments.path)
        except:
            pass


@receiver(models.signals.pre_save, sender=Contest)
def auto_delete_file_on_change_2(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_statements = Contest.objects.get(pk=instance.pk).statements
    except Contest.DoesNotExist:
        return False
    try:
        new_statements = instance.statements
        if not old_statements == new_statements:
            if os.path.isfile(old_statements.path):
                os.remove(old_statements.path)
    except:
        pass


class Battleship(models.Model):
    name = models.CharField(max_length=500, blank=True)
    contest = models.IntegerField()

    def __str__(self):
        return self.name


class BattleshipTeam(models.Model):
    battleship = models.ForeignKey(Battleship, on_delete=models.CASCADE, related_name='teams')
    name = models.CharField(max_length=500, blank=True)


class UserId(models.Model):
    team = models.ForeignKey(BattleshipTeam, on_delete=models.CASCADE, related_name='ids')
    user = models.IntegerField()


class ShipPosition(models.Model):
    team = models.ForeignKey(BattleshipTeam, on_delete=models.CASCADE, related_name='ships')
    x = models.IntegerField()
    y = models.IntegerField()
