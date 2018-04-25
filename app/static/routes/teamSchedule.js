function routeTeamSchedule() { 
  $('div.content').load('templates/teamSchedule.html', function(){
    
    function display() {
      var self = this;

      self.schedule = ko.observable();
      self.weeksLeft = ko.observable();

      self.playEntireSeason = function() {
        api.playRegularSeason().then(function() {
          updateSchedule();
        });
      }

      function updateSchedule() {
        api.getTeamSchedule(gameState.state.team.id).then(function(schedule) {
          console.log(schedule)
          weeksLeft = 0
          schedule = _.map(schedule, function(s){ 
            home = s.game.game.home.city;
            away = s.game.game.away.city;
            result = ""
            if (s.game.result) {
              home += " " + s.game.result.home_score;
              away += " " + s.game.result.away_score;
              if (s.game.game.home.id = gameState.state.team.id) {
                result = s.game.result.home_score > s.game.result.away_score ? "Win" : "Loss";
              } else {
                result = s.game.result.home_score < s.game.result.away_score ? "Win" : "Loss";
              }
            } else {
              weeksLeft += 1
            }
            
            return {
              'week': s.week,
              'game': {
                'home': home,
                'away': away
              },
              'result': result
            }
          });
          self.schedule(schedule);
          self.weeksLeft(weeksLeft)
        });
      }

      updateSchedule();
    }

    ko.applyBindings(new display(), document.getElementById('fullSchedule'));
  });
}
