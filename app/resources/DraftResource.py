from flask import request
from flask_restful import Resource
from itertools import groupby
from app.domain.State import State
from app.domain.draft.DraftPick import DraftPick
from app.domain.roster.Player import Player
from app.domain.roster.TeamToPlayer import TeamToPlayer
from app.controller.PlayerController import retiringPlayers
from app.controller.PlayerController import generateFreeAgents
from app.server import query
from app.server import db


class DraftPickResource(Resource):
    def get(self):
        state = query(State).first()
        if state.phase.phase != 'DRAFT':
            return "Can not draft players now", 400
        draftData = {}
        draftPicks = query(DraftPick).order_by(DraftPick.overall_pick).all()
        for r, pick in groupby(draftPicks, key=lambda x: x.round):
            draftData[r] = [p.toJSON() for p in pick]
        return draftData
