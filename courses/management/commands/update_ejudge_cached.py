from django.core.management.base import BaseCommand

from courses.models import Contest
from courses.judges import ejudge_cached


class Command(BaseCommand):
    help = 'Loads data for cached ejudge standings'

    def handle(self, *args, **options):
        contests = Contest.objects.filter(judge=Contest.EJUDGE_CACHED)
        for contest in contests:
            print("loading", contest.contest_id)
            try:
                ejudge_cached.load_ejudge_cached_contest(contest)
            except:
                print("Can not update contest, unknown error")

        print('Ejudge cached loaded!')
