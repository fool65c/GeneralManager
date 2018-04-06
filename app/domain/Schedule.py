from app.domain import Base
from sqlalchemy import Integer
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import func
from app.domain.Game import Game
from app.domain.Conference import Conference
from app.domain.Division import Division
from app.domain.Team import Team
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


class CreateSchedule(object):
    def __init__(self):
        self.regular_season_weeks = 16
        self.post_season_teams = 8

    def __newSchedule(self):
        self.regular_season_weeks = 17

        self.regular_season_weeks = 16

    def createRegularSeasonSchedule(self, teams=None):
        if query(Schedule).count() != 0:
            return

        gameType = query(GameType).filter_by(game_type="regular season") \
                                  .first()

        # 17 week season, 16 games
        # first 3 game division
        # last 3 games division
        # 4 bye weeks per week starting week 5
        # 4 games vs another division in conference 2 home 2 away
        # 4 games vs another division not in conference 2 home 2 away
        # 2 games vs ranked (not in above) one at home 1 on the road

        # for team add opponents 
            # 5 catagories
            # home, away, tossup
            # 3 home, 3 away, 10 tossup, 1 bye week NONE, weeks open (range 1, 18)

        # start with one team
            # move half tossup into home half away
            # make sure other team is balanced
            # adjust other 10 teams
            # add bye week

        # TODO CHANGE RANKINGS TO HAVE FULL DOMAIN CLASSES
        # go through each division
            # week 15 1 3, home 2, 4 away
            # week 16 2, 4 home 1, 3 away
            # week 17 3, 1 home, 2, 4 away
            # foreach week choice 1, 5 to reverse
                # if week alreay taken remove week and choice again

        # weeks 1 - 5
            # foreach team fill holes

        # weeks 6 - 14
            # first 4 teams get byes
            # foreach team fill holes
            # if week can't be filled
                # and team dosne't have a bye week yet
                # team bye week
                # if bye week already taken see if matchup is availiable on bye week
                    # swap
                # else
                    # cry



            # remove from opponents where approporate

        # weeks 1-5
            # 




        if teams is None:
            teams = query(Team).all()

        if len(teams) % 2 == 1 and len(teams):
            teams.append(None)

        count = len(teams)
        half = int(count / 2)

        for turn in range(self.regular_season_weeks):
            left = teams[:half]
            right = teams[count - half - 1 + 1:][::-1]
            pairings = zip(left, right)
            if turn % 2 == 1:
                pairings = [(y, x) for (x, y) in pairings]
            teams.insert(1, teams.pop())
            for pair in pairings:
                if pair[0] is None or pair[1] is None:
                    print("BYE WEEK SON")
                else:
                    game = Game(pair[0], pair[1])
                    db.session.add(game)
                    schedule = Schedule(turn + 1, gameType, game)
                    db.session.add(schedule)
        db.session.commit()

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
