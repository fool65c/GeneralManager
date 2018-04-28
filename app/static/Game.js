gameState = {}

gameState.menu = ko.observable();
ko.applyBindings({menu: gameState.menu}, document.getElementById('navagaion'));

gameState.start = function() {
  $(document).ready(function() {
    hasher.setHash('');
    crossroads.resetState();
    gameState.advance();
  });
}  
  
gameState.advance = function() {
  api.getState().then(function(state) {
    console.log(state);
    gameState.state = state;
    gameState.updateMenu();
    hasher.setHash(state.phase.route);
  });
}

gameState.updateMenu= function() {
  var newMenu;
  switch(gameState.state.phase.phase) {
    case "NEWGAME":
      newMenu = [{ href: '#/newGame', text: 'Select Team'}];
      break;
    case "REGULARSEASON":
      newMenu = [
        {href: '#/regularSeason', text: 'Dashboard'},
        {text: 'Team', items: [
          {href: '#/teamRoster', text: 'Roster'},
          {href: '#/teamSchedule', text: 'Schedule'}
        ]},
        {text: 'League', items: [
          {href: '#/fullSchedule', text: 'Schedule'},
          {href: '#/rankings', text: 'Rankings'}
        ]}
      ];
      break;
    case "POSTSEASON":
      newMenu = [
        { href: '#/playoffs', text: 'Playoffs'},
        { href: '#/rankings', text: 'Rankings'}
      ];
      break;
    default:
      newMenu = [];
      break;
  }
  this.menu(newMenu);
}
