from flask_restful import Resource
from app.domain.Schedule import Schedule
from app.domain.PostSeasonSchedule import PostSeasonSchedule
from app.domain.Playoff import Playoff
from app.domain.GameType import GameType
from app.server import query
from sqlalchemy import func


class GetPlayoffScheduleResource(Resource):
    def get(self):
        return Playoff().toJSON()


class PlayoffsNextWeekResource(Resource):
    def get(self):
        gT = query(GameType).filter_by(game_type="post season").first()
        maxWeek = query(Schedule, func.min(Schedule.week)) \
                        .filter_by(result=None) \
                        .filter_by(game_type=gT).first()
        nextWeek = maxWeek[1]
        games = query(Schedule).filter_by(week=nextWeek).all()

        for game in games:
            game.play()

        postSeason = PostSeasonSchedule()
        postSeason.advancePostSeasonSchedule()

        return Playoff().toJSON()
