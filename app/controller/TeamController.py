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
    setStarters(team)
    db.session.commit()

    VerifyState(state)

    return team.toJSON()


def setStarters(team):
    roster = Roster(team.id)
    formations = {
        'offensiveFormation': {
            'QB': 1,
            'RB': 2,
            "WR": 2,
            "TE": 1,
            "OL": 5
        },
        'defensiveFormation': {
            'DL': 4,
            'LB': 4,
            'DB': 3
        },
        'specialTeamsFormation': {
            'K': 1,
            'P': 1
        }
    }

    starters = {}

    for formation, positions in formations.items():
        starters[formation] = {
            'rating': 0
        }
        for position, count in positions.items():
            currentStarters = 0
            starters[formation][position] = 0
            for player in roster.getPositionBySkill(position):
                if currentStarters < count:
                    player.starter = True
                    starters[formation][position] += player.player\
                                                           .getOverallLevel()
                else:
                    player.starter = False
                currentStarters += 1

    for formation in formations:
        for position in formations[formation]:
            starters[formation]['rating'] += (starters[formation][position]
                                              / formations[formation]
                                              [position])

    team.offense = starters['offensiveFormation']['rating'] / 20
    team.defense = starters['defensiveFormation']['rating'] / 20
    team.special_teams = starters['specialTeamsFormation']['rating'] / 20

    print(starters)
