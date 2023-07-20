from django.contrib import admin
from django.forms import TextInput, Textarea, NumberInput, SelectMultiple
from django import forms

from courses.models import *


class ContestInlineForm(forms.ModelForm):
    add_new_standings = forms.ModelChoiceField(queryset=Standings.objects.none(), required=False, label="add new standings")
    current_standings = forms.ModelMultipleChoiceField(queryset=Standings.objects.none(), required=False, label="current standings")

    def __init__(self, *args, **kwargs):
        super(ContestInlineForm, self).__init__(*args, **kwargs)
        if self.instance.pk is not None:
            self.fields['add_new_standings'] = forms.ModelChoiceField(queryset=Standings.objects.filter(course=self.instance.course), required=False)
            self.fields['current_standings'] = forms.ModelMultipleChoiceField(queryset=self.instance.standings.all(), required=False, initial=self.instance.standings.all())

    class Meta:
        model = Course
        fields = '__all__'

    def save(self, commit=True):
        remained_standings = self.cleaned_data.get("current_standings", None)
        try:
            removed_standings = self.instance.standings.difference(remained_standings)
            for standings in removed_standings:
                standings.contests.remove(self.instance)
        except:
            pass
        new_standing = self.cleaned_data.get('add_new_standings', None)
        try:
            new_standing.contests.add(self.instance)
        except:
            pass
        return super(ContestInlineForm, self).save(commit=commit)


class ContestInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 20})},
    }
    model = Contest
    form = ContestInlineForm
    show_change_link = True


class CourseLinkInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    model = CourseLink
    show_change_link = True


class MainLinkInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    model = MainLink
    show_change_link = True


class MainCourseInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    model = MainCourse


class ContestLinkInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    model = ContestLink
    show_change_link = True


class ContestUserLoadInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    model = ContestUsersLoad


class GroupInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    model = ParticipantsGroup
    show_change_link = True


class ParticipantInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 20})},
    }
    model = Participant
    show_change_link = True
    exclude = ['person']

    def get_formset(self, request, obj=None, **kwargs):
        self.parent_obj = obj
        return super(ParticipantInline, self).get_formset(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "group":
            if self.parent_obj is not None:
                kwargs["queryset"] = ParticipantsGroup.objects.filter(course_id=self.parent_obj.id)
            else:
                kwargs["queryset"] = ParticipantsGroup.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class BattleshipInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 20})},
    }
    model = Battleship
    show_change_link = True

    def get_formset(self, request, obj=None, **kwargs):
        self.parent_obj = obj
        return super(BattleshipInline, self).get_formset(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "contest":
            if self.parent_obj is not None:
                kwargs["queryset"] = Contest.objects.filter(course_id=self.parent_obj.id)
            else:
                kwargs["queryset"] = Contest.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class BattleshipTeamInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 20})},
    }
    model = BattleshipTeam

    def get_formset(self, request, obj=None, **kwargs):
        self.parent_obj = obj
        return super(BattleshipTeamInline, self).get_formset(request, obj, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "groups":
            kwargs["queryset"] = ParticipantsGroup.objects.all().order_by("id")

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class BattleshipParticipantInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 20})},
    }
    model = BattleshipParticipant
    show_change_link = True
    extra = 10

    def get_formset(self, request, obj=None, **kwargs):
        self.parent_obj = obj
        return super(BattleshipParticipantInline, self).get_formset(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "team":
            if self.parent_obj is not None:
                kwargs["queryset"] = BattleshipTeam.objects.filter(battleship_id=self.parent_obj.id)
            else:
                kwargs["queryset"] = BattleshipTeam.objects.none()
        if db_field.name == "participant":
            if self.parent_obj is not None:
                teams = BattleshipTeam.objects.filter(battleship_id=self.parent_obj.id)
                groups = ParticipantsGroup.objects.filter(battleship_teams__in=teams)
                kwargs["queryset"] = Participant.objects.filter(group__in=groups).order_by("name")
            else:
                kwargs["queryset"] = Participant.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class NotCourseParticipantInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    model = Participant
    show_change_link = True
    exclude = ['course']


class ContestInStandingInline(admin.TabularInline):
    model = Standings.contests.through
    show_change_link = True

    def get_formset(self, request, obj=None, **kwargs):
        self.parent_obj = obj
        return super(ContestInStandingInline, self).get_formset(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "contest":
            if self.parent_obj is not None:
                kwargs["queryset"] = Contest.objects.filter(course_id=self.parent_obj.course.id)
            else:
                kwargs["queryset"] = Contest.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class StandingsInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    model = Standings
    show_change_link = True
    # exclude = ["js_for_contest_mark", "js_for_total_mark", "js"]
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        self.parent_obj = obj
        return super(StandingsInline, self).get_formset(request, obj, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "contests":
            if self.parent_obj is not None:
                kwargs["queryset"] = Contest.objects.filter(course_id=self.parent_obj.id)
            else:
                kwargs["queryset"] = Contest.objects.none()
        if db_field.name == "groups":
            if self.parent_obj is not None:
                kwargs["queryset"] = ParticipantsGroup.objects.filter(course_id=self.parent_obj.id)
                for standings in self.parent_obj.standings.all():
                    used_groups = ParticipantsGroup.objects.filter(standings=standings)
                    kwargs["queryset"] |= used_groups
                kwargs["queryset"] = kwargs["queryset"].distinct()
            else:
                kwargs["queryset"] = ParticipantsGroup.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# class TeacherInline(admin.TabularInline):
#     model = Course.teachers.through
#     show_change_link = True


class TeacherInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    model = TeacherInCourse


class CourseInline(admin.TabularInline):
    model = Main.courses.through
    show_change_link = True


class BlitzProblemInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    model = BlitzProblem


class BlitzProblemStartInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    model = BlitzProblemStart


class PageInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    model = Page


class EjudgeRegisterApiGroupInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    model = EjudgeRegisterApiGroupAdd


class EjudgeRegisterApiContestInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    model = EjudgeRegisterApiContestAdd


class FormFieldInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    model = FormField


class FormExportInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    model = FormSheetsExport
    exclude = ['latest_id', 'latest_row']
    extra = 0


class SheetsExportInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    model = StandingsSheetExport
    extra = 0


@admin.register(Main)
class MainAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    list_display = ['id', 'title', 'subtitle']
    inlines = [MainCourseInline, MainLinkInline]
    exclude = ['courses']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    inlines = [CourseLinkInline, StandingsInline, ContestInline, GroupInline, ParticipantInline, BattleshipInline, PageInline, TeacherInline]
    list_display = ['id', 'label', 'title', 'subtitle']


@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    inlines = [ContestLinkInline, ContestUserLoadInline, BlitzProblemInline]
    list_display = ['id', 'title', 'date', 'contest_type', 'judge']


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    list_display = ['id', 'name', 'group', 'ejudge_id', 'codeforces_handle']
    exclude = ['course']

    def save_form(self, request, form, change):
        instance = form.save(commit=False)
        instance.course = instance.group.course
        instance.save()
        form.save_m2m()
        return instance

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            if type(instance) == Participant:
                instance.course = instance.group.course
                instance.save()
        formset.save_m2m()


@admin.register(ParticipantsGroup)
class ParticipantsGroupAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    list_display = ['id', 'course', 'name', 'short_name']
    inlines = [NotCourseParticipantInline]

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            if type(instance) == Participant:
                instance.course = instance.group.course
                instance.save()
        formset.save_m2m()


@admin.register(Standings)
class StandingsAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    list_display = ['id', 'label', 'title', 'contest_type']
    inlines = [ContestInStandingInline, SheetsExportInline]
    exclude = ['contests']


@admin.register(Page)
class PagesAdmin(admin.ModelAdmin):
    list_display = ['id', 'label', 'title', 'subtitle']


@admin.register(Teacher)
class TeachersAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    list_display = ['id', 'name', 'description']


@admin.register(BlitzProblem)
class BlitzProblemAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    list_display = ['id', 'problem_id', 'contest']
    inlines = [BlitzProblemStartInline]


@admin.register(BlitzProblemStart)
class BlitzProblemStartAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    list_display = ['id', 'problem', 'participant_id', 'time', 'bid']


@admin.register(EjudgeRegisterApi)
class EjudgeRegisterApiAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    inlines = [EjudgeRegisterApiGroupInline, EjudgeRegisterApiContestInline]
    list_display = ['id', 'name', 'login']


@admin.register(Battleship)
class BattleshipAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    inlines = [BattleshipTeamInline, BattleshipParticipantInline]
    list_display = ['id', 'name', 'course']


@admin.register(FormBuilder)
class FormAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    inlines = [FormFieldInline, FormExportInline]
    list_display = ['id', 'label', 'title', 'subtitle']


class PoleChudesTeamInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 20})},
    }
    model = PoleChudesTeam
    show_change_link = True
    extra = 10


class PoleChudesWordInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 20})},
    }
    model = PoleChudesWord
    extra = 10


@admin.register(PoleChudesGame)
class PoleChudesAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    list_display = ['id', 'course', 'name']
    inlines = [PoleChudesTeamInline, PoleChudesWordInline]


class PoleChudesParticipantInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 20})},
    }
    model = PoleChudesParticipant
    show_change_link = True
    extra = 10

    def get_formset(self, request, obj=None, **kwargs):
        self.parent_obj = obj
        return super(PoleChudesParticipantInline, self).get_formset(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "participant":
            if self.parent_obj is not None:
                teams = list(PoleChudesTeam.objects.filter(id=self.parent_obj.id))
                if len(teams) != 0:
                    kwargs["queryset"] = Participant.objects.filter(course_id=teams[0].game.course.id).order_by("name")
                else:
                    kwargs["queryset"] = Participant.objects.none()
            else:
                kwargs["queryset"] = Participant.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class PoleChudesGuessInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 20})},
    }
    model = PoleChudesGuess
    extra = 0


class PoleChudesLetterInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 20})},
    }
    model = PoleChudesLetter
    extra = 1


@admin.register(PoleChudesTeam)
class PoleChudesTeamAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    list_display = ['id', 'game', 'name']
    inlines = [PoleChudesParticipantInline, PoleChudesGuessInline, PoleChudesLetterInline]


@admin.register(StandingsSheetExport)
class StandingsSheetExportAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    list_display = ['id', 'name', 'standings']


@admin.register(FormSheetsExport)
class FormSheetExportAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    list_display = ['id', 'name', 'form', 'do_update']
    exclude = ['latest_id', 'latest_row']


# Better hide it from admin page and show only for editing
# @admin.register(MailAuth)
# class MailAuthAdmin(admin.ModelAdmin):
#     formfield_overrides = {
#         models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
#     }
#     list_display = ['id', 'name']
