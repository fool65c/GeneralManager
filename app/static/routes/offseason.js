function offseason() { 
  $('div.content').load('templates/offseason.html', function(){
    function display() {
      var self = this;
    }

    ko.applyBindings(new display(), document.getElementById('offseason'));
  });
}
