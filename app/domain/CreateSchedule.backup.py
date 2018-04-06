from app.domain.Game import Game
# from app.domain.Conference import Conference
# from app.domain.Division import Division
# from app.domain.Team import Team
from app.domain.Standings import Standings
from app.domain.Season import Season
from app.domain.Schedule import Schedule
from app.domain.GameType import GameType
from app.server import db
from app.server import query
from sqlalchemy import func
from random import sample, choice
import copy


class CreateSchedule(object):
    def __init__(self):
        self.regular_season_weeks = 18
        self.post_season_teams = 12
        self.matchups = {}
        self.season = query(Season, func.max(Season.id)).first()[0]
        standings = Standings()
        self.standings = standings.standings
        self.schedule = {}
        self.__init_matchups()

    def __init_matchups(self):
        for conf, divisions in self.standings.items():
            print("matchups init for {}".format(conf))
            for div, teams in divisions.items():
                print("matchups init for {}-{}".format(conf, div))

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

        # gameType = query(GameType).filter_by(game_type="regular season") \
        #                           .first()



        # logic for all non division games
        self.__create_nondivision_matchups()
        # add divisional opponents
        self.__create_division_matchups()

        # set bye week init schedule
        for team_id in self.matchups:
            byeWeek = (team_id + self.season.id) % 8 + 7
            self.matchups[team_id]['byeWeek'] = byeWeek
            self.schedule[team_id] = {
                'weeks': {},
                'home': 0,
                'away': 0
            }

        # divisional games
        while True:
            teams = list(filter(lambda team_id: len(self.matchups[team_id]['division']) > 0, self.matchups))
            if len(teams) == 0:
                break
            else:
                self.__add_divisional_matchups(set(teams))

        # while True:
        #    teams = list(filter(lambda team_id: len(self.matchups[team_id]['opponents']) > 0, self.matchups))
        #    if len(teams) == 0:
        #        break
        #    else:
        #        self.__add_matchups(set(teams))

        for team_id in self.matchups:
            while len(self.matchups[team_id]['opponents']) > 0:
                print(team_id, len(self.matchups[team_id]['opponents']))
                weeks = set(list(range(1, self.regular_season_weeks + 1)))
                location = set(['home', 'away'])

                if len(self.schedule[team_id]['weeks']) > 0:
                    weeks -= set(self.schedule[team_id]['weeks'].keys())
                    # weeks -= set([self.matchups[team_id]['byeWeek']])

                opponent = choice(list(self.matchups[team_id]['opponents'].keys()))
                if len(self.schedule[opponent]['weeks']) > 0:
                    weeks -= set(self.schedule[opponent]['weeks'].keys())
                    # weeks -= set([self.matchups[opponent]['byeWeek']])

                #  fix scheduling conflict
                if len(weeks) < 1:
                    print("WE HAVE A scheduling problem")
                    weeks = self.__reworkschedule(set(list(range(1, self.regular_season_weeks + 1))),
                                                  team_id,
                                                  opponent)

                week = list(weeks)[0]
                game = None
                loc = sample(location, 1)[0]
                if self.schedule[team_id]['home'] < 8 and loc == 'home':
                    game = Game(self.matchups[team_id]['team'],
                                self.matchups[opponent]['team'])
                    self.schedule[team_id]['home'] += 1
                    self.schedule[opponent]['away'] += 1
                elif self.schedule[opponent]['away'] < 8:
                    game = Game(self.matchups[opponent]['team'],
                                self.matchups[team_id]['team'])
                    self.schedule[opponent]['home'] += 1
                    self.schedule[team_id]['away'] += 1
                else:
                    raise Exception("TO MANY HOME GAMES", "OH NO")

                self.schedule[team_id]['weeks'][week] = game
                self.schedule[opponent]['weeks'][week] = game
                # remove teams for next round
                self.matchups[team_id]['opponents'].pop(opponent)
                self.matchups[opponent]['opponents'].pop(team_id)


        for team_id in self.schedule:
            for week, game in self.schedule[team_id]['weeks'].items():
                print("Week {}: {} at {}".format(week,
                                                 game.away.city,
                                                 game.home.city))

        # for team_id in self.matchups:
        #    print(self.matchups[team_id]['division'])
        #    print(self.matchups[team_id]['opponents'])
        # Schedule(week, game_type, game)
        # Game(home, away)

        # start with one team
        # move half tossup into home half away
        # make sure other team is balanced
        # adjust other 10 teams
        # add bye week

        # go through each division
        # week 15 1 3, home 2, 4 away
        # week 16 2, 4 home 1, 3 away
        # week 17 3, 1 home, 2, 4 away
        # foreach week choice 1, 5 to reverse
        # if week alreay taken remove week and choice again

        # weeks 1 - 5
        # foreach team fill holes

        # weeks 6 - 14
        # first 4 teams get byes
        # foreach team fill holes
        # if week can't be filled
        # and team dosne't have a bye week yet
        # team bye week
        # if bye week already taken see if matchup is availiable on bye week
        # swap
        # else
        # cry

    def __add_divisional_matchups(self, teams):
        while len(teams) != 0:
            firstWeeks = set(list(range(1, 6)))
            lastWeeks = set(list(range(15, self.regular_season_weeks + 1)))
            team = sample(teams, 1)[0]
            teams.remove(team)
            if len(self.matchups[team]['division']) == 0:
                continue

            if len(self.schedule[team]['weeks']) > 0:
                firstWeeks -= set(self.schedule[team]['weeks'].keys())
                lastWeeks -= set(self.schedule[team]['weeks'].keys())

            opponent = choice(list(self.matchups[team]['division'].keys()))
            if len(self.schedule[opponent]['weeks']) > 0:
                firstWeeks -= set(self.schedule[opponent]['weeks'].keys())
                lastWeeks -= set(self.schedule[opponent]['weeks'].keys())

            #  fix scheduling conflict
            if len(firstWeeks) < 1:
                print("WE HAVE A scheduling problem")
                firstWeeks = self.__reworkschedule(set(list(range(1, 6))),
                                                   team,
                                                   opponent)
            # fix scheduling conflict
            if len(lastWeeks) < 1:
                print("WE HAVE A scheduling problem")
                lastWeeks = self.__reworkschedule(set(list(range(15, self.regular_season_weeks + 1))),
                                                  team,
                                                  opponent)

            # schedule the first game
            fweek = sample(firstWeeks, 1)[0]
            game1 = Game(self.matchups[team]['team'],
                         self.matchups[opponent]['team'])
            self.schedule[team]['weeks'][fweek] = game1
            self.schedule[team]['home'] += 1
            self.schedule[opponent]['weeks'][fweek] = game1
            self.schedule[opponent]['away'] += 1

            # schedule the last game
            lweek = sample(lastWeeks, 1)[0]
            game2 = Game(self.matchups[opponent]['team'],
                         self.matchups[team]['team'])
            self.schedule[team]['weeks'][lweek] = game2
            self.schedule[team]['away'] += 1
            self.schedule[opponent]['weeks'][lweek] = game2
            self.schedule[opponent]['home'] += 1

            # remove teams for next round
            self.matchups[team]['division'].pop(opponent)
            self.matchups[opponent]['division'].pop(team)

    def __add_matchups(self, teams):
        while len(teams) != 0:
            weeks = set(list(range(1, self.regular_season_weeks + 1)))
            team = sample(teams, 1)[0]
            teams.remove(team)

            if len(self.schedule[team]['weeks']) > 0:
                weeks -= set(self.schedule[team]['weeks'].keys())
                weeks -= set([self.matchups[team]['byeWeek']])

            if len(self.matchups[team]['opponents']) == 0:
                continue

            opponent = choice(list(self.matchups[team]['opponents'].keys()))
            if len(self.schedule[opponent]['weeks']) > 0:
                weeks -= set(self.schedule[opponent]['weeks'].keys())
                weeks -= set([self.matchups[opponent]['byeWeek']])

            #  fix scheduling conflict
            if len(weeks) < 1:
                print("WE HAVE A scheduling problem")
                weeks = self.__reworkschedule(set(list(range(1, self.regular_season_weeks + 1))),
                                              team,
                                              opponent)

            # schedule the first game
            # week = sample(weeks, 1)[0]
            week = list(weeks)[0]
            game = None
            if self.schedule[team]['home'] < 8:
                game = Game(self.matchups[team]['team'],
                            self.matchups[opponent]['team'])
                self.schedule[team]['home'] += 1
                self.schedule[opponent]['away'] += 1
            elif self.schedule[opponent]['home'] < 8:
                game = Game(self.matchups[opponent]['team'],
                            self.matchups[team]['team'])
                self.schedule[opponent]['home'] += 1
                self.schedule[team]['away'] += 1
            else:
                raise Exception("TO MANY HOME GAMES", "OH NO")

            self.schedule[team]['weeks'][week] = game
            self.schedule[opponent]['weeks'][week] = game

            # remove teams for next round
            self.matchups[team]['opponents'].pop(opponent)
            self.matchups[opponent]['opponents'].pop(team)

    def __reworkschedule(self, weeks, home_id, away_id):
        for week in weeks:
            if (
                    week in self.schedule[home_id]['weeks'] and
                    week in self.schedule[away_id]['weeks']
            ):
                print("Both teams have {} booked".format(week))
            else:
                team_id = None
                game = None
                if week in self.schedule[home_id]['weeks']:
                    team_id = home_id
                    print("team {} needs rework".format(home_id))
                elif week in self.schedule[away_id]['weeks']:
                    team_id = away_id
                    print("team {} needs rework".format(away_id))
                else:
                    print("Both Teams have week {} open".format(week))
                    return set([week])

                print("trying to move game for team {} week {}".format(team_id,
                                                                       week))

                game = self.schedule[team_id]['weeks'][week]
                tmpWeeks = copy.deepcopy(weeks)
                print(tmpWeeks)
                tmpWeeks -= set(self.schedule[game.home.id]['weeks'].keys())
                print(tmpWeeks, set(self.schedule[game.home.id]['weeks'].keys()))
                tmpWeeks -= set(self.schedule[game.away.id]['weeks'].keys())
                print(tmpWeeks, set(self.schedule[game.away.id]['weeks'].keys()))
                if len(tmpWeeks) > 0:
                    print("we found a week to move the existing game")
                    moveToWeek = sample(tmpWeeks, 1)[0]
                    game = self.schedule[game.home.id]['weeks'][week]
                    self.schedule[game.home.id]['weeks'][moveToWeek] = game
                    self.schedule[game.away.id]['weeks'][moveToWeek] = game
                    self.schedule[game.home.id]['weeks'].pop(week)
                    self.schedule[game.away.id]['weeks'].pop(week)
                    return set([week])

        if self.matchups[home_id]['byeWeek'] not in self.schedule[away_id]['weeks']:
            print("can use bye week #1")
        elif self.matchups[away_id]['byeWeek'] not in self.schedule[home_id]['weeks']:
            print("can use bye week #2")
        else:
            print("WE CAN NOT USE THE BYE WEEK")

        print("home team: {}".format(self.matchups[home_id]['team'].city))
        for week, game in self.schedule[home_id]['weeks'].items():
            print("{}: {} at {}".format(week, game.away.city, game.home.city))
        print("away team: {}".format(self.matchups[away_id]['team'].city))
        for week, game in self.schedule[away_id]['weeks'].items():
            print("{}: {} at {}".format(week, game.away.city, game.home.city))
        raise Exception('spam', 'eggs')

    def __create_division_matchups(self):
        for conf in self.standings:
            print(conf)
            for division in self.standings[conf]:
                print(division)
                for rank, team in self.standings[conf][division].items():
                    self.matchups[team.id]['division'] = {}
                    for o in self.standings[conf][division].values():
                        if o.id != team.id:
                            self.matchups[team.id]['division'][o.id] = o

    def __create_nondivision_matchups(self):
        # intra conference every 3 years
        intra_offset = (self.season.id % 3) + 1

        # loop through intra conference play
        for cname, divisions in self.standings.items():
            print("conference: {}".format(cname))
            # first position plays intraconf_offset
            # left overs play eachother
            # first and intraconf_offset play rank from leftovers
            # leftovers play rank from first and intraconf_offset
            divList = list(divisions.keys())
            leftovers = copy.deepcopy(divList)
            del leftovers[intra_offset]
            del leftovers[0]
            print("Division matchups: {} vs {}".format(divList[0],
                                                       divList[intra_offset]))
            print("Division Rank matchups: {} vs {}".format(leftovers[0],
                                                            leftovers[1]))

            self.__intra_conference_play(divisions[divList[0]],
                                         divisions[divList[intra_offset]],
                                         divisions[leftovers[0]],
                                         divisions[leftovers[1]])
            self.__intra_conference_play(divisions[divList[intra_offset]],
                                         divisions[divList[0]],
                                         divisions[leftovers[0]],
                                         divisions[leftovers[1]])
            self.__intra_conference_play(divisions[leftovers[0]],
                                         divisions[leftovers[1]],
                                         divisions[divList[0]],
                                         divisions[divList[intra_offset]])
            self.__intra_conference_play(divisions[leftovers[1]],
                                         divisions[leftovers[0]],
                                         divisions[divList[0]],
                                         divisions[divList[intra_offset]])

        # inter conference every 4
        interconf_matchup = self.season.id % 4
        conf = list(self.standings.keys())
        for index, division in enumerate(self.standings[conf[0]].values()):
            matchup = (index + interconf_matchup) % 4
            for team in division.values():
                for opp in self.standings[conf[1]][divList[matchup]].values():
                    self.matchups[team.id]['opponents'][opp.id] = opp
                    self.matchups[opp.id]['opponents'][team.id] = team
        #for index, division in enumerate(self.standings[conf[1]].values()):
        #    matchup = (index + interconf_matchup) % 4
        #    for team in division.values():
        #        for opp in self.standings[conf[0]][divList[matchup]].values():
        #            self.matchups[team.id]['opponents'][opp.id] = opp
        #            self.matchups[opp.id]['opponents'][team.id] = team

    def __intra_conference_play(self, division, opponents, rank1, rank2):
        """division contains a dictionary of RANK: TEAM to add games for
           opponents is the teams to play the entire division
           rank1|2 will only play the team with the same rank"""
        for rank, team in division.items():
            self.matchups[team.id] = {
                'team': team,
                'opponents': {t.id: t for t in opponents.values()}
            }

            self.matchups[team.id]['opponents'][rank1[rank].id] = rank1[rank]
            self.matchups[team.id]['opponents'][rank2[rank].id] = rank2[rank]

    def advancePostSeasonSchedule(self):
        standings = Standings()
        gameType = query(GameType).filter_by(game_type="post season") \
                                  .first()

        maxWeek = query(Schedule,
                        func.max(Schedule.week)).filter_by(game_type=gameType)\
                                                .first()
        lastWeek = maxWeek[1]

        playoffTeams = {}
        if lastWeek is None:
            for rank in range(1, self.post_season_teams+1):
                playoffTeams[rank] = standings.rankings[rank]
            maxWeek = query(Schedule, func.max(Schedule.week)).first()
        else:
            # we'll need to pick winners
            games = query(Schedule) \
                    .filter_by(game_type=gameType) \
                    .filter_by(week=lastWeek).all()

            if len(games) <= 1:
                # Season's over son
                return None
            else:
                count = 1
                print(games)
                for game in games:
                    print(game.toJSON())
                    if game.result.home_score > game.result.away_score:
                        playoffTeams[count] = game.game.home
                    else:
                        playoffTeams[count] = game.game.away
                    count += 1

        nextWeek = maxWeek[1] + 1
        home = 1
        away = len(playoffTeams)
        while home < away:
            game = Game(playoffTeams[home], playoffTeams[away])
            db.session.add(game)
            schedule = Schedule(nextWeek, gameType, game)
            db.session.add(schedule)
            away = away - 1
            home = home + 1

        db.session.commit()
