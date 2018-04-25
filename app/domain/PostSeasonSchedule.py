from app.domain.Game import Game
from app.domain.Playoff import Playoff
from app.domain.Playoffs import Playoffs
from app.domain.Standings import Standings
from app.domain.Conference import Conference
from app.server import db
from app.server import query


class PostSeasonSchedule(object):
    def advancePostSeasonSchedule(self):
        standings = Standings().standings

        playoffs = Playoffs().playoffs
        if 1 not in playoffs:
            self.__createPostSeasonSchedule(standings)
            return

        currentRound = max(list(playoffs.keys()))
        if currentRound == 1:
            for conf in query(Conference).all():
                # get result from 3 vs 6
                game1 = playoffs[currentRound][conf.name][2].game
                result1 = playoffs[currentRound][conf.name][2].result
                print(playoffs[currentRound][conf.name][2].rank)
                game1Winner = None
                if result1.home_score > result1.away_score:
                    game1Winner = game1.home
                else:
                    game1Winner = game1.away
                game = Game(playoffs[currentRound][conf.name][1].team,
                            game1Winner)
                db.session.add(game)
                playoff = Playoff(conf,
                                  playoffs[currentRound][conf.name][1].team,
                                  2, 2, game)
                db.session.add(playoff)
                playoff = Playoff(conf, game1Winner, 2, 3, game)
                db.session.add(playoff)

                # get result form 4 vs 5
                game2 = playoffs[currentRound][conf.name][3].game
                result2 = playoffs[currentRound][conf.name][3].result
                game2Winner = None
                if result2.home_score > result2.away_score:
                    game2Winner = game2.home
                else:
                    game2Winner = game2.away
                game = Game(playoffs[currentRound][conf.name][0].team,
                            game2Winner)
                db.session.add(game)
                playoff = Playoff(conf,
                                  playoffs[currentRound][conf.name][0].team,
                                  2, 1, game)
                db.session.add(playoff)
                playoff = Playoff(conf, game2Winner, 2, 4, game)
                db.session.add(playoff)
        if currentRound == 2:
            for conf in query(Conference).all():
                # get result from 1 vs 4
                game1 = playoffs[currentRound][conf.name][0].game
                result1 = playoffs[currentRound][conf.name][0].result
                game1Winner = None
                if result1.home_score > result1.away_score:
                    game1Winner = game1.home
                else:
                    game1Winner = game1.away
                # get result form 2 vs 3
                game2 = playoffs[currentRound][conf.name][1].game
                result2 = playoffs[currentRound][conf.name][1].result
                game2Winner = None
                if result2.home_score > result2.away_score:
                    game2Winner = game2.home
                else:
                    game2Winner = game2.away
                game = Game(game1Winner, game2Winner)
                db.session.add(game)
                playoff = Playoff(conf, game1Winner, 3, 1, game)
                db.session.add(playoff)
                playoff = Playoff(conf, game2Winner, 3, 2, game)
                db.session.add(playoff)
        if currentRound == 3:
            championship = {}
            for conf in query(Conference).all():
                championship[conf.name] = {
                    'conf': conf,
                    'team': None
                }
                for playoff in playoffs[currentRound][conf.name]:
                    # get result from 1 vs 2
                    game = playoffs[currentRound][conf.name][0].game
                    result = playoffs[currentRound][conf.name][0].result
                    gameWinner = None
                    if result.home_score > result.away_score:
                        gameWinner = game.home
                    else:
                        gameWinner = game.away
                    championship[conf.name]['team'] = gameWinner
            confs = list(championship.keys())
            homeConf = championship[confs[0]]['conf']
            homeTeam = championship[confs[0]]['team']
            awayConf = championship[confs[1]]['conf']
            awayTeam = championship[confs[1]]['team']
            game = Game(homeTeam, awayTeam)
            db.session.add(game)
            playoff = Playoff(homeConf, homeTeam, 4, 1, game)
            db.session.add(playoff)
            playoff = Playoff(awayConf, awayTeam, 4, 2, game)
            db.session.add(playoff)

        db.session.commit()

    def __createPostSeasonSchedule(self, standings):
        playoffTeams = {}
        wildCardTeams = {}
        for conf, divisions in standings.items():
            playoffTeams[conf] = []
            wildCardTeams[conf] = []
            for division, teams in divisions.items():
                for rank, team in teams.items():
                    if rank == 1:
                        playoffTeams[conf].append(team)
                    else:
                        wildCardTeams[conf].append(team)

            playoffTeams[conf] = sorted(playoffTeams[conf],
                                        key=lambda x: x.points_against)
            playoffTeams[conf] = sorted(playoffTeams[conf],
                                        key=lambda x: x.points_for,
                                        reverse=True)
            playoffTeams[conf] = sorted(playoffTeams[conf],
                                        key=lambda x: x.wins, reverse=True)
            for r, t in enumerate(playoffTeams[conf]):
                print("KMAGER0",r,t.city,t.wins)

            wildCardTeams[conf] = sorted(wildCardTeams[conf],
                                         key=lambda x: x.points_against)
            wildCardTeams[conf] = sorted(wildCardTeams[conf],
                                         key=lambda x: x.points_for,
                                         reverse=True)
            wildCardTeams[conf] = sorted(wildCardTeams[conf],
                                         key=lambda x: x.wins, reverse=True)
            for r, t in enumerate(wildCardTeams[conf]):
                print("KMAGER1", r,t.city,t.wins)

        for conf in query(Conference).all():
            # team rank 1 gets a bye
            playoff = Playoff(conf, playoffTeams[conf.name][0], 1, 1, None)
            db.session.add(playoff)
            # team rank 2 gets a bye
            playoff = Playoff(conf, playoffTeams[conf.name][1], 1, 2, None)
            db.session.add(playoff)
            # team rank 4 plays rank 5
            game = Game(playoffTeams[conf.name][3],
                        wildCardTeams[conf.name][0])
            db.session.add(game)
            playoff = Playoff(conf, playoffTeams[conf.name][3], 1, 4, game)
            db.session.add(playoff)
            playoff = Playoff(conf, wildCardTeams[conf.name][0], 1, 5, game)
            db.session.add(playoff)
            # team rank 3 plays rank 6
            game = Game(playoffTeams[conf.name][3],
                        wildCardTeams[conf.name][1])
            db.session.add(game)
            playoff = Playoff(conf, playoffTeams[conf.name][2], 1, 3, game)
            db.session.add(playoff)
            playoff = Playoff(conf, wildCardTeams[conf.name][1], 1, 6, game)
            db.session.add(playoff)

        db.session.commit()
