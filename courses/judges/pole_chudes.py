from courses.judges.common_verdicts import EJUDGE_OK
from courses.judges.judges import load_contest
from courses.models import PoleChudesGame, PoleChudesParticipant, PoleChudesLetter, Participant
from django.db.models import prefetch_related_objects
import logging


def recalc_pole_chudes_standings(game: PoleChudesGame):
    logger = logging.getLogger(__name__)
    teams = game.teams.order_by("id")
    users = list(Participant.objects.filter(pole_chudes_participants__team__in=teams))
    contest = load_contest(game.contest, users, utc_time=True)

    for team in teams:
        let = []
        let_id = 0
        team.score = 0
        team.word_id = 0
        team.problems = 0
        team.unsuccess = 0

        for p in team.participants.prefetch_related("participant"):
            if p.participant.id in contest["users"]:
                for i, submit in enumerate(contest["users"][p.participant.id]):
                    if submit["verdict"] == EJUDGE_OK and i < len(game.alphabet):
                        let.append({"time": submit["utc_time"], "letter": game.alphabet[i]})
                        team.score += game.accept_bonus
                        team.problems += 1

        let.sort(key=lambda x: x["time"])

        all_guessed = team.guesses.order_by("id")
        all_letters = list(team.letters.all())

        for i, word in enumerate(game.words.order_by("id")):
            guessed_letters = set()

            for letter in all_letters:
                if letter.word_id == i:
                    guessed_letters.add(letter.letter)

            guess_time = 10 ** 100

            for guess in all_guessed:
                if guess.word_id != i:
                    continue
                team.score += guess.score
                if guess.guessed:
                    guess_time = guess.time.timestamp()
                    team.word_id += 1
                    break
                else:
                    team.unsuccess += 1

            while let_id < len(let) and let[let_id]["time"] < guess_time:
                if let[let_id]["letter"] not in guessed_letters:
                    letter = PoleChudesLetter.objects.create(
                        team=team,
                        word_id=i,
                        letter=let[let_id]["letter"],
                        score=0,
                    )
                    letter.save()
                    guessed_letters.add(let[let_id]["letter"])
                let_id += 1

        team.save()

