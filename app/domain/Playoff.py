from app.domain.Schedule import Schedule
from app.domain.GameType import GameType
from app.server import query
from sqlalchemy import func


class Playoff(object):
    def __init__(self):
        self.playoffs = []
        gT = query(GameType).filter_by(game_type="post season").first()

        firstWeek = query(Schedule,
                          func.min(Schedule.week)).filter_by(game_type=gT) \
                                                  .first()[1]
        playoffWeek = firstWeek
        while True:
            games = query(Schedule).filter_by(game_type=gT) \
                                    .filter_by(week=playoffWeek) \
                                    .all()
            if len(games) == 0:
                break

            self.playoffs.append([games])
            playoffWeek += 1

    def toJSON(self):
        results = {
            "teams": [],
            "results": []
        }

        for games in self.playoffs[0]:
            for game in games:
                results["teams"].append([game.game.home.city,
                                         game.game.away.city])

        for playoffWeek in self.playoffs:
            weekResults = []
            for games in playoffWeek:
                for game in games:
                    if game.result is None:
                        weekResults.append([])
                    else:
                        weekResults.append([game.result.home_score,
                                            game.result.away_score])
            results["results"].append(weekResults)

        return results
