from pathlib import Path
from app.server import app, api
from app.resources.TeamResource import TeamResource
from app.resources.TeamResource import TeamsResource
from app.resources.ScheduleResource import GetTeamRegularSeasonResource
from app.resources.ScheduleResource import GetRegularSeasonResource
from app.resources.ScheduleResource import PlayNextWeekResource
from app.resources.ScheduleResource import PlayRegularSeasonResource
from app.resources.ScheduleResource import GetNextWeekResource
from app.resources.ScheduleResource import GetLastWeekResource
from app.resources.RankingsResource import RankingResource
from app.resources.RankingsResource import DivisionRankingResource
from app.resources.PlayoffResource import PlayoffsNextWeekResource
from app.resources.PlayoffResource import GetPlayoffScheduleResource
from app.resources.StateResource import GetPhasesResource
from app.resources.StateResource import GetGameState


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    print("app/static/{}".format(path))
    if Path("app/static/{}".format(path)).is_file():
        return app.send_static_file(path)
    else:
        return app.send_static_file('index.html')


api.add_resource(TeamResource, '/api/team/<team_id>')
api.add_resource(TeamsResource, '/api/team')

api.add_resource(GetRegularSeasonResource, '/api/schedule')
api.add_resource(GetTeamRegularSeasonResource, '/api/schedule/<team_id>')
api.add_resource(PlayRegularSeasonResource, '/api/schedule/play')
api.add_resource(GetNextWeekResource, '/api/schedule/nextWeek/<team_id>')
api.add_resource(GetLastWeekResource, '/api/schedule/lastWeek/<team_id>')
api.add_resource(PlayNextWeekResource, '/api/schedule/nextWeek/play')

api.add_resource(GetPlayoffScheduleResource, '/api/playoff')
api.add_resource(PlayoffsNextWeekResource, '/api/playoff/play')

api.add_resource(RankingResource, '/api/rankings')
api.add_resource(DivisionRankingResource, '/api/rankings/division')

api.add_resource(GetGameState, '/api/state')
api.add_resource(GetPhasesResource, '/api/state/phase')
