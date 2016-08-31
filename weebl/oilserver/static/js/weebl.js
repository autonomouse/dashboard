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
        .when('/results/bug/:bugId', {
            templateUrl: '/static/partials/individualBug.html',
            controller: 'bugController',
            controllerAs:'bug'
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
        .when('/throughput/scheduler', {
            templateUrl: '/static/partials/scheduler.html',
            controller: 'schedulerController',
            controllerAs:'scheduler'
        })
        .when('/throughput', {
            redirectTo: '/throughput/scheduler'
        })
        .otherwise({
            redirectTo: '/results/successRate'
        });
  });

app.directive('onErrorSrc', function() {
    return {
        link: function(scope, element, attrs) {
            element.bind('error', function() {
            if (attrs.src != attrs.onErrorSrc) {
                attrs.$set('src', attrs.onErrorSrc);
            }
            });
        }
    }
});
