function playoffs() { 
  api.getPlayoffs().then(function (playoffSchedule) {
    $('div.content').load('templates/playoffs.html', function(){
      console.log(playoffSchedule)



      function display() {
        var self = this;

        gameState.setMenu([
          { href: '#/playoffs', text: 'Playoffs'},
          { href: '#/rankings', text: 'Rankings'}
        ]);

        self.rounds = 4
        self.playoffsOver = ko.observable(false);

        self.updatePlayoffSchedule = function (playoffSchedule) {
          $('#playoffs').bracket({
            skipConsolationRound: true,
            teamWidth: 100,
            scoreWidth: 50,
            matchMargin: 50,
            init: playoffSchedule
          });
            
          console.log(playoffSchedule.results[self.rounds -1])
          if (self.rounds > playoffSchedule.results.length) {
            self.playoffsOver(false)
          } else if (playoffSchedule.results[self.rounds -1][0][0] == null) {
            self.playoffsOver(false)
          } else {
            self.playoffsOver(true)
          }
        } 

        self.playNextRound = function() { 
          api.playNextPlayoffWeek().then(function(playoffSchedule) {
            self.updatePlayoffSchedule(playoffSchedule);
          });
        }

        self.updatePlayoffSchedule(playoffSchedule);
      }

      ko.applyBindings(new display(), document.getElementById('playoffActions'));
    });
  });
}
