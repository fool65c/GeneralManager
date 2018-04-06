from flask_restful import Resource
from app.domain.Phase import Phase
from app.domain.State import State
from app.controller.StateController import VerifyState
from app.server import query


class GetPhasesResource(Resource):
    def get(self):
        phases = query(Phase).all()
        return [phase.toJSON() for phase in phases]


class GetGameState(Resource):
    def get(self):
        state = query(State).first()
        state = VerifyState(state)
        return state.toJSON()
