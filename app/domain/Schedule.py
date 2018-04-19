from app.domain import Base
from sqlalchemy import Integer
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import func
from app.domain.Game import Game
from app.domain.Standings import Standings
from app.domain.GameType import GameType
from app.domain.Result import Result
from app.server import db
from app.server import query


class Schedule(Base):
    __tablename__ = 'schedule'
    id = Column(Integer, primary_key=True)
    week = Column(Integer, nullable=False)
    game_type_id = Column(Integer, ForeignKey("game_type.id"), nullable=False)
    game_id = Column(Integer, ForeignKey("game.id"), nullable=False)
    result_id = Column(Integer, ForeignKey("result.id"), nullable=True)
    game_type = relationship("GameType", foreign_keys=[game_type_id])
    game = relationship("Game", foreign_keys=[game_id])
    result = relationship(Result, foreign_keys=[result_id])

    def __init__(self, week, game_type, game, result=None):
        self.week = week
        self.game_type = game_type
        self.game = game
        self.result = result

    def toJSON(self):
        results = {}
        results['id'] = self.id
        results['week'] = self.week
        results['game_type'] = self.game_type.toJSON()
        results['game'] = self.game.toJSON()

        if self.result is None:
            results['result'] = self.result
        else:
            results['result'] = self.result.toJSON()
        return results

    def play(self):
        if self.result is None:
            self.result = self.game.play()
            if self.result.home_score > self.result.away_score:
                self.game.home.wins += 1
                self.game.away.losses += 1
            else:
                self.game.away.wins += 1
                self.game.home.losses += 1

            self.game.home.points_for += self.result.home_score
            self.game.home.points_against += self.result.away_score
            self.game.away.points_for += self.result.away_score
            self.game.away.points_against += self.result.home_score

            db.session.commit()


class CreatePostSeasonSchedule(object):
    def __init__(self):
        self.regular_season_weeks = 16
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
