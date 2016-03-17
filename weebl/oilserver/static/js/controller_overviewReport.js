var app = angular.module('weebl');
app.controller('overviewReportController', [
    '$scope', 'SearchFactory', 'Common',
    function($scope, SearchFactory, Common) {
        $scope = Common.initialise($scope);
        if(angular.isUndefined($scope.data.reports.search)) $scope.data.reports.search = new SearchFactory.Search();
        $scope.data.reports.show_filters = true;
        $scope.data.results.show_filters = false;
        $scope.data.results.show_search = false;
    }]);
