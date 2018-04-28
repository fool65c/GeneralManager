from itertools import groupby
from app.domain.roster.Player import Player
from app.domain.roster.TeamToPlayer import TeamToPlayer
from app.server import db
from app.server import query


class Roster:
    def __init__(self, team_id):
        self.roster = query(TeamToPlayer).filter_by(team_id=team_id).all()

    def toJSON(self):
        roster = {}
        for status, allPlayers in groupby(self.roster, lambda p: p.starter):
            statusText = None
            if status:
                statusText = "Starter"
            else:
                statusText = "Bench"
            if statusText not in roster:
                roster[statusText] = {}

            for position, players in groupby(allPlayers,
                                             lambda p:
                                             p.player.position.shortName
                                             ):
                players = sorted(players,
                                 key=lambda p: (p.player.getOffensiveWeight()
                                                + p.player.getDefensiveWeight()
                                                + (p.player
                                                   .getSpecialTeamsWeight())
                                                ),
                                 reverse=True)
                roster[statusText][position] = [p.player.toJSON()
                                                for p in players]
        return roster

    @staticmethod
    def assignPlayers(team):
        for player in query(Player).all():
            ttp = TeamToPlayer(player, team, False)
            db.session.add(ttp)
        db.session.commit()
