function routeDepthChart() { 
  $('div.content').load('templates/depthChart.html', function(){
    var offensivePositions = ['QB', 'RB', 'WR', 'TE', 'OL']
    var defensivePositions = ['DL', 'LB', 'DB']
    var specialTeamsPositions = ['K', 'P']
    function display() {
      var self = this;

      self.roster = ko.observable();
      self.positions = ko.observable([]);
      self.activeChart = ko.observable('offense');

      self.setOffensiveChart = function() {
        self.positions(offensivePositions)
        self.activeChart('offense')
      }
      self.setDefensiveChart = function() {
        self.positions(defensivePositions)
        self.activeChart('defense')
      }
      self.setSpecialTeamsChart = function() {
        self.positions(specialTeamsPositions)
        self.activeChart('st')
      }

      api.getTeamRoster(gameState.state.team.id).then(function(roster) {
        console.log(_.groupBy(roster, function(player) {return player.position.shortName}));
        roster = _.filter(roster, function(player) { return player.starter });
        roster = _.sortBy(roster, function(player) { return -player.level });
        self.roster(_.groupBy(roster, function(player) {return player.position.shortName}));
        self.positions(offensivePositions);

      });
    }

    ko.applyBindings(new display(), document.getElementById('depth-chart'));
  });
}
