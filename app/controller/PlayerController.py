from app.domain.roster.Player import Player
from app.domain.roster.Position import Position
from app.domain.roster.TeamToPlayer import TeamToPlayer
from app.domain.roster.PlayerGenerator import generatePlayer
from app.domain.roster.PlayerGenerator import getPositionDefaults
from random import choice
from app.server import query
from app.server import db


def getPlayersWithoutTeams():
    players = query(Player)
    teamPlayers = query(TeamToPlayer.player_id)
    return(players.filter(Player.id.notin_(teamPlayers)).all())


def retiringPlayers():
    retiringPlayers = []

    playersWithoutTeam = getPlayersWithoutTeams()
    # force players without a team to retire
    for player in playersWithoutTeam:
        if player.age > 27:
            retiringPlayers.append(player.toJSON())
            db.session.delete(player)
            query(TeamToPlayer).filter(TeamToPlayer.player_id == player.id).\
                delete(synchronize_session=False)

        if player.position_ability < 50:
            retiringPlayers.append(player.toJSON())
            db.session.delete(player)
            query(TeamToPlayer).filter(TeamToPlayer.player_id == player.id).\
                delete(synchronize_session=False)

    # players on the team but retiring
    players = query(Player).all()
    for player in players:
        if player.willPlayerRetire():
            retiringPlayers.append(player.toJSON())
            db.session.delete(player)
            query(TeamToPlayer).filter(TeamToPlayer.player_id == player.id).\
                delete(synchronize_session=False)

    return retiringPlayers


def generateFreeAgents():
    maxFreeAgents = 32
    freeAgents = getPlayersWithoutTeams()
    positions = query(Position).all()
    positionDefaults = getPositionDefaults()

    while len(freeAgents) < maxFreeAgents:
        position = choice(positions)
        freeAgent = generatePlayer(position, minAge=26,
                                   **positionDefaults[position.shortName]
                                   ['abilities'])
        db.session.add(freeAgent)
        freeAgents.append(freeAgent)

    return freeAgents
