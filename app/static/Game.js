class Game {
  constructor() {
    this.state = {};
    this.menuFunction = function() { return false; }
    var game = this;
    this.menu = ko.observable();

    var navControl = {
      menu: game.menu
    }

    ko.applyBindings(navControl, document.getElementById('navagaion'));
  }

  setMenu(menu) {
    this.menu(menu);
  }

  start() {
    var game = this;
    $(document).ready(function() {

      hasher.setHash('');
      crossroads.resetState();

      game.advance();
    });
  }  

  advance() {
    var game = this;
    api.getState().then(function(state) {
      console.log(state);
      game.state = state;
      hasher.setHash(state.phase.route);
    });
  }
}
