//setup crossroads
var routes = [
  {
    script: '/routes/newGame.js',
    route: '/newGame',
    function: 'routeNewGame'
  },
  {
    script: '/routes/fullSchedule.js',
    route: '/fullSchedule',
    function: 'routeFullSchedule'
  },
  {
    script: '/routes/roster.js',
    route: '/teamRoster',
    function: 'routeTeamRoster'
  },
  {
    script: '/routes/depthChart.js',
    route: '/depthChart',
    function: 'routeDepthChart'
  },
  {
    script: '/routes/teamSchedule.js',
    route: '/teamSchedule',
    function: 'routeTeamSchedule'
  },
  {
    script: '/routes/dashboard.js',
    route: '/dashboard',
    function: 'seasonDashboard'
  },
  {
    script: '/routes/dashboard.js',
    route: '/regularSeason',
    function: 'seasonDashboard'
  },
  {
    script: '/routes/rankings.js',
    route: '/rankings',
    function: 'rankings'
  },
  {
    script: '/routes/playoffs.js',
    route: '/playoffs',
    function: 'playoffs'
  },
  {
    script: '/routes/offseason.js',
    route: '/offseason',
    function: 'offseason'
  },
  {
    script: '/routes/freeAgents.js',
    route: '/freeAgency',
    function: 'freeAgency'
  }
]

_.forEach(routes, function(route) {
  $.getScript(route.script, function() {
    crossroads.addRoute(route.route, window[route.function]);
    routeComplete()
  });
})

//var home = crossroads.addRoute('/', function(){
//  $('div.content').html('')
//});
//
crossroads.addRoute('/startPostSeason', startPostSeason);

function startPostSeason() {
}


crossroads.routed.add(console.log, console); //log all routes

//setup hasher
function parseHash(newHash, oldHash){
  crossroads.parse(newHash);
}
hasher.initialized.add(parseHash); //parse initial hash
hasher.changed.add(parseHash); //parse hash changes
hasher.init(); //start listening for history change

var routesComplete = 0
function routeComplete() {
  routesComplete++;
  if (routesComplete == routes.length) {
    console.log("ALL ROUTES LOADED");
    console.log(crossroads._routes)
    gameState.start();
  }
}
