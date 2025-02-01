from django.urls import path
from django.views.decorators.cache import cache_page

from algocode.settings import DEFAULT_HOME
from courses.views import *


urlpatterns = [
    path('', MainView.as_view() if DEFAULT_HOME == "main" else CourseView.as_view() if DEFAULT_HOME == "course" else PageView.as_view(), name='main'),
    path('main/<int:main_id>/', MainView.as_view(), name='main'),
    path('page/<str:page_label>/', PageView.as_view(), name='page'),
    path('standings/<str:standings_label>/', cache_page(0)(StandingsView.as_view()), name='standings'),
    path('standings/<str:standings_label>/<int:contest_id>/', cache_page(0)(StandingsView.as_view()), name='standings'),
    path('standings_data/<str:standings_label>/', cache_page(0)(StandingsDataView.as_view()), name='standings_data'),
    path('participants_group/<int:group_id>', cache_page(0)(ParticipantsGroupView.as_view()), name='participants_group'),
    path('serve_control/', ServeControl.as_view(), name='serve_control'),
    path('serve_control/restart_ejudge/', RestartEjudge.as_view(), name='restart_ejudge'),
    path('serve_control/create_valuer/', CreateValuer.as_view(), name='create_valuer'),
    path('login/', Login.as_view(), name="login"),
    path('blitz/<int:contest_id>/', BlitzView.as_view(), name="blitz_view"),
    path('blitz/problem/<int:problem_id>/open', BlitzOpenProblem.as_view(), name="blitz_open_problem"),
    path('blitz/problem/<int:problem_id>/make_bid', BlitzMakeBid.as_view(), name="blitz_make_bid"),
    path('battleship/<int:battleship_id>/', BattleshipView.as_view(), name='battleship'),
    path('battleship_admin/<int:battleship_id>/', BattleshipAdminView.as_view(), name='battleship_admin'),
    path('pole_chudes/team/<int:team_id>/', PoleChudesTeamView.as_view(), name='pole_chudes_team'),
    path('pole_chudes/team/guess/<int:team_id>/', PoleChudesGuessView.as_view(), name='pole_chudes_team_guess'),
    path('pole_chudes/<int:game_id>/', PoleChudesTeamsView.as_view(), name='pole_chudes'),
    path('api/ejudge_register/', EjudgeRegister.as_view(), name='ejudge_register_api'),
    path('form/data/', FormDataView.as_view(), name='form_data'),
    path('form/export/json/<str:form_label>', FormJsonExport.as_view(), name='form_json_export'),
    path('form/export/csv/<str:form_label>', FormCSVExport.as_view(), name='form_csv_export'),
    path('form/<str:form_label>/', FormView.as_view(), name='form'),
    path('<str:course_label>/', CourseView.as_view(), name='course'),
]
