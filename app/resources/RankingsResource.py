from flask_restful import Resource
from app.domain.schedule.Standings import Standings


class RankingResource(Resource):
    def get(self):
        return Standings().toJSON()


class DivisionRankingResource(Resource):
    def get(self):
        standings = Standings()
        standings.newHotness()
        return standings.toJSON2()
