class GeneralManagerCache {
  constructor() {
    this._team = null;
    this._teams = null;
    this._loading = true
    this._schedule = null;
    this._rankings = null;
  }

  //get user selected team
  get team() {
    return this._team;
  }

  set team(team_id) {
    this._team = this._teams[team_id];
  }

  // get loading
  get loading() {
    return this._loading;
  }

  set loading(loading) {
    this._loading  = loading;
    if (this._loading) {
      $('#loaderModal').modal('show')
    } else {
      $('#loaderModal').modal('hide');
    }
  }

  //get teams
  getTeams(useCache) {
    this.loading = true;
    var dfd = jQuery.Deferred();
    var cache = this;
    if (cache._teams && useCache) {
      dfd.resolve(cache._teams);
      cache.loading = false;
    } else { 
      $.getJSON("api/league/1/teams", function(teams) {
        cache._teams = teams;
        if (cache._team && cache._team.team_id) {
          cache._team = teams[cache._team.team_id]
        }
        dfd.resolve(cache._teams);
        cache.loading = false;
        });
    }
    return dfd.promise();
  }


  //get team Ranking
  getTeamRankings() {
    var dfd = jQuery.Deferred();
    this.loading = true;
    var cache = this;
    $.getJSON("/api/league/1/rankings", function(rankings) {
      cache._rankings = rankings;
      cache.loading = false;
      dfd.resolve(cache._rankings);
    });
    return dfd.promise();
  }


  //create the schedule
  createSchedule() {
    var dfd = jQuery.Deferred();
    this.loading = true;
    var cache = this;
    $.getJSON("/api/league/1/schedule/create", function(schedule) {
      cache._schedule = schedule;
      cache.loading = false;
      dfd.resolve(cache._schedule);
    });
    return dfd.promise();
  }

  //fetch the schedule
  getSchedule(useCache) {
    var dfd = jQuery.Deferred();
    this.loading = true;
    var cache = this;
    if (cache._schedule && useCache) {
      cache.loading = false;
      dfd.resolve(cache._schedule);
    } else { 
      $.getJSON("/api/league/1/schedule/create", function(schedule) {
        cache._schedule = schedule;
        cache.loading = false;
        dfd.resolve(cache._schedule);
      });
    }
    return dfd.promise();
  }


  //get results
  getResults() {
    var dfd = jQuery.Deferred();
    this.loading = true;
    var cache = this;
    $.getJSON("/api/league/1/results", function(results) {
      cache._results = results;
      cache.loading = false;
      dfd.resolve(cache._results);
    });
    return dfd.promise();
  }

  //startNewSeason
  startNewSeason() {
    //call to create new season
    //call for teams
    //create schedule
  }

  //pull the schedule and results
  getScheduleWithResults() {
    var dfd = jQuery.Deferred();
    this.loading = true;
    var cache = this;
    cache.getTeams(true).then(function(teams) {
      cache.getSchedule(true).then(function(schedule) {
        cache.getResults().then(function(gameResults) {
          console.log(gameResults, schedule)
          var results = _.map(schedule, function(week) {
            var games = _.map(week.games, function(game) {
              var result = _.find(gameResults, function(gameResult) {
                return gameResult.game_id == game.game_id;
              });
              var returnObject = {
                home_team: teams[game.home_team],
                away_team: teams[game.away_team]
              }
              if (result) {
                returnObject.results = true;
                returnObject.toBePlayed = false;
                returnObject.home_score = result.home_score;
                returnObject.away_score = result.away_score;
              } else {
                returnObject.toBePlayed = true;
                returnObject.results = false;
              }
              return returnObject;
                
            });
            return {
              week: week.week,
              games: games
            }
          });
          cache.loading = false;
          dfd.resolve(results);
        });
      });
    });
    return dfd.promise();
  }

  getNextGame(teamId) {
    var dfd = jQuery.Deferred();
    this.loading = true;
    var cache = this;
    $.getJSON("/api/league/1/schedule/team/{0}/next".format(teamId), function(nextGame) {
      cache.loading = false;
      dfd.resolve(nextGame);
    });
    return dfd.promise();
  }


  getLastGame(teamId) {
    var dfd = jQuery.Deferred();
    this.loading = true;
    var cache = this;
    $.getJSON("/api/league/1/results/team/{0}/last".format(teamId), function(lastGame) {
      cache.loading = false;
      dfd.resolve(lastGame);
    });
    return dfd.promise();
  }

  getGameState() {
    var dfd = $.Deferred();
    this.loading = true;
    var cache = this;
    //one day this will be an ajax call
    var state = {
      leaguePhase: LEAGUE_PHASE.NEWGAME,
      team: null
    }

    if (state.team) {
      cache.getTeams(true).then(function(teams) {
        cache.team = team;
        state.team = cache.team;
        cache.loading = false;
        dfd.resolve(state);
      });
    } else {
      cache.loading = false;
      dfd.resolve(state);
    }

    return dfd.promise();
  }


  playNextWeek(week) {
    var dfd = jQuery.Deferred();
    this.loading = true;
    var cache = this;
    $.getJSON('/api/league/1/schedule/week/{0}/play'.format(week), function(data) {
      cache.loading = false;
      dfd.resolve();
    });
    return dfd.promise();
  }
}
