from app.controller.StateController import VerifyState
from app.domain.league.Team import Team
from app.domain.State import State
from app.domain.roster.Roster import Roster
from app.domain.formations.proOffense import proOffense
from app.domain.formations.Defense44 import Defense44
from app.domain.formations.SpecialTeams import SpecialTeams
from app.server import query
from app.server import db


def SetTeam(team_id):
    team = query(Team).filter_by(id=team_id).first()

    if team is None:
        return "Not Found", 404

    state = query(State).first()
    print(state.toJSON())
    state.setTeam(team)

    Roster.assignPlayers(team)
    setStarters(team)
    db.session.commit()

    VerifyState(state)

    return team.toJSON()


def setStarters(team):
    roster = Roster(team.id)

    offense = proOffense()
    defense = Defense44()
    specialTeams = SpecialTeams()

    offense.setStarters(roster)
    defense.setStarters(roster)
    specialTeams.setStarters(roster)

    team.offense = offense.rating / 20
    team.defense = defense.rating / 20
    team.special_teams = specialTeams.rating / 20
