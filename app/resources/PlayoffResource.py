from flask_restful import Resource
from app.domain.PostSeasonSchedule import PostSeasonSchedule
from app.domain.Playoffs import Playoffs


class GetPlayoffScheduleResource(Resource):
    def get(self):
        return Playoffs().toJSON()


class PlayoffsNextWeekResource(Resource):
    def get(self):
        playoffs = Playoffs()
        playoffs.playNextRound()

        postSeason = PostSeasonSchedule()
        postSeason.advancePostSeasonSchedule()

        return Playoffs().toJSON()
