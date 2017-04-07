var app = angular.module('weebl');
app.controller('pdfReportController', [
    '$scope',
    function($scope) {
        $scope.generatePDF = function() {
            $scope.data.pdf_content = angular.element("#content-block").html();
        };
  }]);
