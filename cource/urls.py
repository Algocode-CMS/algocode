from django.contrib import admin
from django.urls import path

from cource.views import *

urlpatterns = [
    path('<int:course_id>/', CourseView.as_view(), name='course'),
    path('<int:course_id>/standings/', StandingsView.as_view(), name='standings'),
    path('<int:course_id>/battleship/<int:battleship_id>/', BattleshipView.as_view(), name='battleship'),
    path('main/<int:main_id>/', MainView.as_view(), name='main'),
]

admin.site.site_header = "Algocode admin"
admin.site.site_title = "Algocode admin"
admin.site.index_title = "Algocode admin"
