function routeTeamRoster() { 
  $('div.content').load('templates/roster.html', function(){
    
    function display() {
      var self = this;

      self.roster = ko.observable();
      api.getTeamRoster(gameState.state.team.id).then(function(roster) {
        console.log(roster)
        displayRoster = []
        _.each(roster, function(positionGroup, starter) {
          _.each(positionGroup, function(players, position) {
            _.each(players, function(player) {
              console.log(player)
              displayRoster.push({
                'position': position,
                'name': player.name,
                'age': player.age,
                'skill': player.skill,
                'speed': player.speed,
                'strength': player.strength,
                'starter': starter
              });
            });
          });
        });
        console.log(displayRoster)
        self.roster(_.sortBy(displayRoster, function(player) { return player.name }));
      });
    }

    ko.applyBindings(new display(), document.getElementById('roster'));
  });
}
