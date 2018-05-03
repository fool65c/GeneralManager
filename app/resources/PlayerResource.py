from flask_restful import Resource
from app.domain.State import State
from app.domain.roster.Player import Player
from app.server import query
from app.server import db


class RetireResource(Resource):
    def get(self):
        retiringPlayers = []
        state = query(State).first()
        if state.phase.phase != 'STARTOFFSEASON':
            return "Can not retire players unless the season is over", 400

        players = query(Player).all()
        for player in players:
            if player.willPlayerRetire():
                retiringPlayers.append(player.toJSON())
                db.session.delete(player)

        state.advancePhase()
        db.session.commit()

        return retiringPlayers
