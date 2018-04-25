from random import choices
from app.domain.Conference import Conference
from app.domain.Division import Division
from app.domain.Team import Team
from app.server import query


class Standings:
    def __init__(self):
        self.standings = {}
        conferences = query(Conference).order_by(Conference.shortName).all()

        for c in conferences:
            self.standings[c.name] = {}
            for d in c.divisions:
                teams = query(Team).filter_by(division_id=d.id) \
                                   .order_by(Team.wins.desc()) \
                                   .order_by(Team.points_for.desc()) \
                                   .order_by(Team.points_against.asc()).all()
                self.standings[c.name][d.name] = self.__createStandings(teams)

    def __createStandings(self, teams):
        standings = {}
        rank = 0
        while rank < len(teams):
            tR = rank
            while (tR+1 < len(teams) and
                   teams[tR].wins == teams[tR+1].wins and
                   teams[tR].points_for == teams[tR+1].points_for and
                   teams[tR].points_against == teams[tR+1].points_against):
                tR += 1

            if tR != rank:
                teamsRanked = []
                tobeRanked = range(rank, tR+1)
                while len(tobeRanked) > 0:
                    # we have teams that are tied
                    luckyTeam = choices(tobeRanked)[0]
                    standings[rank+1] = teams[luckyTeam]
                    teamsRanked.append(luckyTeam)
                    tobeRanked = list(set(tobeRanked) - set(teamsRanked))
                    rank += 1
            else:
                standings[rank+1] = teams[rank]
            rank += 1

        return standings

    def toJSON(self):
        rankings = []
        for c in self.standings:
            conf = {
                'conference': c,
                'divisions': []
            }
            for d in self.standings[c]:
                division = {
                    'division': d,
                    'teams': [{'rank': r,
                               'team': t.toJSON()} for r,
                              t in self.standings[c][d].items()]
                }
                print(self.standings[c][d])
                conf['divisions'].append(division)
            rankings.append(conf)
        return rankings

    def teamRankLookup(self, team):
        conf = team.division.conference.name
        division = team.division.name

        for rank, t in self.standings[conf][division].items():
            if t.id == team.id:
                return rank
