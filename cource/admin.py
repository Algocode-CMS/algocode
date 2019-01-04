from django import forms
from django.contrib import admin
from django.urls import resolve

from cource.models import *


class ContestInline(admin.TabularInline):
    model = Contest
    show_change_link = True
    exclude = ['exec_for_marks']

    def get_formset(self, request, obj=None, **kwargs):
        self.parent_obj = obj
        return super(ContestInline, self).get_formset(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "type":
            if self.parent_obj is not None:
                kwargs["queryset"] = ContestType.objects.filter(course_id=self.parent_obj.id)
            else:
                kwargs["queryset"] = ContestType.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ContestTypeInline(admin.TabularInline):
    model = ContestType
    show_change_link = True
    exclude = ['exec_for_marks']


class LeftLinkInline(admin.TabularInline):
    model = LeftLink
    show_change_link = True


class ContestLinkInline(admin.TabularInline):
    model = ContestLink
    show_change_link = True


class UserIdInline(admin.TabularInline):
    model = UserId
    show_change_link = True


class ShipPositionInline(admin.TabularInline):
    model = ShipPosition
    show_change_link = True


class BattleshipTeamInline(admin.TabularInline):
    model = BattleshipTeam
    show_change_link = True


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    inlines = [ContestTypeInline, LeftLinkInline, ContestInline]
    list_display = ['id', 'title']


@admin.register(ContestType)
class ContestTypeAdmin(admin.ModelAdmin):
    inlines = [ContestInline]
    list_display = ['id', 'name', 'olymp', 'enable_marks', 'show_standings_left_link', 'allow_standings']


@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    inlines = [ContestLinkInline]
    list_display = ['id', 'title', 'ejudge_id', 'type', 'show_statements_link', 'show_in_standings', 'duration', 'coefficient']


@admin.register(Battleship)
class BattleshipAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'contest']
    inlines = [BattleshipTeamInline]
