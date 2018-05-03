from app.domain.schedule.Game import Game
from app.domain.league.Team import Team
from app.domain.schedule.Standings import Standings
from app.domain.schedule.Season import Season
from app.domain.schedule.Schedule import Schedule
from app.server import db
from app.server import query
from sqlalchemy import func
from random import choice
import copy


class CreateSchedule(object):
    def __init__(self):
        self.regular_season_weeks = 17
        self.number_of_bye_weeks = 2
        self.post_season_teams = 12
        self.matchups = {}
        self.season = query(Season, func.max(Season.id)).first()[0]
        self.stand = Standings()
        self.standings = self.stand.standings
        self.schedule = {}
        self.__init_matchups()
        self.teams = {t.id: t for t in query(Team).all()}
        self.league = {}
        self.__init_league()
        self.divisionalMatchups = {}

    def __init_league(self):
        self.league = {}
        for conf, divisions in self.standings.items():
            self.league[conf] = {}
            for division,  teams in divisions.items():
                self.league[conf][division] = {}
                for team in teams.values():
                    # print(team)
                    self.league[conf][division][team.id] = team

    def __init_matchups(self):
        for conf, divisions in self.standings.items():
            # print("matchups init for {}".format(conf))
            for div, teams in divisions.items():
                # print("matchups init for {}-{}".format(conf, div))
                for team in teams.values():
                    # print("matchups init for {}".format(team.city))
                    self.matchups[team.id] = {
                        'team': team,
                        'interconf': [],
                        'divisionstart': [],
                        'divisionend': [],
                        'rank': [],
                        'intraconf': []
                    }

    def __convert_matchups(self):
        for team_id, matchups in self.matchups.items():
            for matchupType in ['interconf',
                                'divisionstart',
                                'divisionend',
                                'rank',
                                'intraconf']:
                matchups[matchupType] = {g.id: g
                                         for g in matchups[matchupType]}
        for team_id, matchups in self.matchups.items():
            for matchupType in ['interconf',
                                'divisionstart',
                                'divisionend',
                                'rank',
                                'intraconf']:
                for game in matchups[matchupType].values():
                    self.matchups[game.away.id][matchupType][game.id] = game

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
        db.session.commit()
        # set rank
        self.__set_home_away(teamMatchups, 'rank', 1)
        db.session.commit()

        # inter conference matchups
        teamMatchups = self.__inter_conference_matchups()
        self.__set_home_away(teamMatchups, 'interconf', 2)
        db.session.commit()

        # division matchups
        teamMatchups = self.__division_matchups()
        self.__set_home_away(teamMatchups, 'divisionstart', 2)
        self.__flip_flop_divisional_games('divisionstart', 'divisionend')
        db.session.commit()

        self.__convert_matchups()

        # setup the schedule
        for week in range(1, self.regular_season_weeks + 1):
            self.schedule[week] = {
                'games': [],
                'teams': set()
            }

        # schedule the games
        self.__schedule_games('rank', 'divisionstart', 2, 2, [1, 4])
        self.__schedule_games('divisionstart', 'intraconf', 2, 2, [2, 3])
        self.__schedule_games('divisionstart', 'interconf', 2, 2, [5, 6])
        self.__schedule_games('intraconf', 'interconf', 2, 2, [7, 8])
        self.__schedule_games('intraconf', 'interconf', 2, 2, [9, 10])
        self.__schedule_games('intraconf', 'dummy', 4, 0, [11])
        self.__schedule_games('interconf', 'rank', 2, 2, [13, 14])
        self.__schedule_games('divisionend', 'dummy', 4, 0, [15])
        self.__schedule_games('divisionend', 'dummy', 4, 0, [16])
        self.__schedule_games('divisionend', 'dummy', 4, 0, [17])

        # move games around to create bye weeks
        self.__create_bye_weeks([7, 8, 9, 10, 13, 14], 11, 12)

        # add the games to the db
        for week in self.schedule:
            for game in self.schedule[week]['games']:
                # print(game.id, week)
                schedule = Schedule(week, game)
                db.session.add(schedule)

        db.session.commit()

    def __schedule_games(self, matchupTypeA, matchupTypeB,
                         desiredGamesA, desiredGamesB,
                         weeks):
        # tracks who is forced to play a different type game next week
        tracker = {}
        for week in weeks:
            tracker[week] = {
                matchupTypeA: set(),
                matchupTypeB: set()
            }

        scheduledGames = {}
        for conf in self.league.keys():
            scheduledGames[conf] = {}
            for division in self.league[conf].keys():
                scheduledGames[conf][division] = {}
                for week in weeks:
                    scheduledGames[conf][division][week] = {
                        matchupTypeA: 0,
                        matchupTypeB: 0
                    }

        for week in weeks:
            allTeams = set(list(self.matchups.keys()))
            while len(allTeams) > 0:
                for conf in self.league.keys():
                    for division, divTeams in self.league[conf].items():
                        teams = set(list(divTeams.keys()))
                        teams -= self.schedule[week]['teams']

                        if len(teams) == 0:
                            # print("all games for {} have been scheduled"
                            #      .format(division))
                            continue

                        countA = (scheduledGames[conf][division]
                                  [week][matchupTypeA])
                        countB = (scheduledGames[conf][division]
                                  [week][matchupTypeB])

                        game = None
                        matchupType = None
                        forcedType = None
                        if countA < desiredGamesA:
                            # schedule a type A game
                            matchupType = matchupTypeA
                            forcedType = matchupTypeB
                        elif countB < desiredGamesB:
                            # schedule a type B game
                            matchupType = matchupTypeB
                            forcedType = matchupTypeA
                        else:
                            # cry
                            raise Exception("CreateSchedule",
                                            ("{} has {} teams left,"
                                             " but already used up game"
                                             " placement".format(division,
                                                                 len(teams))))

                        # find a game by sorting teams by rank
                        sortedTeams = []
                        for team in self.standings[conf][division].values():
                            if team.id in teams:
                                sortedTeams.append(team.id)
                        for team in sortedTeams:
                            if game is not None:
                                break

                            # games = self.matchups[team][matchupType].values()
                            games = sorted(self.matchups[team][matchupType]
                                           .values(), key=lambda x: self.stand
                                           .teamRankLookup(x.away)
                                           if x.home.id == team
                                           else self.stand
                                           .teamRankLookup(x.home))
                            for g in games:
                                if g.home.id in self.schedule[week]['teams']:
                                    # print(g.home.city, "scheduled for week",
                                    #      week)
                                    continue
                                elif g.away.id in self.schedule[week]['teams']:
                                    # print(g.away.city, "scheduled for week",
                                    #      week)
                                    continue
                                elif g.home.id in tracker[week][forcedType]:
                                    # print(g.home.id, "forced", forcedType)
                                    continue
                                elif g.away.id in tracker[week][forcedType]:
                                    # print(g.away.id, "forced", forcedType)
                                    continue
                                else:
                                    game = g
                                    break
                        # add game
                        if game is None:
                            print("NO games for:", team)
                            print(self.matchups[team][matchupType])
                            for g in self.matchups[team][matchupType].values():
                                print("possible games {} at {}"
                                      .format(g.away.city, g.home.city))
                            raise Exception("CreateSchedule", "No Games")

                        # print(game)
                        # print("Week: {} {} {} at {} {}".format(week,
                        #                                        game.away.city,
                        #                                       game.away.id,
                        #                                       game.home.city,
                        #                                       game.home.id))
                        (scheduledGames[conf][game.home.division.name]
                         [week][matchupType]) += 1
                        (scheduledGames[conf][game.away.division.name]
                         [week][matchupType]) += 1
                        self.schedule[week]['games'].append(game)
                        self.schedule[week]['teams'].add(game.home.id)
                        self.schedule[week]['teams'].add(game.away.id)

                        # force for the next week
                        nextWeekIndex = weeks.index(week) + 1
                        if nextWeekIndex < len(weeks):
                            nextWeek = weeks[nextWeekIndex]
                            tracker[nextWeek][forcedType].add(game.home.id)
                            tracker[nextWeek][forcedType].add(game.away.id)

                        # cleanup
                        del self.matchups[game.home.id][matchupType][game.id]
                        del self.matchups[game.away.id][matchupType][game.id]
                        allTeams.discard(game.home.id)
                        allTeams.discard(game.away.id)

    def __create_bye_weeks(self, weeks, overBookedWeek, emptyWeek):
        """This assumes that there is an empty week with no games scheduled
        and that week also has teams on a bye
        and that overBookedWeek has half its games and has teams on bye"""
        teamsOnBye = len(self.teams) / (len(weeks) + 2)
        teamsWithBye = set()

        gameCount = 0
        for index, game in enumerate(self.schedule[overBookedWeek]['games']):
            if gameCount % 2 == 0:
                self.schedule[emptyWeek]['games'].append(game)
                self.schedule[emptyWeek]['teams'].add(game.home.id)
                self.schedule[emptyWeek]['teams'].add(game.away.id)
                self.schedule[overBookedWeek]['teams'].remove(game.home.id)
                self.schedule[overBookedWeek]['teams'].remove(game.away.id)
                del self.schedule[overBookedWeek]['games'][index]

        for week in weeks:
            weekByes = 0
            for index, game in enumerate(self.schedule[week]['games']):
                if game.home.id in teamsWithBye:
                    # print("{} already has bye week".format(game.home.city))
                    continue
                if game.away.id in teamsWithBye:
                    # print("{} already has bye week".format(game.away.city))
                    continue
                if weekByes >= teamsOnBye:
                    # print("Week {} has enough bye weeks".format(week))
                    break

                sourceWeek = None
                if (game.home.id
                   not in self.schedule[overBookedWeek]['teams'] and
                   game.away.id
                   not in self.schedule[overBookedWeek]['teams']):
                    sourceWeek = overBookedWeek

                if (game.home.id
                   not in self.schedule[emptyWeek]['teams'] and
                   game.away.id
                   not in self.schedule[emptyWeek]['teams']):
                    sourceWeek = emptyWeek

                if sourceWeek is not None:
                    # print("moving {} at {}".format(game.away.city,
                    #                               game.home.city))
                    self.schedule[sourceWeek]['games'].append(game)
                    self.schedule[sourceWeek]['teams'].add(game.home.id)
                    self.schedule[sourceWeek]['teams'].add(game.away.id)
                    self.schedule[week]['teams'].remove(game.home.id)
                    self.schedule[week]['teams'].remove(game.away.id)
                    del self.schedule[week]['games'][index]
                    teamsWithBye.add(game.home.id)
                    teamsWithBye.add(game.away.id)
                    weekByes += 2
                    continue

    def __flip_flop_divisional_games(self, source, dest):
        for team_id in self.matchups:
            for g in self.matchups[team_id][source]:
                game = Game(g.away, g.home)
                db.session.add(game)
                # print("Creating {}: {} at {}".format(dest,
                #                                     game.away.city,
                #                                     game.home.city))
                self.matchups[game.home.id][dest].append(game)

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
            # print("Creating {}: {} at {}".format(matchupType,
            #                                     opp.city,
            #                                     team.city))
            game = Game(team, opp)
            game_fix = db.session.merge(game)
            db.session.add(game_fix)

            self.matchups[team.id][matchupType].append(game_fix)

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
            # print("conference: {}".format(cname))
            divMatchups[cname] = {}
            group1 = list(divisions.keys())
            group2 = copy.deepcopy(group1)
            del group2[intra_offset]
            del group2[0]
            # print("Division matchups: {} vs {}".format(group1[0],
            #                                           group1[intra_offset]))
            # print("Division Rank matchups: {} vs {}".format(group2[0],
            #                                                group2[1]))

            divMatchups[cname][group1[0]] = {
                'divIntraconf': group1[intra_offset],
                'divRank': [group2[0], group2[1]]
            }

            divMatchups[cname][group1[intra_offset]] = {
                'divIntraconf': group1[0],
                'divRank': [group2[0], group2[1]]
            }

            divMatchups[cname][group2[0]] = {
                'divIntraconf': group2[1],
                'divRank': [group1[intra_offset], group1[0]]
            }

            divMatchups[cname][group2[1]] = {
                'divIntraconf': group2[0],
                'divRank': [group1[intra_offset], group1[0]]
            }

        # convert to team level
        for conf, divisions in self.standings.items():
            for div, teams in divisions.items():
                for rank, t in teams.items():
                    self.divisionalMatchups[t.id] = copy.deepcopy(divMatchups
                                                                  [conf][div])
                    teamMatchups[t.id] = copy.deepcopy(divMatchups[conf][div])
                    teamMatchups[t.id]['intraconf'] = copy.deepcopy(list(
                        self.standings[conf][divMatchups[conf][div]
                                             ['divIntraconf']].values()))
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
                    matchups[team.id]['divInter'] = divList[matchup]
                    matchups[team.id]['interconf'].append(opp)
                    if opp.id not in matchups:
                        matchups[opp.id] = {'interconf': []}
                    matchups[opp.id]['divInter'] = divList[index]
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
