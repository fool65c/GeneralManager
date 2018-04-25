function rankings() { 
  $('div.content').load('templates/rankings.html', function(){
    
    api.getTeamRankings().then(function(rankings) {
      var viewModel = {
        rankings: ko.observableArray(rankings)
      }
      ko.applyBindings(viewModel, document.getElementById('rankings'));

    });
  });
}
