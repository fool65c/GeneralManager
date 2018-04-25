function routeNewGame() { 
  api.getTeams().then(function (teams) {
    $('div.content').load('templates/newGame.html', function(){
      console.log(teams)

      function display() {
        var self = this;
        self.teams = teams;
        self.resularSeason = false;
        self.selectTeam = function(team) { 
          api.setTeam(team.id).then(function() {
            gameState.advance();
          });
        }
      }

      ko.applyBindings(new display(), document.getElementById('newGame'));
    });
  });
}
