from app.controller.ScheduleController import CreateScheduleController
from app.controller.ScheduleController import CreatePlayoffsController
from app.controller.OffseasonController import OffseasonController
from app.controller.OffseasonController import PrepRankingsController
from app.domain.Phase import Phase
from app.domain.Standings import Standings
from app.domain.Schedule import Schedule
from app.domain.State import State
from app.server import query
from app.server import db


def VerifyState(state):
    gamesLeft = query(Schedule).filter_by(result=None).all()

    if state is None:
        newGamePhase = query(Phase).filter_by(phase="NEWGAME").first()
        state = State(newGamePhase, None)
        db.session.add(state)
        db.session.commit()
    elif state.team is not None and state.phase.phase == "GENERATE_SCHEDULE":
        state = CreateScheduleController()
    elif len(gamesLeft) == 0 and state.phase.phase == "REGULARSEASON":
        state.advancePhase()
        db.session.commit()
        state = CreatePlayoffsController()
    elif len(gamesLeft) == 0 and state.phase.phase == "POSTSEASON":
        state.advancePhase()
        OffseasonController()
        db.session.commit()
    elif state.phase.phase == "OFFSEASON":
        startOver = query(Phase).filter_by(phase="GENERATE_SCHEDULE").first()
        teams = PrepRankingsController(Standings())
        state.phase = startOver
        db.session.commit()
        state = CreateScheduleController(teams)
    return state
