var app = angular.module('weebl');
app.controller('overviewReportController', [
    '$scope',
    function($scope) {
        $scope.data.show_filters = false;
        $scope.data.show_search = false;
    }]);
