function rankings() { 
  $('div.content').load('templates/rankings.html', function(){
    function display() {
      var self = this;

      self.rankings = ko.observable();

      api.getTeamRankings().then(function(rankings) {
        console.log(rankings);
        self.rankings(rankings);
      });
    }

    ko.applyBindings(new display(), document.getElementById('rankings'));
  });
}
