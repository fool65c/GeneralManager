from flask_restful import Resource
from app.domain.Schedule import Schedule
from app.server import query
from sqlalchemy import func


class PlayNextWeekResource(Resource):
    def get(self):
        maxWeek = query(Schedule,
                        func.min(Schedule.week)) \
                        .filter_by(result=None).first()
        nextWeek = maxWeek[1]
        if nextWeek is None:
            return []

        games = query(Schedule).filter_by(week=nextWeek).all()

        for game in games:
            game.play()

        games = query(Schedule).filter_by(week=nextWeek).all()
        return [game.toJSON() for game in games]


class GetNextWeekResource(Resource):
    def get(self, team_id):
        team_id = int(team_id)
        maxWeek = query(Schedule,
                        func.min(Schedule.week)) \
                        .filter_by(result=None).first()
        nextWeek = maxWeek[1]

        if nextWeek is None:
            return "Regular Season is Over", 200

        games = query(Schedule).filter_by(week=nextWeek).all()

        nextGame = None
        for game in games:
            if game.game.home_id == team_id or game.game.away_id == team_id:
                nextGame = game

        if nextGame is None:
            return "Bye Week", 200

        return nextGame.toJSON()


class GetLastWeekResource(Resource):
    def get(self, team_id):
        team_id = int(team_id)
        tmpWeek = query(Schedule,
                        func.min(Schedule.week)).filter_by(result=None).first()

        lastWeek = 0
        # subtract a week for last weeks results
        if tmpWeek[0] is None:
            tmpWeek = query(Schedule,
                            func.max(Schedule.week)).first()
            lastWeek = tmpWeek[1]
        else:
            lastWeek = int(tmpWeek[1])
            if lastWeek == 1:
                # season hasn't started
                return "Season not started", 200
            lastWeek = lastWeek - 1

        games = query(Schedule).filter_by(week=lastWeek).all()

        lastGame = None
        for game in games:
            if game.game.home_id == team_id or game.game.away_id == team_id:
                lastGame = game

        if lastGame is None:
            return "Bye Week", 200

        return lastGame.toJSON()


class PlayRegularSeasonResource(Resource):
    def get(self):
        games = query(Schedule).all()
        for game in games:
            game.play()

        games = query(Schedule).all()
        return [game.toJSON() for game in games]


class GetRegularSeasonResource(Resource):
    def get(self):
        schedule = query(Schedule).all()
        return [game.toJSON() for game in schedule]
