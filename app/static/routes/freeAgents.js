function freeAgency() { 
  var playersSigned = {};
  var originalNeed = {};

  $('div.content').load('templates/freeAgents.html', function(){
    
    function display() {
      var self = this;

      self.freeAgents = ko.observable();
      self.needs = ko.observableArray();

      api.getFormations().then(function(formations) {
        api.getTeamRoster(gameState.state.team.id).then(function(roster) {
          roster = _.filter(roster, function(player) { return player.starter });
          roster = _.countBy(roster, function(player) { return player.position.shortName });
          needs = [];
          _.each(formations, function(positions) {
            _.each(positions, function(need, position) {
              if (roster[position]) {
                needs.push({
                  'position': position,
                  'need': need - roster[position]
                });
                originalNeed[position] = need - roster[position]
              } else {
                needs.push({
                  'position': position,
                  'need': need
                });
                originalNeed[position] = need
              }
            })
          });
          self.needs(needs)

        });
      });
      
      api.getFreeAgents().then(function(freeAgents) {
        freeAgents = _.sortBy(freeAgents, function(player) { return player.last_name });
        freeAgents = _.sortBy(freeAgents, function(player) { return player.position.shortName});
        self.freeAgents(freeAgents);
      });

      signPlayers = function() {
        api.signFreeAgents(playersSigned).then(function() {
          gameState.advance();
        });
      }

      playerClicked = function(player, event) {
        var adjustNeed = 0;
        if (event.target.checked) {
          playersSigned[player.id] = player
        } else {
          delete playersSigned[player.id]
        }

        if (originalNeed[player.position.shortName] > 0) {
          adjustNeed = originalNeed[player.position.shortName] - _.reduce(playersSigned, function(memo, p) { 
            return p.position.shortName == player.position.shortName ? memo + 1 : memo 
            }, 0);
          adjustNeed = adjustNeed < 0 ? 0 : adjustNeed;
          needIndex = _.findIndex(self.needs(), { 'position': player.position.shortName });
          self.needs.replace(self.needs()[needIndex], {
            position: self.needs()[needIndex].position,
            need: adjustNeed
          });
        }

        return true;
      }
    }
    ko.applyBindings(new display(), document.getElementById('free-agents'));
  });
}
