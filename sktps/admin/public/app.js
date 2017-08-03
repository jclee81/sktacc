'use strict';

const app = angular.module('admin', [
  'ngRoute', 'btford.socket-io'
]);

app.config([
  '$locationProvider',
  '$routeProvider',
  function ($locationProvider, $routeProvider) {
    $routeProvider
      .when('/', {
        templateUrl: 'src/manage.html',
        controller: 'ManageController',
      })
      .otherwise({
        redirectTo: '/'
      });
  }
]);

app.constant('PS_SERVER', `http://${config.psServerHost}:${config.psServerPort}`);

// TODO PS socket connect
//app.factory('socket', function (socketFactory, GAME_SERVER) {
//  return socketFactory({
//    ioSocket: io.connect(GAME_SERVER, { transports: ['websocket'] })
//  });
//});
