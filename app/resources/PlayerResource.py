from flask_restful import Resource
from app.domain.State import State
from app.controller.PlayerController import retiringPlayers
from app.controller.PlayerController import generateFreeAgents
from app.server import query
from app.server import db


class RetireResource(Resource):
    def get(self):
        state = query(State).first()
        if state.phase.phase != 'STARTOFFSEASON':
            return "Can not retire players unless the season is over", 400

        players = retiringPlayers()

        state.advancePhase()
        db.session.commit()

        return players


class FreeAgentsResource(Resource):
    def get(self):
        freeAgents = generateFreeAgents()
        db.session.commit()
        return [player.toJSON() for player in freeAgents]
