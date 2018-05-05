from flask_restful import Resource
from app.domain.formations.proOffense import proOffense
from app.domain.formations.Defense44 import Defense44
from app.domain.formations.SpecialTeams import SpecialTeams


class FormationResource(Resource):
    def get(self):
        formations = {
            'offense': proOffense().positions,
            'defense': Defense44().positions,
            'special_teams': SpecialTeams().positions
        }

        return formations
