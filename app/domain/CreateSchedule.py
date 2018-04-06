# from app.domain.Game import Game
# from app.domain.Conference import Conference
# from app.domain.Division import Division
from app.domain.Team import Team
from app.domain.Standings import Standings
from app.domain.Season import Season
from app.domain.Schedule import Schedule
# from app.domain.GameType import GameType
# from app.server import db
from app.server import query
from sqlalchemy import func
from random import choice
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
                        'interconf': {
                              'home': {},
                              'away': {}
                        },
                        'division': {},
                        'rank': {
                            'home': {},
                            'away': {}
                        },
                        'intraconf': {
                            'home': {},
                            'away': {}
                        }
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

        # gameType = query(GameType).filter_by(game_type="regular season") \
        #                           .first()

        # intra conference matchups
        teamMatchups = self.__intra_conference_matchups()
        # set intra-division
        self.__set_home_away(teamMatchups, 'intraconf', 2)
        # set rank
        self.__set_home_away(teamMatchups, 'rank', 1)

        # inter conference matchups
        teamMatchups = self.__inter_conference_matchups()
        self.__set_home_away(teamMatchups, 'interconf', 2)

    def __set_home_away(self, teamMatchups, matchupType, locGames):
        team_id = None
        teams = copy.deepcopy(self.teams)
        while len(teams) > 0:
            if team_id is None:
                team_id = choice(list(teams.keys()))
            team = self.matchups[team_id]['team']
            possibleOpp = teamMatchups[team.id][matchupType]
            if (len(self.matchups[team.id][matchupType]['home']) >= locGames or
               len(possibleOpp) == 0):
                if team_id in teams:
                    del teams[team_id]
                team_id = None
                continue

            opp = choice(possibleOpp)

            if len(self.matchups[opp.id][matchupType]['away']) >= locGames:
                print("{} has to many away games")
                continue

            # set the matchup
            print("Scheduling {} at {}".format(opp.city, team.city))
            self.matchups[team.id][matchupType]['home'][opp.id] = opp
            self.matchups[opp.id][matchupType]['away'][team.id] = team

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
