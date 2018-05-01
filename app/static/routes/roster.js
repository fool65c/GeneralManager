function routeTeamRoster() { 
  $('div.content').load('templates/roster.html', function(){
    
    function display() {
      var self = this;

      self.roster = ko.observable();
      api.getTeamRoster(gameState.state.team.id).then(function(roster) {
        console.log(roster)
        self.roster(_.sortBy(roster, function(player) { return player.last_name }));
      });
    }

    ko.applyBindings(new display(), document.getElementById('roster'));
  });
}
