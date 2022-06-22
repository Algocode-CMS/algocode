from courses.judges.common_verdicts import EJUDGE_OK
from courses.judges.judges import load_contest
from courses.models import PoleChudesGame, PoleChudesParticipant, PoleChudesLetter


def recalc_pole_chudes_standings(game: PoleChudesGame):
    teams = game.teams.order_by("id")
    participants = list(PoleChudesParticipant.objects.filter(team__in=teams))
    users = [participant.participant for participant in participants]
    contest = load_contest(game.contest, users, utc_time=True)

    for team in teams:
        let = []
        let_id = 0
        team.score = 0
        team.word_id = 0
        team.problems = 0
        team.unsuccess = 0

        for p in team.participants.all():
            if p.participant.id in contest["users"]:
                for i, submit in enumerate(contest["users"][p.participant.id]):
                    if submit["verdict"] == EJUDGE_OK and i < len(game.alphabet):
                        let.append({"time": submit["utc_time"], "letter": game.alphabet[i]})
                        team.score += game.accept_bonus
                        team.problems += 1

        let.sort(key=lambda x: x["time"])

        for i, word in enumerate(game.words.order_by("id")):
            guessed_letters = {x.letter for x in team.letters.filter(word_id=i)}
            guess_time = 10 ** 100

            for guess in team.guesses.filter(word_id=i).order_by("id"):
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

