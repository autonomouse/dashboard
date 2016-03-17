var app = angular.module('weebl');
app.controller('overviewReportController', [
    '$scope', 'SearchFactory', 'DataService', 'Common',
    function($scope, SearchFactory, DataService, Common) {
        $scope = Common.initialise($scope);
        if(angular.isUndefined($scope.data.reports.search)) $scope.data.reports.search = new SearchFactory.Search();
        $scope.data.reports.show_filters = true;
        $scope.data.results.show_filters = false;
        $scope.data.results.show_search = false;

	$scope.data.reports.search.defaultFilters = {"date": "All Time"};
	$scope.data.reports.search.individualFilters = ["date", "report"];
	$scope.data.reports.search.update();

        if(angular.isUndefined($scope.data.reports.metadata)) $scope.data.reports.metadata = {};

        function getMetadata() {
            $scope.data.reports.metadata.reportPeriods = DataService.refresh(
                'reportperiod', $scope.data.user, $scope.data.apikey).query({});
            $scope.data.reports.metadata.environments = DataService.refresh(
                'environment', $scope.data.user, $scope.data.apikey).query({});
            $scope.data.reports.metadata.reportGroups = DataService.refresh(
                'report', $scope.data.user, $scope.data.apikey).query({});
        }

        getMetadata();


    }]);
