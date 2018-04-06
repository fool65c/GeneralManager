from app.domain.GameType import GameType
from app.domain.Champions import Champions
from app.domain.Schedule import Schedule
from app.domain.History import History
from app.domain.Season import Season
from app.domain.Team import Team
from app.server import query
from app.server import db
from sqlalchemy import func
import random


def OffseasonController():
    # Set Champion
    gT = query(GameType).filter_by(game_type="post season").first()
    season = query(Season,
                   func.max(Season.id)).first()[0]
    chapionshipGame = query(Schedule,
                            func.max(Schedule.week)) \
                            .filter_by(game_type=gT).first()[0]

    champion = None
    if chapionshipGame.result.home_score > chapionshipGame.result.away_score:
        champion = Champions(chapionshipGame.game.home,
                             season)
    else:
        champion = Champions(chapionshipGame.game.away,
                             season)
    db.session.add(champion)

    teams = query(Team).all()
    for team in teams:
        # Copy History
        history = History(team, season)
        db.session.add(history)

        # Reset Team wins
        team.wins = 0
        team.losses = 0
        team.points_for = 0
        team.points_against = 0

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

    # Clear Schedule
    query(Schedule).delete()

    # Advance Season
    nextSeason = Season("Season {}".format(season.id + 1))
    db.session.add(nextSeason)
    db.session.commit()


def PrepRankingsController(rankings):
    teams = []
    for rank, team in rankings.rankings.items():
        teams.append(team)
    return teams
