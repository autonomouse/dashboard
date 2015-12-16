var app = angular.module('weebl');
app.controller('successRateController', [
    '$scope', 'data', 'SearchService', 'DataService', 'graphFactory', 'Common',
    function($scope, data, SearchService, DataService, graphFactory, Common) {
        for (var datum in $scope.data) {
            data[datum] = $scope.data[datum]
        };
        $scope.data = data;

        binding = this;
        binding.user = $scope.data.user;
        binding.apikey = $scope.data.apikey;
        $scope.data.show_filters = true;
        $scope.data.show_search = true;

        $scope.data.default_tab = 'successRate';
        $scope.data.time_range = 'Last 24 Hours';

        if (typeof($scope.data.filters)==='undefined') $scope.data.filters = SearchService.getEmptyFilter();

        if (typeof($scope.data.metadata)==='undefined') $scope.data.metadata = {};
        if (typeof($scope.data.successRate)==='undefined') $scope.data.successRate = {};
        if (typeof($scope.data.bugs)==='undefined') $scope.data.bugs = {};
        if (typeof($scope.data.testRuns)==='undefined') $scope.data.testRuns = {};
        if (typeof($scope.data.regexes)==='undefined') $scope.data.regexes = {};

        if (typeof($scope.data.tabs)==='undefined') {
            $scope.data.tabs = {};
            $scope.data.tabs.successRate = {};
            $scope.data.tabs.successRate.pagetitle = "Success Rate";
            $scope.data.tabs.testRuns = {};
            $scope.data.tabs.testRuns.pagetitle = "Test Runs";
            $scope.data.tabs.testRuns.predicate = "completed_at";
            $scope.data.tabs.testRuns.reverse = false;
            $scope.data.tabs.bugs = {};
            $scope.data.tabs.bugs.pagetitle = "Bugs";
            $scope.data.tabs.bugs.predicate = "occurrences";
            $scope.data.tabs.bugs.reverse = false;
        };

        function generateActiveFilters(origin) {
            var active_filters = {};
            var field_to_filter = generateFilterPaths(origin);

            for (var enum_field in $scope.data.filters) {
                if (!(enum_field in $scope.data.metadata))
                    continue;

                enum_values = [];
                $scope.data.filters[enum_field].forEach(function(enum_value) {
                    enum_values.push(enum_value.substr(1));
                });

                // generate active filters from the perspective of origin:
                active_filters[field_to_filter[enum_field]] = enum_values;
            }
            // generate date active filters from the perspective of origin:
            if ($scope.data.start_date)
                active_filters[field_to_filter['completed_at__gte']] = $scope.data.start_date;
            if ($scope.data.finish_date)
                active_filters[field_to_filter['completed_at__lte']] = $scope.data.finish_date;

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


        function getFilterModels() {
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
                $scope.data.metadata[enum_fields[i]] = DataService.refresh(
                    enum_fields[i], $scope.data.user, $scope.data.apikey).query({});
                }
            return $scope.data;
        };

        function updateGraphs() {
            active_filters = generateActiveFilters('build');
            graphFactory.refresh(binding, active_filters);
            $scope.data.builds = update('build')
        };


        function update(model) {
            active_filters = generateActiveFilters(model);
            return DataService.refresh(model, $scope.data.user, $scope.data.apikey).get(active_filters);
        };

        function dateToString(date) {
            return date.getUTCFullYear() + "-" + (date.getUTCMonth() + 1) + "-" + date.getUTCDate();
        }

        $scope.data.humaniseDate = Common.humaniseDate;

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
            $scope.data.start_date = prior_date.toISOString();
            $scope.data.finish_date = today.toISOString();
        };

        function updateFromServer() {
            updateGraphs();
            $scope.data.bugs = update('bug');
            $scope.data.testRuns = update('pipeline');
        }

        // Clear the search bar.
        $scope.data.clearSearch = function() {
            $scope.data.search = "";
            $scope.data.start_date = null;
            $scope.data.finish_date = null;
            $scope.data.updateSearch();
        };

        // Update the filters object when the search bar is updated.
        $scope.data.updateSearch = function() {
            var filters = SearchService.getCurrentFilters(
                $scope.data.search);
            if(filters === null) {
                $scope.data.filters = SearchService.getEmptyFilter();
                $scope.data.searchValid = false;
            } else {
                $scope.data.filters = filters;
                $scope.data.searchValid = true;
            }
            updateFromServer();
        };

        $scope.data.abbreviateUUID = function(UUID) {
            return UUID.slice(0, 4) + "..." + UUID.slice(-5);
        };

        $scope.data.highlightTab = function(datestr) {
            Common.highlightTab($scope, datestr);
        };

        $scope.data.updateFilter = function(type, value, tab) {
            console.log("Updating filter! %s %s %s", type, value, tab);

            if (type == "date") {
                // Only one date can be set at a time.
                new_value = "=" + value;
                if ($scope.data.filters["date"] && $scope.data.filters["date"][0] == new_value) {
                    $scope.data.filters["date"] = [];
                    $scope.data.start_date = null;
                    $scope.data.finish_date = null;
                } else {
                    updateDates(value);
                    $scope.data.filters["date"] = [new_value];
                }
            } else {
                $scope.data.filters = SearchService.toggleFilter(
                    $scope.data.filters, type, value, true);
            }
            $scope.data.search = SearchService.filtersToString($scope.data.filters);
            updateFromServer();
        };

        $scope.data.isFilterActive = function(type, value, tab) {
            return SearchService.isFilterActive(
                $scope.data.filters, type, value, true);
        };

        // Sorts the table by predicate.
        $scope.data.sortTable = function(predicate, tab) {
            $scope.data.tabs[tab].predicate = predicate;
            $scope.data.tabs[tab].reverse = !$scope.data.tabs[tab].reverse;
        };

        if (Object.keys($scope.data.filters).length < 2) {
            $scope.data.updateFilter('date', $scope.data.time_range, $scope.data.default_tab);
            $scope.data.highlightTab($scope.data.default_tab)
            $scope.data = getMetadata($scope);
        };
        $scope.data.sortTable('occurrence_count', 'bugs');
        updateFromServer();
    }]);
