function offseason() { 
  $('div.content').load('templates/offseason.html', function(){
    api.getPlayersRetiring().then(function(retirees) {
      function display() {
        var self = this;
        self.retirees = ko.observableArray(retirees);
      }

      ko.applyBindings(new display(), document.getElementById('offseason'));
    });
  });
}
