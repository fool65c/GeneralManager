class GeneralManagerRestApi {
  constructor() {
    this.loading = false;
  }

  getTeam() {
    return this.getJSON('/api/state', function(data) { return data.team });
  }

  getTeams() {
    return this.getJSON('/api/team');
  }

  getTeamRoster(team_id) {
    return this.getJSON('/api/team/{0}/roster'.format(team_id));
  }

  setTeam(team_id) {
    return this.postJSON('/api/team', {"team_id": team_id})
  }

  getTeamRankings() {
    return this.getJSON('/api/rankings');
  }

  getSchedule() {
    return this.getJSON('/api/schedule');
  }

  getTeamSchedule(team_id) {
    return this.getJSON('/api/schedule/{0}'.format(team_id));
  }

  playRegularSeason() {
    return this.getJSON('/api/schedule/play');
  }

  playNextWeek() {
    return this.getJSON('/api/schedule/nextWeek/play');
  }

  getNextWeek(team_id) {
    return this.getJSON('/api/schedule/nextWeek/{0}'.format(team_id));
  }

  getLastWeek(team_id) {
    return this.getJSON('/api/schedule/lastWeek/{0}'.format(team_id));
  }

  getPlayoffs() {
    return this.getJSON('/api/playoff');
  }

  playNextPlayoffWeek() {
    return this.getJSON('/api/playoff/play');
  }

  getPhases() {
    return this.getJSON('/api/state/phase');
  }

  getState() {
    return this.getJSON('/api/state');
  }


  // helper function to get JSON
  getJSON(url, func) {
    var dfd = jQuery.Deferred();
    $.getJSON(url, function(response, textStatus, xhr) {
      if (func) {
        dfd.resolve(func(response, xhr.status));
      } else {
        dfd.resolve(response);
      }
    });
    return dfd.promise()
  }

  //helper function to POST JSON
  postJSON(url, data, func) {
    var dfd = jQuery.Deferred();
    $.ajax({
      url: url, 
      data: JSON.stringify(data),
      type: 'POST',
      success: function(response) {
        if (func) {
          dfd.resolve(func(response));
        } else {
          dfd.resolve(response);
        }
        }, 
      contentType: 'application/json',
      dataType: 'json'});

    return dfd.promise()
  }

}
