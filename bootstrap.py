import random
from app.server import db
from app.domain.Conference import Conference
from app.domain.Division import Division
from app.domain.Team import Team
from app.domain.Game import Game
from app.domain.Champions import Champions
from app.domain.Season import Season
from app.domain.History import History
from app.domain.Schedule import Schedule
from app.domain.Result import Result
from app.domain.Phase import Phase
from app.domain.Playoff import Playoff
from app.domain.State import State

# Players and stuff
from app.domain.roster.Position import Position
from app.domain.roster.Player import Player
from app.domain.roster.PlayerGenerator import generatePlayer

# db imports
from app.domain import initialize_sql


initialize_sql(db.engine)

print("Adding first season")
season = Season("Season 1")
db.session.add(season)

print("Creating Conferences")
afc = Conference(name="American Football Conference",
                 shortName="AFC")
db.session.add(afc)
nfc = Conference(name="National Football Conference",
                 shortName="NFC")
db.session.add(nfc)

print("Creating Divisions")
afc_n = Division(name="North")
db.session.add(afc_n)
afc_s = Division(name="South")
db.session.add(afc_s)
afc_e = Division(name="East")
db.session.add(afc_e)
afc_w = Division(name="West")
db.session.add(afc_n)

afc.divisions.append(afc_n)
afc.divisions.append(afc_e)
afc.divisions.append(afc_s)
afc.divisions.append(afc_w)


nfc_n = Division(name="North")
db.session.add(nfc_n)
nfc_s = Division(name="South")
db.session.add(nfc_s)
nfc_e = Division(name="East")
db.session.add(nfc_e)
nfc_w = Division(name="West")
db.session.add(nfc_n)

nfc.divisions.append(nfc_n)
nfc.divisions.append(nfc_s)
nfc.divisions.append(nfc_e)
nfc.divisions.append(nfc_w)

print("Adding Teams")
def addTeam(teamName, division):
    team = Team(teamName,
                division,
                random.randint(1, 5),
                random.randint(1, 5),
                random.randint(1, 5))
    db.session.add(team)
    division.teams.append(team)


addTeam("Baltimore", afc_n)
addTeam("Cincinatti", afc_n)
addTeam("Cleveland", afc_n)
addTeam("Pittsburgh", afc_n)

addTeam("Buffalo", afc_e)
addTeam("New England", afc_e)
addTeam("Miami", afc_e)
addTeam("New Jersey", afc_e)

addTeam("Jacksonville", afc_s)
addTeam("Indianapolis", afc_s)
addTeam("Houston", afc_s)
addTeam("Tennessee", afc_s)

addTeam("Denver", afc_w)
addTeam("Kansas City", afc_w)
addTeam("Oakland", afc_w)
addTeam("Los Angeles", afc_w)

addTeam("Atlanta", nfc_s)
addTeam("Carolina", nfc_s)
addTeam("New Orleans", nfc_s)
addTeam("Tampa Bay", nfc_s)

addTeam("Chicago", nfc_n)
addTeam("Detroit", nfc_n)
addTeam("Green Bay", nfc_n)
addTeam("Minnessota", nfc_n)

addTeam("Dallas", nfc_e)
addTeam("New York", nfc_e)
addTeam("Philadelphia", nfc_e)
addTeam("Washington", nfc_e)

addTeam("Arizona", nfc_w)
addTeam("San Diego", nfc_w)
addTeam("San Francisco", nfc_w)
addTeam("Seattle", nfc_w)


print("Creating Game Phases")
phase = Phase("NEWGAME", "newGame")
db.session.add(phase)
phase = Phase("GENERATE_SCHEDULE", "createSchedule")
db.session.add(phase)
phase = Phase("REGULARSEASON", "regularSeason")
db.session.add(phase)
phase = Phase("STARTPOSTSEASON", "createPlayoffs")
db.session.add(phase)
phase = Phase("POSTSEASON", "playoffs")
db.session.add(phase)
phase = Phase("OFFSEASON", "offseason")
db.session.add(phase)

print("Creating Positions")
qb = Position("Quarter Back", "QB", 35, 9, 1, 90)
db.session.add(qb)
rb = Position("Running Back", "RB", 10, 40, 40, 20)
db.session.add(rb)
wr = Position("Wide Receiver", "WR", 10, 60, 15, 25)
db.session.add(wr)
te = Position("Tight End", "TE", 5, 30, 30, 40)
db.session.add(te)
ol = Position("Offensive Line", "OL", 40, 5, 45, 50)
db.session.add(ol)

dl = Position("Defensive Line", "DL", 35, 4, 45, 50)
db.session.add(dl)
lb = Position("Line Backer", "LB", 35, 30, 30, 40)
db.session.add(lb)
dback = Position("Defensive Back", "DB", 30, 60, 20, 20)
db.session.add(dback)
k = Position("Kicker", "K", 50, 0, 5, 95)
db.session.add(k)
p = Position("Punter", "P", 50, 0, 5, 95)
db.session.add(p)

print("Creating first roster")
players = {
    qb: {
        'count': 3,
        'abilities': {
            'maxSpeed': 50,
            'maxStrength': 50,
        }
    },
    rb: {
        'count': 4,
        'abilities': {
            'minSpeed': 50
        }
    },
    wr: {
        'count': 6,
        'abilities': {
            'minSpeed': 50
        }
    },
    te: {
        'count': 3,
        'abilities': {
            'maxSpeed': 75,
            'minSpeed': 25
        }
    },
    ol: {
        'count': 9,
        'abilities': {
            'maxSpeed': 45,
            'minStrength': 50
        }
    },
    dl: {
        'count': 9,
        'abilities': {
            'maxSpeed': 45,
            'minStrength': 50
        }
    },
    lb: {
        'count': 9,
        'abilities': {
            'minSpeed': 33,
            'maxSpeed': 75,
            'minStrength': 33
        }
    },
    dback: {
        'count': 10,
        'abilities': {
            'minSpeed': 50
        }
    },
    k: {
        'count': 1,
        'abilities': {
            'maxSpeed': 10,
            'maxStrength': 15
        }
    },
    p: {
        'count': 1,
        'abilities': {
            'maxSpeed': 10,
            'maxStrength': 15
        }
    }
}

for position, attr in players.items():
    for c in range(0, attr['count']):
        db.session.add(generatePlayer(position, **attr['abilities']))
db.session.commit()
