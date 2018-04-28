from app.controller.StateController import VerifyState
from app.domain.Team import Team
from app.domain.State import State
from app.domain.roster.Roster import Roster
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

    db.session.commit()

    VerifyState(state)

    return team.toJSON()
