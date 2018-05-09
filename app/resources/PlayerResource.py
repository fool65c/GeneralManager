from flask import request
from flask_restful import Resource
from app.domain.State import State
from app.domain.roster.Player import Player
from app.domain.roster.TeamToPlayer import TeamToPlayer
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
        state = query(State).first()
        if state.phase.phase != 'FREEAGENCY':
            return "Can not sign free agents until the season is over", 400

        freeAgents = generateFreeAgents()
        db.session.commit()
        return [player.toJSON() for player in freeAgents]

    def post(self):
        json_data = request.get_json(force=True)
        state = query(State).first()
        if state.phase.phase != 'FREEAGENCY':
            return "Can not sign free agents until the season is over", 400

        for playerId in json_data:
            print(playerId)
            ttp = query(TeamToPlayer).filter_by(player_id=playerId).first()
            player = query(Player).filter_by(id=playerId).first()
            if ttp is None:
                print("adding ttp")
                teamToPlayer = TeamToPlayer(player, state.team, False)
                db.session.add(teamToPlayer)
            else:
                ttp.team = state.team

        state.advancePhase()
        db.session.commit()

        return 200, 200
