from sqlalchemy import func
from app.domain.Game import Game
from app.domain.Standings import Standings
from app.domain.GameType import GameType
from app.domain.Schedule import Schedule
from app.server import db
from app.server import query


class PostSeasonSchedule(object):
    def __init__(self):
        self.post_season_teams = 8

    def advancePostSeasonSchedule(self):
        standings = Standings()
        gameType = query(GameType).filter_by(game_type="post season") \
                                  .first()

        maxWeek = query(Schedule,
                        func.max(Schedule.week)).filter_by(game_type=gameType)\
                                                .first()
        lastWeek = maxWeek[1]

        playoffTeams = {}
        if lastWeek is None:
            for rank in range(1, self.post_season_teams+1):
                playoffTeams[rank] = standings.rankings[rank]
            maxWeek = query(Schedule, func.max(Schedule.week)).first()
        else:
            # we'll need to pick winners
            games = query(Schedule) \
                    .filter_by(game_type=gameType) \
                    .filter_by(week=lastWeek).all()

            if len(games) <= 1:
                # Season's over son
                return None
            else:
                count = 1
                print(games)
                for game in games:
                    print(game.toJSON())
                    if game.result.home_score > game.result.away_score:
                        playoffTeams[count] = game.game.home
                    else:
                        playoffTeams[count] = game.game.away
                    count += 1

        nextWeek = maxWeek[1] + 1
        home = 1
        away = len(playoffTeams)
        while home < away:
            game = Game(playoffTeams[home], playoffTeams[away])
            db.session.add(game)
            schedule = Schedule(nextWeek, gameType, game)
            db.session.add(schedule)
            away = away - 1
            home = home + 1

        db.session.commit()
