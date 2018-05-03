from flask import request
from flask_restful import Resource
from app.controller.TeamController import SetTeam
from app.domain.league.Team import Team
from app.domain.roster.Roster import Roster
from app.server import query


class TeamResource(Resource):
    def get(self, team_id):
        team = query(Team).filter_by(id=team_id).first()
        if team is None:
            return 404, 404
        else:
            return team.toJSON()


class TeamRosterResource(Resource):
    def get(self, team_id):
        team = query(Team).filter_by(id=team_id).first()
        if team is None:
            return 404, 404
        else:
            return Roster(team_id).toJSON()


class TeamsResource(Resource):
    def get(self):
        teams = query(Team).all()
        return [team.toJSON() for team in teams]

    def post(self):
        json_data = request.get_json(force=True)
        team_id = json_data['team_id']

        return SetTeam(team_id)
