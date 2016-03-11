var app = angular.module('weebl', ['nvd3', 'ngResource', 'ngRoute']);

app.config(function ($routeProvider) {
    $routeProvider
        .when('/results/successRate', {
            templateUrl: '/static/partials/successRate.html',
            controller: 'successRateController',
            controllerAs:'successRate'
        })
        .when('/results/bugs', {
            templateUrl: '/static/partials/bugs.html',
            controller: 'successRateController',
            controllerAs:'successRate'
        })
        .when('/results/testRuns', {
            templateUrl: '/static/partials/testRuns.html',
            controller: 'successRateController',
            controllerAs:'successRate'
        })
        .when('/results/testRun/:testRunId', {
            templateUrl: '/static/partials/individualTestRun.html',
            controller: 'testRunController',
            controllerAs:'testRun'
        })
        .when('/results', {
            redirectTo: '/results/successRate'
        })
        .when('/reports/overview', {
            templateUrl: '/static/partials/overview.html',
            controller: 'overviewReportController',
            controllerAs: 'overviewReport'
        })
        .when('/reports', {
            redirectTo: '/reports/overview'
        })
        .when('/triage', {
            redirectTo: '/triage/triage'
        })
        .otherwise({
            redirectTo: '/results/successRate'
        });
  });
