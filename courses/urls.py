from django.contrib import admin
from django.urls import path

from courses.views import *

urlpatterns = [
    path('', MainView.as_view(), name='main'),
    path('main/<int:main_id>/', MainView.as_view(), name='main'),
    path('page/<str:page_label>/', PageView.as_view(), name='page'),
    path('standings/<int:standings_id>/', StandingsView.as_view(), name='standings'),
    path('standings/<int:standings_id>/<int:contest_id>/', StandingsView.as_view(), name='standings'),
    path('standings_data/<int:standings_id>/', StandingsDataView.as_view(), name='standings_data'),
    path('<str:course_label>/', CourseView.as_view(), name='course'),
]

admin.site.site_header = "Algocode admin"
admin.site.site_title = "Algocode admin"
admin.site.index_title = "Algocode admin"
