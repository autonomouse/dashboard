var app = angular.module('weebl', ['nvd3', 'ngResource', 'ngRoute']);

app.config(function ($routeProvider) {
    $routeProvider
        .when('/results/successRate', {
            reloadOnSearch: false,
            templateUrl: '/static/partials/successRate.html',
            controller: 'successRateController',
            controllerAs:'successRate'
        })
        .when('/results/bugs', {
            reloadOnSearch: false,
            templateUrl: '/static/partials/bugs.html',
            controller: 'successRateController',
            controllerAs:'successRate'
        })
        .when('/results/bug/:bugId', {
            reloadOnSearch: false,
            templateUrl: '/static/partials/individualBug.html',
            controller: 'bugController',
            controllerAs:'bug'
        })
        .when('/results/testRuns', {
            reloadOnSearch: false,
            templateUrl: '/static/partials/testRuns.html',
            controller: 'successRateController',
            controllerAs:'successRate'
        })
        .when('/results/testRun/:testRunId', {
            reloadOnSearch: false,
            templateUrl: '/static/partials/individualTestRun.html',
            controller: 'testRunController',
            controllerAs:'testRun'
        })
        .when('/results', {
            reloadOnSearch: false,
            redirectTo: '/results/successRate'
        })
        .when('/reports/detailed', {
            reloadOnSearch: false,
            templateUrl: '/static/partials/detailed.html',
            controller: 'detailedReportController',
            controllerAs: 'detailedReport'
        })
        .when('/reports/overview', {
            reloadOnSearch: false,
            templateUrl: '/static/partials/overview.html',
            controller: 'overviewReportController',
            controllerAs: 'overviewReport'
        })
        .when('/reports', {
            reloadOnSearch: false,
            redirectTo: '/reports/overview'
        })
        .when('/throughput/scheduler', {
            reloadOnSearch: false,
            templateUrl: '/static/partials/scheduler.html',
            controller: 'schedulerController',
            controllerAs:'scheduler'
        })
        .when('/throughput', {
            reloadOnSearch: false,
            redirectTo: '/throughput/scheduler'
        })
        .when('/qa/overview', {
            reloadOnSearch: false,
            templateUrl: '/static/partials/qa_overview.html',
            controller: 'qaOverviewController',
            controllerAs:'qaOverview'
        })
        .otherwise({
            redirectTo: '/qa/overview'
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
