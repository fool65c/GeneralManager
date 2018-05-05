function freeAgency() { 
  $('div.content').load('templates/freeAgents.html', function(){
    
    function display() {
      var self = this;

      self.roster = ko.observable();
      self.needs = ko.observableArray();

      api.getFormations().then(function(formations) {
        api.getTeamRoster(gameState.state.team.id).then(function(roster) {
          roster = _.filter(roster, function(player) { return player.starter });
          roster = _.countBy(roster, function(player) { return player.position.shortName });
          console.log(roster)
          needs = {};
          _.each(formations, function(positions) {
            _.each(positions, function(need, position) {
              if (roster[position]) {
                needs[position] = need - roster[position];
              } else {
                needs[position] = need
              }
            })
          });
          console.log(needs)

        });
      });
      
      api.getFreeAgents().then(function(roster) {
        console.log(_.groupBy(roster, function(player) { return player.position.shortName}));
        self.roster(_.sortBy(roster, function(player) { return player.last_name }));
      });
    }

    ko.applyBindings(new display(), document.getElementById('free-agents'));
  });
}
