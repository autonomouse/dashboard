var app = angular.module('weebl', ['nvd3', 'ngResource', 'ngRoute']);

app.config(function ($routeProvider) {
    $routeProvider
        .when('/successRate', {
            templateUrl: '/static/partials/successRate.html',
            controller: 'successRateController',
            controllerAs:'successRate'
        })
        .when('/bugs', {
            templateUrl: '/static/partials/bugs.html',
            controller: 'successRateController',
            controllerAs:'successRate'
        })
        .when('/testRuns', {
            templateUrl: '/static/partials/testRuns.html',
            controller: 'successRateController',
            controllerAs:'successRate'
        })
        .when('/testRun/:testRunId', {
            templateUrl: '/static/partials/individualTestRun.html',
            controller: 'testRunController',
            controllerAs:'testRun'
        })
        .otherwise({
            redirectTo: '/successRate'
        });
  });
