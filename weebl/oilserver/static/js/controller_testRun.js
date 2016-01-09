var app = angular.module('weebl');
app.controller('testRunController', [
    '$scope', '$rootScope', '$routeParams', 'data', 'DataService', 'Common',
    function($scope, $rootScope, $routeParams, data, DataService, Common) {
        for (var datum in $scope.data) {
            data[datum] = $scope.data[datum]
        };
        $scope.data = data;

        $scope.data.testRunId = $routeParams.testRunId;
        $scope.data.show_filters = false;
        $scope.data.show_search = false;
        $scope.data.individual_testRun = DataService.refresh(
                'pipeline', $scope.data.user, $scope.data.apikey).get({"uuid": $scope.data.testRunId});

        active_filters_for_bug = Common.generateActiveFilters($scope, 'bug');
        active_filters_for_bug['knownbugregex__bugoccurrences__build__pipeline__uuid'] = $scope.data.testRunId;
        $scope.data.bugs_affecting_pipeline = DataService.refresh(
            'bug', $scope.data.user, $scope.data.apikey).get(active_filters_for_bug);

        active_filters_for_build = Common.generateActiveFilters($scope, 'build');
        active_filters_for_build['pipeline__uuid'] = $scope.data.testRunId;
        $scope.data.pipeline_builds = DataService.refresh(
            'build', $scope.data.user, $scope.data.apikey).get(active_filters_for_build);
        $scope.data.this_environment = DataService.refresh(
                'environment', $scope.data.user, $scope.data.apikey).get(
                {"jenkins__buildexecutor__pipeline__uuid": $scope.data.testRunId});
    }]);