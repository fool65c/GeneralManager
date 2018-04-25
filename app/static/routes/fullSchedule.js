function routeFullSchedule() { 
  $('div.content').load('templates/fullSchedule.html', function(){
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
        api.getSchedule().then(function(schedule) {
          schedule = _.groupBy(schedule, function(sch) { return sch.week });
          console.log(_.values(schedule))
          self.schedule(schedule);
          self.weeksLeft(_.chain(schedule).filter(function(week){
            return _.chain(week).filter(function(game) {
              return game.result == null;
            }).size().value() > 0
          }).size().value());
        });
      }

      updateSchedule();
    }

    ko.applyBindings(new display(), document.getElementById('fullSchedule'));
  });
}
