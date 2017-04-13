var app = angular.module('weebl');
app.controller('bugController', [
    '$scope', '$rootScope', '$q', '$rootScope', '$routeParams', 'data', 'DataService', 'graphFactory', 'Common',
    function($scope, $rootScope, $q, $rootScope, $routeParams, data, DataService, graphFactory, Common) {
        binding = this;

        $scope.data.individualBug = {};
        $scope.data.individualBug.bugId = $routeParams.bugId;
        $scope = Common.initialise($scope);
        $rootScope.data.show_reports_filters = false;
        $rootScope.data.show_filters = false;
        $rootScope.data.show_search = false;

        $scope.data.individualBug.plotData = {};
        $scope.data.individualBug.regex = DataService.refresh(
            'knownbugregex', $scope.data.user, $scope.data.apikey).get(
                {"bug__bugtrackerbug__bug_number": $scope.data.individualBug.bugId});
        $scope.data.individualBug.testRuns = DataService.refresh(
            'pipeline', $scope.data.user, $scope.data.apikey).get(
                {"builds__testcaseinstances__bugoccurrences__knownbugregex__bug__bugtrackerbug__bug_number": $scope.data.individualBug.bugId});

        function getBugOccurrences() {
            console.log("Updating bug occurrence plot to use " + $scope.data.subfilterPlotForm.grouping + " data");
            params = {"bugtrackerbug__bug_number": $scope.data.individualBug.bugId,
                      "historical_bugoccurrences_grouping": $scope.data.subfilterPlotForm.grouping};
            $scope.data.individualBug.plotData = DataService.refresh(
                'bug', $scope.data.user, $scope.data.apikey).get(params);
        };

        function plotBugOccurrences() {
            $q.all([
                $scope.data.individualBug.regex.$promise,
                $scope.data.individualBug.plotData.$promise,
            ]).then(function() {
                var description = ""
                if (angular.isDefined($scope.data.individualBug.regex.objects)) {
                    var description = $scope.data.individualBug.regex.objects[0].bug.description;
                };
                if ($scope.data.individualBug.plotData.$resolved) {
                    var plotData = padMissingDates($scope.data.individualBug.plotData.objects[0]['historical_bugoccurrences']);
                    var maxNum = 0;
                    var minDate = new Date(new Date().setMonth(new Date().getMonth() - 3)).getTime(); // default to 3 months ago
                    for (i = 0; i < plotData.length; i++) {
                        maxNum = Math.max(maxNum, plotData[i].count);
                        minDate = Math.min(minDate, new Date(plotData[i].date).getTime());
                    };
                    graphFactory.plotBugHistoryGraph(binding, {
                        'title': "Recent bug history for " + $scope.data.individualBug.bugId,
                        'subtitle': "",
                        'bugnumber': $scope.data.individualBug.bugId,
                        'description': description,
                        'data': plotData,
                        'maxNum': maxNum,
                        'minDate': minDate});
                };
            });
        };

        function padMissingDates(originalPlotData) {
            var plotData = [];
            var grouping = $scope.data.subfilterPlotForm.grouping;
            var prevDate;
            for (i = 0; i < originalPlotData.length; i++) {
                var date = new Date(originalPlotData[i].date);
                if (i > 0) {
                    //iterate over a range based on chosen 'day' or 'month' if we are not the
                    //first data point
                    var intermediateDateRange = d3.time[grouping].range(prevDate, date);
                    for (n = 1; n < intermediateDateRange.length; n++) {
                        var dateString = d3.time.format("%Y-%m-%dT00:00:00")(intermediateDateRange[n]);
                        plotData.push({count: 0, date: dateString});
                    }
                }
                plotData.push(originalPlotData[i]);
                prevDate = date;
            }
            return plotData;
        };

        $scope.data.humaniseDate = Common.humaniseDate;

        $scope.data.subfilterPlotForm.grouping = 'day';
        $scope.$watch('data.subfilterPlotForm.grouping', function(grouping) {
            getBugOccurrences();
            plotBugOccurrences();
        });
    }]);
