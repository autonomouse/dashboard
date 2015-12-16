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

    }]);
