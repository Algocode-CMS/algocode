from django.contrib import admin
from django.urls import path
from django.views.decorators.cache import cache_page

from courses.views import *

urlpatterns = [
    path('', MainView.as_view(), name='main'),
    path('main/<int:main_id>/', MainView.as_view(), name='main'),
    path('page/<str:page_label>/', PageView.as_view(), name='page'),
    path('standings/<int:standings_id>/', cache_page(60)(StandingsView.as_view()), name='standings'),
    path('standings/<int:standings_id>/<int:contest_id>/', cache_page(60)(StandingsView.as_view()), name='standings'),
    path('standings_data/<int:standings_id>/', cache_page(60)(StandingsDataView.as_view()), name='standings_data'),
    path('serve_control/', ServeControl.as_view(), name='serve_control'),
    path('serve_control/restart_ejudge/', RestartEjudge.as_view(), name='restart_ejudge'),
    path('serve_control/create_valuer/', CreateValuer.as_view(), name='create_valuer'),
    path('login/', Login.as_view(), name="login"),
    path('blitz/<int:contest_id>/', BlitzView.as_view(), name="blitz_view"),
    path('blitz/problem/<int:problem_id>/open', BlitzOpenProblem.as_view(), name="blitz_open_problem"),
    path('blitz/problem/<int:problem_id>/make_bid', BlitzMakeBid.as_view(), name="blitz_make_bid"),
    path('<str:course_label>/', CourseView.as_view(), name='course'),
]

admin.site.site_header = "Algocode admin"
admin.site.site_title = "Algocode admin"
admin.site.index_title = "Algocode admin"
