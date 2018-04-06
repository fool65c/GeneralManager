function seasonDashboard() {
  $('div.content').load('templates/reqularSeasonDashboard.html', function(){
    function display() {
      var self = this;

      gameState.setMenu([
        { href: '#/regularSeason',
          text: 'Dashboard'
        },
        {
          href: '#/fullSchedule',
          text: 'Schedule'
        },
        {
          href: '#/rankings',
          text: 'Rankings'
        }
      ]);

      //team block
      self.team = ko.observable({});
      //next Game block
      self.nextGame = ko.observable();
      self.showPlayWeek = ko.observable(false);
      self.byeWeek = ko.observable(false);
      self.startPlayoffs = ko.observable(false);
      //last Game block
      self.lastGame = ko.observable();
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
            self.lastGame([]);
          } else if (lastWeek == "Season not started") {
            self.wasByeWeek(false);
            self.lastGame([]);
          } else {
            self.wasByeWeek(false);
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
