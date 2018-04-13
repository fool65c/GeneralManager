from app.domain.Game import Game
# from app.domain.Conference import Conference
# from app.domain.Division import Division
from app.domain.Team import Team
from app.domain.Standings import Standings
from app.domain.Season import Season
from app.domain.Schedule import Schedule
from app.domain.GameType import GameType
from app.server import db
from app.server import query
from sqlalchemy import func
from sqlalchemy import or_
from random import choice, sample
import copy


class CreateSchedule(object):
    def __init__(self):
        self.regular_season_weeks = 17
        self.number_of_bye_weeks = 2
        self.post_season_teams = 12
        self.matchups = {}
        self.season = query(Season, func.max(Season.id)).first()[0]
        standings = Standings()
        self.standings = standings.standings
        self.schedule = {}
        self.__init_matchups()
        self.teams = {t.id: t for t in query(Team).all()}

    def __init_matchups(self):
        for conf, divisions in self.standings.items():
            print("matchups init for {}".format(conf))
            for div, teams in divisions.items():
                print("matchups init for {}-{}".format(conf, div))
                for team in teams.values():
                    print("matchups init for {}".format(team.city))
                    self.matchups[team.id] = {
                        'team': team,
                        'interconf': {},
                        'divisionstart': {},
                        'divisionend': {},
                        'rank': {},
                        'intraconf': {}
                    }

    def createRegularSeasonSchedule(self):
        # 17 week season, 16 games
        # first 3 division game in first 5 weeks
        # last 3 games division
        # 1 bye week per team starting week 7 ending week 14
        # 4 games vs another division in conference 2 home 2 away
        # 4 games vs another division not in conference 2 home 2 away
        # 2 games vs ranked (not in above) one at home 1 on the road
        if query(Schedule).count() != 0:
            return

        # intra conference matchups
        teamMatchups = self.__intra_conference_matchups()
        # set intra-division
        self.__set_home_away(teamMatchups, 'intraconf', 2)
        # set rank
        self.__set_home_away(teamMatchups, 'rank', 1)

        # inter conference matchups
        teamMatchups = self.__inter_conference_matchups()
        self.__set_home_away(teamMatchups, 'interconf', 2)

        # division matchups
        teamMatchups = self.__division_matchups()
        self.__set_home_away(teamMatchups, 'divisionstart', 2)
        self.__flip_flop_divisional_games('divisionstart', 'divisionend')

        # commit all the games
        db.session.commit()

        # schedule the games
        # self.__conference_schedule_games('rank', [1], 4)
        # self.__conference_schedule_games('divisionstart', [1], 4)
        # self.__conference_schedule_games('rank', [1], 4)
        # self.__conference_schedule_games('rank', [1, 4, 11, 12], 4)
        self.__rename_schedule_games()

    def __rename_schedule_games(self):
        for conf, divisions in self.standings.items():
            print(conf)
            division = choice(list(divisions.keys()))
            print(division)
            team = choice(divisions[division])
            print(team)
        # Div1 pick one game from random division
        # remaining teams must play rank games one vs another division (div2) and one vs  (div3)
        # div2 2 plays one game vs div 4, div 3 plays one game vs div 4
        # div2,3,4 remaining 
        # intra(div4)
        # div2 remaining teams play conference
        # division not played 




    def __conference_schedule_games(self, gameType, weeks, numGames):
        for conf, divisions in self.standings.items():
            print(conf)
            for week in weeks:
                print("week: {}".format(week))
                if week not in self.schedule:
                    self.schedule[week] = {
                        conf: set(),
                        'games': []
                    }
                if conf not in self.schedule[week]:
                    self.schedule[week][conf] = set()

                for division, teams in divisions.items():
                    teamGamesLeft = {}
                    maxGamesLeft = 0
                    possibleGame = None
                    for t in teams.values():
                        for game in self.matchups[t.id][gameType]:
                            # add teams to the counter
                            print("trying {} at {}".format(game.home.city,
                                                           game.away.city))
                            if game.home.id not in teamGamesLeft:
                                teamGamesLeft[game.home.id] = 1
                            else:
                                teamGamesLeft[game.home.id] += 1
                            if game.away.id not in teamGamesLeft:
                                teamGamesLeft[game.away.id] = 1
                            else:
                                teamGamesLeft[game.away.id] += 1

                            if (game.home.id in self.schedule[week][conf] or
                               game.away.id in self.schedule[week][conf]):
                                print("tossing {} at {}".format(game.away.city,
                                                                game.home.city))
                            else:
                                if teamGamesLeft[game.home.id] > maxGamesLeft:
                                    possibleGame = game
                                    maxGamesLeft = teamGamesLeft[game.home.id]
                                else:
                                    possibleGame = game
                                if (teamGamesLeft[game.away.id] > maxGamesLeft and
                                   teamGamesLeft[game.away.id] > teamGamesLeft[game.home.id]):
                                    possibleGame = game
                                    maxGamesLeft = teamGamesLeft[game.home.id]


                    # choose one game for the division
                    game = possibleGame
                    # add it to the schedule
                    self.schedule[week][conf].add(game.home.id)
                    self.schedule[week][conf].add(game.away.id)
                    self.schedule[week]['games'].append(game)

                    # remove the game from matchups
                    for index, g in enumerate(self.matchups[game.home.id]
                                              [gameType]):
                        if g.id == game.id:
                            del self.matchups[game.home.id][gameType][index]
                            break

    def __unused(self):
        # week 1
        # one game from each division
        # teams not playing will play "Rank"
        # week 2
        # one game from each division
        # teams not playing will play "intra"
        # repeat week 2ish
        # week 4 swap rank and divisions ... infact just schedule this during week 1
        # week 5 

        # schedule the games
        self.__schedule_games(list(range(self.regular_season_weeks - 2,
                                         self.regular_season_weeks + 1)),
                              [
                                  'divisionend'
                              ])
        self.__schedule_games(list(range(1, 3)),
                              [
                                  'divisionstart'
                              ])
        self.__schedule_games(list(reversed(range(3,
                                         self.regular_season_weeks - 2))),
                              [
                                  'interconf',
                                  'rank',
                                  'intraconf'
                              ],4)

        # commit schedule
        db.session.commit()

        # see if there are any games left
        gamesLeft = []
        for team_id, source in self.matchups.items():
            for s in ['interconf', 'intraconf', 'rank',
                      'divisionstart', 'divisionend']:
                if len(source[s]) > 0:
                    gamesLeft.append(source[s])

        gamesLeft = {i.id: i for s in gamesLeft for i in s}
        gamesLeft = self.__cleanup_schedule(gamesLeft)
        # commit schedule
        db.session.commit()

        # try again because things changed
        gamesLeft = self.__cleanup_schedule(gamesLeft)
        # commit schedule
        db.session.commit()

    def __cleanup_schedule(self, totalGamesLeft):
        canNotPlace = {}
        # try to schedule teams that haven't been scheduled.
        gameType = query(GameType).filter_by(game_type="regular season") \
                                  .first()
        count = 0

        for game_id, game in totalGamesLeft.items():
            print(game.home.city, game.away.city)
            games = query(Game).filter(or_(Game.home_id == game.home.id,
                                           Game.away_id == game.home.id)) \
                               .all()
            gameIds = set([g.id for g in games])
            sched = query(Schedule).filter(Schedule.game_id.in_(gameIds)).all()
            hWeeksTaken = set([s.week for s in sched])

            games = query(Game).filter(or_(Game.home_id == game.away.id,
                                           Game.away_id == game.away.id)) \
                               .all()
            gameIds = set([g.id for g in games])
            sched = query(Schedule).filter(Schedule.game_id.in_(gameIds)).all()
            aWeeksTaken = set([s.week for s in sched])

            availWeeks = set(list(range(1, self.regular_season_weeks + 1)))
            hAvailWeeks = availWeeks - hWeeksTaken
            aAvailWeeks = availWeeks - aWeeksTaken
            availWeeks -= hWeeksTaken
            availWeeks -= aWeeksTaken

            # check to see if they overlop on some other week
            if len(availWeeks) > 0:
                print("Found {} weeks open".format(len(availWeeks)))
                week = sample(availWeeks, 1)[0]
                schedule = Schedule(week, gameType, game)
                print("Moving game to week {}".format(schedule.week))
                db.session.add(schedule)
                count += 1
                continue
            else:
                print("The teams don't have any open weeks that overlap")

            # check home opponents schedule for away teams openings
            freeWeek = self.__swap_games(game.home,
                                         hAvailWeeks,
                                         game.away,
                                         aAvailWeeks)
            if freeWeek is not None:
                schedule = Schedule(freeWeek, gameType, game)
                print("Moving game to week {}".format(schedule.week))
                db.session.add(schedule)
                count += 1
                continue
            else:
                print("Couldn't move games for {}".format(game.home.city))

            # check away opponents schedule for away teams openings
            freeWeek = self.__swap_games(game.away,
                                         aAvailWeeks,
                                         game.home,
                                         hAvailWeeks)
            if freeWeek is not None:
                schedule = Schedule(freeWeek, gameType, game)
                print("Moving game to week {}".format(schedule.week))
                db.session.add(schedule)
                count += 1
                continue
            else:
                print("Couldn't move games for {}".format(game.home.city))

            failText = "Couldn't find an open week for {} at {}"
            canNotPlace[game.id] = game
            print(failText.format(game.away.city, game.home.city))

        print("WE SCHEDULED {} of {}".format(count,
                                             len(totalGamesLeft)))
        return canNotPlace

    def __swap_games(self, team1, weeks1, team2, weeks2):
        # tried to move the games for team 1
        # will return week it made availiable
        freeWeek = None
        games = (query(Game)
                 .filter(or_(Game.home_id == team1.id,
                             Game.away_id == team1.id))
                 .filter(Schedule.week.in_(weeks2))
                 .filter(Schedule.game_id == Game.id)
                 .all())

        for game in games:
            opp_id = None
            if game.home.id != team1.id:
                opp_id = game.home.id
            else:
                opp_id = game.away.id

            oppGames = (query(Game)
                        .filter(or_(Game.home_id == opp_id,
                                    Game.away_id == opp_id))
                        .filter(Schedule.week.in_(weeks1))
                        .filter(Schedule.game_id == Game.id)
                        .all())
            # we have a winner!
            if len(oppGames) < len(weeks1):
                # remove all the take weeks
                for oppGame in oppGames:
                    tmp = query(Schedule).filter_by(game_id=oppGame.id).first()
                    weeks1.remove(tmp.week)

                # select the new week for the existing game
                newWeek = sample(weeks1, 1)[0]

                # select the existing games
                schedule = query(Schedule).filter_by(game_id=game.id).first()

                movingText = "Moving {} at {} form week {} to week {}"
                print(movingText.format(game.away.city,
                                        game.home.city,
                                        schedule.week,
                                        newWeek))
                freeWeek = schedule.week
                schedule.week = newWeek
                return freeWeek
        return freeWeek

    def __schedule_games(self, weeks, sources, byeWeekTeams=0):
        byeTeams = set()
        gameType = query(GameType).filter_by(game_type="regular season") \
                                  .first()

        games = {}
        # populate all possible games for the weeks
        # this may be more than the weeks allow and thats ok!
        for source in sources:
            for team_id in self.matchups:
                for game in self.matchups[team_id][source]:
                    games[game.id] = game

        # schedule the games
        for week in weeks:
            print("Scheduling week: {}".format(week))
            teams = copy.deepcopy(self.teams)

            # remove bye week teams
            possibleByeTeams = set(teams.keys())
            possibleByeTeams -= byeTeams
            if len(possibleByeTeams) >= byeWeekTeams:
                weekByes = set(sample(possibleByeTeams, byeWeekTeams))
                byeTeams = byeTeams | weekByes

                for id in weekByes:
                    del teams[id]

                if len(weekByes) > 0:
                    byeWeekText = "Week: {} teams with bye: {}"
                    print(byeWeekText.format(week, weekByes))

            while len(teams) > 0:
                game = self.__find_game(games, teams)

                if game is None:
                    noneText = "Can't schedule {} teams in Week {}"
                    print(noneText.format(len(teams), week))
                    game = self.__find_game(games, weekByes)
                    teams.clear()
                    continue
                # schedule the game
                print("Scheduling game: {}".format(game.id))
                print("Week {}: {} at {}".format(week,
                                                 game.away.city,
                                                 game.home.city))
                schedule = Schedule(week, gameType, game)
                db.session.add(schedule)

                # remove teams
                del teams[game.home.id]
                del teams[game.away.id]

                # remove the game
                del games[game.id]
                gameIndex = None
                gameSource = None
                for source in sources:
                    for index, g in enumerate(self.matchups[game.home.id]
                                              [source]):
                        if g.id == game.id:
                            gameIndex = index
                            gameSource = source
                            break

                if gameIndex is None:
                    raise Exception("Can not find game", "oh no")

                # remove the game
                del self.matchups[game.home.id][gameSource][gameIndex]
        print("Games not Scheduled: {}".format(len(games)))

    def __find_game(self, games, teams):
        game = None
        for game_id in games:
            if (games[game_id].home.id in teams and
               games[game_id].away.id in teams):
                game = games[game_id]
                break
        return game

    def __flip_flop_divisional_games(self, source, dest):
        for team_id in self.matchups:
            for g_id, g in self.matchups[team_id][source].items():
                game = Game(g.away, g.home)
                db.session.add(game)
                print("Creating {}: {} at {}".format(dest,
                                                     game.away.city,
                                                     game.home.city))
                self.matchups[game.home.id][dest][game.id] = game

    def __set_home_away(self, teamMatchups, matchupType, locGames):
        team_id = None
        teams = copy.deepcopy(self.teams)
        while len(teams) > 0:
            if team_id is None:
                team_id = choice(list(teams.keys()))
            team = self.matchups[team_id]['team']
            possibleOpp = teamMatchups[team.id][matchupType]
            if (len(self.matchups[team.id][matchupType]) >= locGames or
               len(possibleOpp) == 0):
                if team_id in teams:
                    del teams[team_id]
                team_id = None
                continue

            opp = choice(possibleOpp)

            # set the matchup
            print("Creating {}: {} at {}".format(matchupType,
                                                 opp.city,
                                                 team.city))
            game = Game(team, opp)
            game_fix = db.session.merge(game)
            db.session.add(game_fix)
            #self.matchups[team.id][matchupType].append(game_fix)
            self.matchups[team.id][matchupType][game_fix.id] = game_fix

            # remove the respective divisions for future games
            opploc = next((i for i, t in
                           enumerate(teamMatchups[team.id]
                                     [matchupType]) if t.id == opp.id),
                          None)
            del teamMatchups[team.id][matchupType][opploc]
            teamloc = next((i for i, t in
                            enumerate(teamMatchups[opp.id]
                                      [matchupType]) if t.id == team.id),
                           None)
            del teamMatchups[opp.id][matchupType][teamloc]

            # delete the current team and set the opp for a home game
            team_id = opp.id

    def __intra_conference_matchups(self):
        # intra conference every 3 years
        intra_offset = (self.season.id % 3) + 1

        divMatchups = {}
        teamMatchups = {}
        # loop through intra conference play
        for cname, divisions in self.standings.items():
            print("conference: {}".format(cname))
            divMatchups[cname] = {}
            group1 = list(divisions.keys())
            group2 = copy.deepcopy(group1)
            del group2[intra_offset]
            del group2[0]
            print("Division matchups: {} vs {}".format(group1[0],
                                                       group1[intra_offset]))
            print("Division Rank matchups: {} vs {}".format(group2[0],
                                                            group2[1]))

            divMatchups[cname][group1[0]] = {
                'intraconf': list(self.standings[cname]
                                  [group1[intra_offset]].values()),
                'divRank': [group2[0], group2[1]]
            }

            divMatchups[cname][group1[intra_offset]] = {
                'intraconf': list(self.standings[cname]
                                  [group1[0]].values()),
                'divRank': [group2[0], group2[1]]
            }

            divMatchups[cname][group2[0]] = {
                'intraconf': list(self.standings[cname]
                                  [group2[1]].values()),
                'divRank': [group1[intra_offset], group1[0]]
            }

            divMatchups[cname][group2[1]] = {
                'intraconf': list(self.standings[cname]
                                  [group2[0]].values()),
                'divRank': [group1[intra_offset], group1[0]]
            }

    # print out the different matchups
        for conf, divisions in divMatchups.items():
            for division in divisions:
                print("{}: {} vs {}".format(conf,
                                            division,
                                            divisions[division]))

        # convert to team level
        for conf, divisions in self.standings.items():
            for div, teams in divisions.items():
                for rank, t in teams.items():
                    teamMatchups[t.id] = copy.deepcopy(divMatchups[conf][div])
                    teamMatchups[t.id]['rank'] = []
                    for divRank in divMatchups[conf][div]['divRank']:
                        opp = self.standings[conf][divRank][rank]
                        teamMatchups[t.id]['rank'].append(opp)

        return teamMatchups

    def __inter_conference_matchups(self):
        # inter conference every 4
        interconf_matchup = self.season.id % 4

        matchups = {}
        conf = list(self.standings.keys())
        divList = list(self.standings[conf[0]].keys())
        for index, division in enumerate(self.standings[conf[0]].values()):
            matchup = (index + interconf_matchup) % 4
            for team in division.values():
                for opp in self.standings[conf[1]][divList[matchup]].values():
                    if team.id not in matchups:
                        matchups[team.id] = {'interconf': []}
                    matchups[team.id]['interconf'].append(opp)
                    if opp.id not in matchups:
                        matchups[opp.id] = {'interconf': []}
                    matchups[opp.id]['interconf'].append(team)
        return matchups

    def __division_matchups(self):
        matchups = {}
        for conf, divisions in self.standings.items():
            for division, teams in divisions.items():
                for team in teams.values():
                    matchups[team.id] = {'divisionstart': []}
                    for opp in teams.values():
                        if team.id != opp.id:
                            matchups[team.id]['divisionstart'].append(opp)
                    (matchups[team.id]
                     ['divisionend']) = copy.deepcopy(matchups[team.id]
                                                      ['divisionstart'])
        return matchups
