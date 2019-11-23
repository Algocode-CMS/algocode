from django.contrib import admin
from django.forms import TextInput, Textarea, NumberInput
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


class ContestLinkInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    model = ContestLink
    show_change_link = True


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
                print(self.parent_obj.standings.all())
                for standings in self.parent_obj.standings.all():
                    print(standings)
                    print(ParticipantsGroup.objects.filter(standings=standings))
                    kwargs["queryset"] = kwargs["queryset"].union(ParticipantsGroup.objects.filter(standings=standings))
            else:
                kwargs["queryset"] = ParticipantsGroup.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class TeacherInline(admin.TabularInline):
    model = Course.teachers.through
    show_change_link = True


class CourseInline(admin.TabularInline):
    model = Main.courses.through
    show_change_link = True


class TeacherInPersonInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    model = Teacher
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


@admin.register(Main)
class MainAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    list_display = ['id', 'title', 'subtitle']
    inlines = [CourseInline, MainLinkInline]
    exclude = ['courses']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    inlines = [CourseLinkInline, StandingsInline, ContestInline, GroupInline, ParticipantInline, TeacherInline]
    list_display = ['id', 'title', 'subtitle']
    exclude = ['teachers']


@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    inlines = [ContestLinkInline, BlitzProblemInline]
    list_display = ['id', 'title', 'date', 'contest_type', 'judge']


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    list_display = ['id', 'name', 'group', 'has_pass', 'ejudge_id', 'codeforces_handle', 'informatics_id']
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
    list_display = ['id', 'title', 'contest_type']
    inlines = [ContestInStandingInline]
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


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    list_display = ['id', 'name']
    inlines = [NotCourseParticipantInline, TeacherInPersonInline]


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
