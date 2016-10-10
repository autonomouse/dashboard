var app = angular.module('weebl');
app.controller('locationController', [
    '$scope', '$location', 'data',
    function($scope, $location, data) {
        $scope.$on("$locationChangeSuccess", function (event, newUrl, oldUrl) {
            $scope.data.absURI = encodeURIComponent($location.absUrl());
        });
    }]);
