from django.contrib import admin
from django.forms import TextInput, Textarea

from courses.models import *


class ContestInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    model = Contest
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
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    model = Participant
    show_change_link = True

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


class GroupParticipantInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    model = Participant
    show_change_link = True
    exclude = ['course']


@admin.register(Main)
class MainAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    list_display = ['id', 'title', 'subtitle']
    inlines = [MainLinkInline]


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    inlines = [CourseLinkInline, ContestInline, GroupInline, ParticipantInline]
    list_display = ['id', 'title', 'subtitle']


@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    inlines = [ContestLinkInline]
    list_display = ['id', 'title', 'date', 'judge']


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    list_display = ['id', 'name', 'group', 'ejudge_id', 'codeforces_handle', 'informatics_id']
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
    inlines = [GroupParticipantInline]

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
    list_display = ['id', 'title']


@admin.register(Page)
class PagesAdmin(admin.ModelAdmin):
    list_display = ['id', 'label', 'title', 'subtitle']


@admin.register(Teacher)
class TeachersAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    list_display = ['id', 'name', 'description']
