from app.domain.roster.Player import Player
from app.domain.roster.Position import Position
from app.domain.roster.TeamToPlayer import TeamToPlayer
from app.domain.roster.PlayerGenerator import generatePlayer
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

        if player.position_ability < 50:
            retiringPlayers.append(player.toJSON())
            db.session.delete(player)

    # players on the team but retiring
    players = query(Player).all()
    for player in players:
        if player.willPlayerRetire():
            retiringPlayers.append(player.toJSON())
            db.session.delete(player)

    return retiringPlayers


def generateFreeAgents():
    maxFreeAgents = 20
    freeAgents = getPlayersWithoutTeams()
    positions = query(Position).all()

    while len(freeAgents) < maxFreeAgents:
        position = choice(positions)
        freeAgent = generatePlayer(position)
        db.session.add(freeAgent)
        freeAgents.append(freeAgent)

    return freeAgents
