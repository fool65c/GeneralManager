function offseason() { 
  $('div.content').load('templates/offseason.html', function(){
    api.getPlayersRetiring().then(function(retirees) {
      var self = this;
        self.retirees = ko.observableArray([]);
      function display() {
        console.log(retirees)
        self.retirees(retirees)
      }

      ko.applyBindings(new display(), document.getElementById('offseason'));
    });
  });
}
