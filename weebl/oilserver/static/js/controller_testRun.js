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

        active_filters_for_bug = {}
        active_filters_for_bug['knownbugregex__bugoccurrences__build__pipeline__uuid'] = $scope.data.testRunId;
        $scope.data.bugs_affecting_pipeline = DataService.refresh(
            'bug', $scope.data.user, $scope.data.apikey).get(active_filters_for_bug);

        active_filters_for_build = {}
        active_filters_for_build['pipeline__uuid'] = $scope.data.testRunId;
        $scope.data.pipeline_builds = DataService.refresh(
            'build', $scope.data.user, $scope.data.apikey).get(active_filters_for_build);

        active_filters_for_machine = {}
        active_filters_for_machine['machineconfiguration__pipeline__uuid'] = $scope.data.testRunId;
        $scope.data.pipeline_machines = DataService.refresh(
            'machine', $scope.data.user, $scope.data.apikey).get(active_filters_for_machine);

	$scope.data.image = Common.getBundleImageLocation($scope.data.testRunId)

        $scope.data.jobtypeLookup = function(jobname) {
            return Common.jobtypeLookup(jobname);
        };
    }]);
