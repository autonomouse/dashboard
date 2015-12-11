var app = angular.module('weebl');
app.controller('successRateController', [
    '$scope', '$rootScope', 'SearchService', 'DataService', 'graphFactory',
    function($scope, $rootScope, SearchService, DataService, graphFactory) {
        binding = this;
        binding.user = $scope.this.user;
        binding.apikey = $scope.this.apikey;
        $scope.filters = SearchService.getEmptyFilter();
        $scope.bugs = {};
        $scope.testRuns = {};
        $scope.metadata = {};
        $scope.regexes = {};

        $scope.tabs = {};

        $scope.tabs.successRate = {};
        $scope.tabs.successRate.pagetitle = "Success Rate";
        $scope.tabs.successRate.currentpage = "successRate";

        $scope.tabs.bugs = {};
        $scope.tabs.bugs.pagetitle = "Bugs";
        $scope.tabs.bugs.currentpage = "bugs";
        $scope.tabs.bugs.predicate = "occurrences";
        $scope.tabs.bugs.reverse = false;

        $scope.tabs.testRuns = {};
        $scope.tabs.testRuns.pagetitle = "Test Runs";
        $scope.tabs.testRuns.currentpage = "testRuns";
        $scope.tabs.testRuns.predicate = "completed_at";
        $scope.tabs.testRuns.reverse = false;

        $scope.tabs.individual_testRun = {};
        $scope.tabs.individual_testRun.pagetitle = "Individual Test Run";
        $scope.tabs.individual_testRun.currentpage = "individual_testRun";

        function generateActiveFilters(origin) {
            var active_filters = {};
            var field_to_filter = generateFilterPaths(origin);

            for (var enum_field in $scope.filters) {
                if (!(enum_field in $scope.metadata))
                    continue;

                enum_values = [];
                $scope.filters[enum_field].forEach(function(enum_value) {
                    enum_values.push(enum_value.substr(1));
                });

                // generate active filters from the perspective of origin:
                active_filters[field_to_filter[enum_field]] = enum_values;
            }
            // generate date active filters from the perspective of origin:
            if ($scope.start_date)
                active_filters[field_to_filter['completed_at__gte']] = $scope.start_date;
            if ($scope.finish_date)
                active_filters[field_to_filter['completed_at__lte']] = $scope.finish_date;

            return active_filters;
        }

        function prefixPathToFields(fields, path) {
            for (var field in fields) {
                fields[field] = path + fields[field];
            }
            return fields;
        };

        function generateFilterPaths(origin) {
            if (typeof(origin)==='undefined') origin = '';

            var model_fields = {
                'completed_at__gte': 'completed_at__gte',
                'completed_at__lte': 'completed_at__lte',
                'openstackversion': 'openstackversion__name__in',
                'ubuntuversion': 'ubuntuversion__name__in',
                'sdn': 'sdn__name__in',
                'compute': 'compute__name__in',
                'blockstorage': 'blockstorage__name__in',
                'imagestorage': 'imagestorage__name__in',
                'database': 'database__name__in',
                'environment': 'buildexecutor__jenkins__environment__name__in',
            };

            // add the path from the origin model to the fields needed:
            var prefixtures = {
                'bug': 'knownbugregex__bugoccurrences__build__pipeline__',
                'build': 'pipeline__',
                'knownbugregex': 'bugoccurrences__build__pipeline__',
                'pipeline': '',
            };

            return prefixPathToFields(model_fields, prefixtures[origin]);
        };


        function getFilterModels($scope) {
            var enum_fields = Object.keys(generateFilterPaths())
            index = enum_fields.indexOf("completed_at__gte");
            enum_fields.splice(index, 1);
            index = enum_fields.indexOf("completed_at__lte");
            enum_fields.splice(index, 1);
            return enum_fields;
        };

        function getMetadata($scope) {
            var enum_fields = getFilterModels();

            for (i = 0; i < enum_fields.length; i++) {
                $scope.metadata[enum_fields[i]] = DataService.refresh(
                    enum_fields[i], $scope.user, $scope.apikey).query({});
                }
            return $scope;
        };

        function updateGraphs() {
            active_filters = generateActiveFilters('build');
            graphFactory.refresh(binding, active_filters);
            $scope.builds = update('build')
        };


        function update(model) {
            active_filters = generateActiveFilters(model);
            return DataService.refresh(model, $scope.user, $scope.apikey).get(active_filters);
        };

        function dateToString(date) {
            return date.getUTCFullYear() + "-" + (date.getUTCMonth() + 1) + "-" + date.getUTCDate();
        }

        $scope.humaniseDate = function(datestr) {
            var date_obj = new Date(datestr);
            var monthNames = ["Jan", "Feb", "Mar","Apr", "May", "Jun",
                              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
            var day = ('0' + date_obj.getUTCDate()).slice(-2);
            var month_name = monthNames[date_obj.getUTCMonth()];
            var year = ('0' + date_obj.getUTCFullYear()).slice(-2);
            var hours = ('0' + date_obj.getUTCHours()).slice(-2);
            var minutes = ('0' + date_obj.getUTCMinutes()).slice(-2);
            var seconds = ('0' + date_obj.getUTCSeconds()).slice(-2);
            return (day + "-" + month_name + "-" + year + " at " + hours + ":" + minutes + ":" + seconds);
        };

        var dateSymbolToDays = {
            'Last 24 Hours': 1,
            'Last 7 Days': 7,
            'Last 30 Days': 30,
            'Last Year': 365
        };

        function updateDates(value) {
            var days_offset = dateSymbolToDays[value];
            console.log("Updating to last %d days.", days_offset);
            today = new Date();
            prior_date = new Date(new Date().setDate(today.getDate()-days_offset));
            $scope.start_date = prior_date.toISOString();
            $scope.finish_date = today.toISOString();
        };

        function updateFromServer() {
            updateGraphs();
            $scope.bugs = update('bug');
            $scope.testRuns = update('pipeline');
        }

        // Clear the search bar.
        $scope.clearSearch = function() {
            $scope.search = "";
            $scope.start_date = null;
            $scope.finish_date = null;
            $scope.updateSearch();
        };

        // Update the filters object when the search bar is updated.
        $scope.updateSearch = function() {
            var filters = SearchService.getCurrentFilters(
                $scope.search);
            if(filters === null) {
                $scope.filters = SearchService.getEmptyFilter();
                $scope.searchValid = false;
            } else {
                $scope.filters = filters;
                $scope.searchValid = true;
            }
            updateFromServer();
        };

        $scope.updateIndividualTestRun = function(pipeline) {
            $scope.individual_testRun = DataService.refresh(
                'pipeline', $scope.user, $scope.apikey).get({"uuid": pipeline});
        };

        $scope.abbreviateUUID = function(UUID) {
            return UUID.slice(0, 4) + "..." + UUID.slice(-5);
        };

        $scope.updateFilter = function(type, value, tab) {
            console.log("Updating filter! %s %s %s", type, value, tab);

            if (type == "date") {
                // Only one date can be set at a time.
                new_value = "=" + value;
                if ($scope.filters["date"] && $scope.filters["date"][0] == new_value) {
                    $scope.filters["date"] = [];
                    $scope.start_date = null;
                    $scope.finish_date = null;
                } else {
                    updateDates(value);
                    $scope.filters["date"] = [new_value];
                }
            } else {
                $scope.filters = SearchService.toggleFilter(
                    $scope.filters, type, value, true);
            }
            $scope.search = SearchService.filtersToString($scope.filters);
            updateFromServer();
        };

        $scope.isFilterActive = function(type, value, tab) {
            return SearchService.isFilterActive(
                $scope.filters, type, value, true);
        };

        // Toggles between the current tab.
        $scope.toggleTab = function(tab) {
            updateFromServer(); // FIXME: Temporary hack. Need to refresh plot rather than redownloading data.
            $rootScope.title = $scope.tabs[tab].pagetitle;
            $scope.currentpage = tab;
        };

        // Sorts the table by predicate.
        $scope.sortTable = function(predicate, tab) {
            $scope.tabs[tab].predicate = predicate;
            $scope.tabs[tab].reverse = !$scope.tabs[tab].reverse;
        };

        $scope = getMetadata($scope);
        $scope.updateFilter('date', 'Last 24 Hours', 'successRate');
        $scope.toggleTab('successRate');
        $scope.sortTable('occurrence_count', 'bugs');
    }]);
