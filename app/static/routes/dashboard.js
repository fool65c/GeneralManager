function seasonDashboard() {
  $('div.content').load('templates/reqularSeasonDashboard.html', function(){
    function display() {
      var self = this;

      //team block
      self.team = ko.observable({});
      //next Game block
      self.nextGame = ko.observable();
      self.showPlayWeek = ko.observable(false);
      self.byeWeek = ko.observable(false);
      self.startPlayoffs = ko.observable(false);
      //last Game block
      self.lastGame = ko.observable();
      self.lastWeekResult = ko.observable("");
      self.wasByeWeek = ko.observable(false);

      function updateDashboard() {
        api.getTeam().then(function(team) {
          self.team(team);
        });

        api.getNextWeek(gameState.state.team.id).then(function(nextWeek) {
          if (nextWeek == "Bye Week") {
            self.showPlayWeek(true);
            self.byeWeek(true);
            self.startPlayoffs(false);
            self.nextGame([]);
          } else if (nextWeek == "Regular Season is Over") {
            self.showPlayWeek(false);
            self.byeWeek(false);
            self.startPlayoffs(true);
            self.nextGame([]);
          } else {
            self.showPlayWeek(true);
            self.startPlayoffs(false);
            self.byeWeek(false);
            self.nextGame([nextWeek.game]);
          }
        });

        api.getLastWeek(gameState.state.team.id).then(function(lastWeek) {
            console.log(lastWeek)

          if (lastWeek == "Bye Week") {
            self.wasByeWeek(true);
            self.lastWeekResult("");
            self.lastGame([]);
          } else if (lastWeek == "Season not started") {
            self.wasByeWeek(false);
            self.lastWeekResult("");
            self.lastGame([]);
          } else {
            self.wasByeWeek(false);
            if (lastWeek.game.home.id == gameState.state.team.id) {
              self.lastWeekResult(lastWeek.result.home_score > lastWeek.result.away_score ? "Win" : "Loss");
            } else {
              self.lastWeekResult(lastWeek.result.home_score < lastWeek.result.away_score ? "Win" : "Loss");
            }
            self.lastGame([lastWeek]);
          }
        });
      }

      updateDashboard();

      self.playNextWeek = function() {
        api.playNextWeek().then(function() { updateDashboard(); });
      }
    }
    ko.applyBindings(new display(), document.getElementById('regularSeasonDashboard'));
  });
}
