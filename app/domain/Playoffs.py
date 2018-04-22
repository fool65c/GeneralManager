from app.domain.Conference import Conference
from app.domain.Playoff import Playoff
from app.server import query
from app.server import db
from itertools import groupby


class Playoffs(object):
    def __init__(self):
        self.playoffs = {}
        self.nextRound = 1
        playoffs = query(Playoff).all()
        playoffs = sorted(playoffs, key=lambda p: p.playoff_round)
        for pRound, teams in groupby(playoffs, lambda p: p.playoff_round):
            self.playoffs[pRound] = {}
            self.nextRound = pRound
            teams = sorted(teams, key=lambda p: p.conf.name)
            for conf, pTeams in groupby(teams, lambda p: p.conf.name):
                self.playoffs[pRound][conf] = sorted(pTeams,
                                                     key=lambda p: p.rank)

    def playNextRound(self):
        for conf, playoffs in self.playoffs[self.nextRound].items():
            for playoff in playoffs:
                if playoff.game is not None and playoff.result is None:
                    result = playoff.game.play()
                    game = playoff.game
                    if result.home_score > result.away_score:
                        game.home.wins += 1
                        game.away.losses += 1
                    else:
                        game.away.wins += 1
                        game.home.losses += 1
                    game.home.points_for += result.home_score
                    game.home.points_against += result.away_score
                    game.away.points_for += result.away_score
                    game.away.points_against += result.home_score

                    # set the results for all playoff teams
                    playoff.result = result
                    for opp in playoffs:
                        if (playoff.id != opp.id and
                           playoff.game_id == opp.game_id):
                            opp.result = result
                    db.session.commit()

    def toJSON(self):
        results = {
            "teams": [],
            "results": []
        }

        if 1 not in self.playoffs:
            return results

        confs = []
        for conf in query(Conference).all():
            confs.append(conf.name)

        results['teams'].append([self.playoffs[1][confs[0]][0].team.city,
                                 None])
        results['teams'].append([self.playoffs[1][confs[0]][3].team.city,
                                 self.playoffs[1][confs[0]][4].team.city])
        results['teams'].append([self.playoffs[1][confs[0]][2].team.city,
                                 self.playoffs[1][confs[0]][5].team.city])
        results['teams'].append([self.playoffs[1][confs[0]][1].team.city,
                                 None])
        results['teams'].append([self.playoffs[1][confs[1]][0].team.city,
                                 None])
        results['teams'].append([self.playoffs[1][confs[1]][3].team.city,
                                 self.playoffs[1][confs[1]][4].team.city])
        results['teams'].append([self.playoffs[1][confs[1]][2].team.city,
                                 self.playoffs[1][confs[1]][5].team.city])
        results['teams'].append([self.playoffs[1][confs[1]][1].team.city,
                                 None])

        for pRound in self.playoffs:
            weekResults = []
            for conf, playoff in self.playoffs[pRound].items():
                if pRound == 1:
                    weekResults.append([None, None])
                    game4v5 = playoff[3].result
                    if game4v5 is None:
                        weekResults.append([None, None])
                    else:
                        weekResults.append([game4v5.home_score,
                                            game4v5.away_score])
                    game3v6 = playoff[2].result
                    if game3v6 is None:
                        weekResults.append([None, None])
                    else:
                        weekResults.append([game3v6.home_score,
                                            game3v6.away_score])
                    weekResults.append([None, None])
                if pRound == 2:
                    for game in [0, 1]:
                        result = playoff[game].result
                        if result is None:
                            weekResults.append([None, None])
                        else:
                            weekResults.append([result.home_score,
                                                result.away_score])
                if pRound == 3:
                    result = playoff[0].result
                    if result is None:
                        weekResults.append([None, None])
                    else:
                        weekResults.append([result.home_score,
                                            result.away_score])
            if pRound == 4:
                result = self.playoffs[pRound][confs[0]][0].result
                if result is None:
                    weekResults.append([None, None])
                else:
                    weekResults.append([result.home_score, result.away_score])
            results['results'].append(weekResults)
        print(results)
        return results
