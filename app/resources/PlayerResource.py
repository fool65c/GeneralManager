from flask_restful import Resource
from app.domain.State import State
from app.domain.roster.Player import Player
from app.domain.roster.Position import Position
from app.domain.roster.TeamToPlayer import TeamToPlayer
from app.domain.roster.PlayerGenerator import generatePlayer
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
