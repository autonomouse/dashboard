var app = angular.module('weebl');
app.controller('qaReleaseController', [
    '$scope', '$q', 'DataService', 'Common',
    function($scope, $q, DataService, Common) {
        if (angular.isUndefined($scope.data))
            $scope.data = data;

        binding = this;
        binding.user = $scope.data.user;
        binding.apikey = $scope.data.apikey;
        $scope = Common.initialise($scope);

        $scope.data.reports.show_filters = false;
        $scope.data.results.show_filters = false;
        $scope.data.qa.show_filters = false;
        $scope.data.results.show_search = false;
        $scope.data.qa.show_search = false;

        $scope.data.reportCalendarCharts = []

        $scope.data.reportCalendarCharts = {};

        var daysInWeek = 7;
        var gap = 25;
        var NoDaysBeforeCriticallyLate = 15;
        var _MS_PER_DAY = 1000 * 60 * 60 * 24;
        var earliestYear = null;
        var latestYear = null;

        $scope.data.humaniseDate = Common.humaniseDate;

        function buildProductGraphDict(product) {
            $scope.data.reportCalendarCharts[product] = {
                type: 'Calendar',
                data: {
                    cols: [
                        { type: 'date', id: 'date' },
                        { type: 'number', id: 'amount' } ],
                    rows: []
                },
                options: {
                    title: product.charAt(0).toUpperCase() + product.slice(1) + ' Release Dates',
                    colorAxis: {maxValue: 0,
                                minValue: -NoDaysBeforeCriticallyLate,
                                values: [-15, -10, -5, 0, 5],
                                colors: ['red', 'orange', '#ffbf00', '#9ACD32', '#00FF00'],
                    },
                    width: 1000,
                }
            };
        };

        function calcNumberOfYears(earliestYear, latestYear) {
            return (latestYear - earliestYear) + 1;
        };

        function calculateDelta(plannedrelease, actualrelease) {
            date1 = new Date(plannedrelease);
            date2 = new Date(actualrelease);

            var delta = Math.floor((
                Date.UTC(date1.getFullYear(), date1.getMonth(), date1.getDate()) -
                Date.UTC(date2.getFullYear(), date2.getMonth(), date2.getDate())
                ) / _MS_PER_DAY);
            return delta > -1 ? 0 : delta;
        };

        function calcDeltas(release) {
            var name = release.producttypeversion.producttype.name;
            if (angular.isDefined($scope.data.qa.tracked_products[name]['releases'].final)) {
                var releases = $scope.data.qa.tracked_products[name]['releases'];
                for (ptype in releases) {
                    for (idx in releases[ptype].releasedates) {
                        var plannedrelease = releases[ptype].releasedates[idx][0];
                        var actualrelease = $scope.data.qa.tracked_products[name]['releases'].final.releasedates[0][0];
                        var delta = calculateDelta(plannedrelease, actualrelease);
                        $scope.data.reportCalendarCharts[name].data.rows.push(
                            {c: [
                                {v: new Date(releases[ptype].releasedates[idx][0])},
                                {v: delta} ]
                            }
                        );
                        releases[ptype].releasedates[idx][1] = delta;
                    };
                };
            }
        };

        $scope.data.qa.tracked_products = {}
        $q.all([
            DataService.refresh('release', $scope.data.user, $scope.data.apikey).get({}).$promise
        ]).then(function([releases]) {
            for (idx in releases.objects) {
                release = releases.objects[idx];
                var product = release.producttypeversion.producttype.name;
                if (angular.isUndefined($scope.data.qa.tracked_products[product]))
                    $scope.data.qa.tracked_products[product] = {}
                $scope.data.qa.tracked_products[product]['name'] = product;
                $scope.data.qa.tracked_products[product]['show'] = release.show;
                $scope.data.qa.tracked_products[product]['tracking'] = release.tracking;
                $scope.data.qa.tracked_products[product]['trackedversion'] = release.producttypeversion.version;
                if (angular.isUndefined($scope.data.qa.tracked_products[product]['releases']))
                    $scope.data.qa.tracked_products[product]['releases'] = {};
                if (angular.isUndefined($scope.data.qa.tracked_products[product]['releases'][release.releasetype.name]))
                    $scope.data.qa.tracked_products[product]['releases'][release.releasetype.name] = {};
                $scope.data.qa.tracked_products[product]['releases'][release.releasetype.name]['releasetype'] = release.releasetype.name;
                if (angular.isUndefined($scope.data.qa.tracked_products[product]['releases'][release.releasetype.name]['releasedates'])) {
                    $scope.data.qa.tracked_products[product]['releases'][release.releasetype.name]['releasedates'] = []
                };
                if (release.actualrelease) {
                    $scope.data.qa.tracked_products[product]['releases'][release.releasetype.name]['actualrelease'] = release.releasedate;
                } else {
                    $scope.data.qa.tracked_products[product]['releases'][release.releasetype.name]['releasedates'].push([release.releasedate, 0]);
                };

                this_date = new Date(release.releasedate).getFullYear()
                if ((this_date > latestYear) || (latestYear === null)) {
                    latestYear = this_date
                };
                if ((this_date < earliestYear) || (earliestYear === null)) {
                    earliestYear = this_date
                };
                buildProductGraphDict(product);
                calcDeltas(release);
            };
            $scope.data.reportCalendarCharts[product].options.height = (
                calcNumberOfYears(earliestYear, latestYear) * daysInWeek * gap);
        });
    }]);
