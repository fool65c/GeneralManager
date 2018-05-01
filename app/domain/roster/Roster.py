from itertools import groupby
from app.domain.roster.Player import Player
from app.domain.roster.TeamToPlayer import TeamToPlayer
from app.server import db
from app.server import query


class Roster:
    def __init__(self, team_id):
        self.roster = query(TeamToPlayer).filter_by(team_id=team_id).all()

    def toJSON(self):
        return [ { **p.player.toJSON(), "starter": p.starter} for p in self.roster]

    def getPositionBySkill(self, position):
        players = list(filter(lambda p: p.player.position.shortName == position, self.roster))
        return sorted(players, key=lambda p: p.player.getOverallLevel(), reverse=True)

    @staticmethod
    def assignPlayers(team):
        for player in query(Player).all():
            ttp = TeamToPlayer(player, team, False)
            db.session.add(ttp)
        db.session.commit()
