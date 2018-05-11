from app.domain.league.History import History
from app.domain.league.Champions import Champions
from app.domain.schedule.Standings import Standings
from app.domain.schedule.Schedule import Schedule
from app.domain.schedule.Playoff import Playoff
from app.domain.schedule.Season import Season
from app.domain.draft.DraftPick import DraftPick
from app.domain.State import State
from app.domain.league.Team import Team
from app.server import query
from app.server import db
from sqlalchemy import func
import random


def StartOffseasonController():
    # Set Champion
    season = query(Season,
                   func.max(Season.id)).first()[0]
    championshipRound = query(Playoff).filter_by(playoff_round=4).first()
    championshipGame = championshipRound.game
    championshipResult = championshipRound.result

    champion = None
    if championshipResult.home_score > championshipResult.away_score:
        champion = Champions(championshipGame.home, season)
    else:
        champion = Champions(championshipGame.away, season)
    db.session.add(champion)

    # set draft picks for championship
    for r in range(1, 8):
        print("champ round {}".format(r))
        dp = DraftPick(champion.team, 32 * r)
        db.session.add(dp)

    for index, team in enumerate(reversed(Standings.getFullLeagueStandings())):
        # set draft picks
        if team.id != champion.team.id:
            if index == 32:
                index = 30
            for r in range(0, 7):
                print(team.city, r, index, index + 1 + 32 * r)
                dp = DraftPick(team, index + 1 + 32 * r)
                db.session.add(dp)

        # Copy History
        history = History(team, season)
        db.session.add(history)

        # Reset Team wins
        team.wins = 0
        team.losses = 0
        team.points_for = 0
        team.points_against = 0

    # Clear Schedule
    query(Schedule).delete()
    query(Playoff).delete()

    # Advance Season
    nextSeason = Season("Season {}".format(season.id + 1))
    db.session.add(nextSeason)
    db.session.commit()


def TrainTeams():
    state = query(State).first()
    teams = query(Team).all()
    for team in teams:
        # skip the player managed team
        if team.id == state.team.id:
            print("skipping player managed team {}".format(team.city))
            continue

        # Adjust team rankings
        rand = random.random()
        if rand > 0.5 and team.offense < 5:
            team.offense += 1
        elif rand < 0.5 and team.offense > 1:
            team.offense -= 1

        rand = random.random()
        if rand > 0.5 and team.defense < 5:
            team.defense += 1
        elif rand < 0.5 and team.defense > 1:
            team.defense -= 1

        rand = random.random()
        if rand > 0.5 and team.special_teams < 5:
            team.special_teams += 1
        elif rand < 0.5 and team.special_teams > 1:
            team.special_teams -= 1
