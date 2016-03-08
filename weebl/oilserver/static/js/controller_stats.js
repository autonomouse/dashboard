var app = angular.module('weebl');
app.controller('successRateController', [
    '$scope', '$q', 'data', 'SearchService', 'DataService', 'graphFactory', 'Common',
    function($scope, $q, data, SearchService, DataService, graphFactory, Common) {
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
        $scope.data.default_section = 'results';
        $scope.data.time_range = 'Last 24 Hours';

        $scope = Common.initialise($scope);

        if (typeof($scope.data.filters)==='undefined') $scope.data.filters = SearchService.getEmptyFilter();


        function getMetadata($scope) {
            var enum_fields = Common.getFilterModels();

            for (i = 0; i < enum_fields.length; i++) {
                field = enum_fields[i];
                query_field = Common.getQueryFieldName(field);
                $scope.data.metadata[field] = DataService.refresh(
                    query_field, $scope.data.user, $scope.data.apikey).query({});
                }
            return $scope.data;
        };

        function fetchDataForEachStatus(model, filter_set, jobname, graphValues) {
            filter_set['meta_only'] = true;
            filter_set['limit'] = 1;
            filter_set['max_limit'] = 1;
            if(jobname === null) {
                delete filter_set['build__jobtype__name'];
                graphValues.total = DataService.refresh(model, $scope.data.user, $scope.data.apikey).get(filter_set);
            } else {
                filter_set['jobtype__name'] = jobname;
                delete filter_set['buildstatus__name']
                graphValues.jobtotal = DataService.refresh(model, $scope.data.user, $scope.data.apikey).get(filter_set);
                filter_set['buildstatus__name'] = 'success';
                graphValues.pass = DataService.refresh(model, $scope.data.user, $scope.data.apikey).get(filter_set);
            };
        };

        function updateGraphValues(total, pass_deploy_count, pass_prepare_count, pass_test_cloud_image_count) {
            $scope.data.fetching_data = true;
            $scope.data.graphValues = {};
            $scope.data.graphValues.total = {}
            $scope.data.graphValues.deploy = {}
            $scope.data.graphValues.prepare = {}
            $scope.data.graphValues.test_cloud_image = {}

            var pipeline_filters = Common.generateActiveFilters($scope, 'pipeline');
            fetchDataForEachStatus('pipeline', pipeline_filters, null, $scope.data.graphValues);
            var build_filters = Common.generateActiveFilters($scope, 'build');
            fetchDataForEachStatus('build', build_filters, 'pipeline_deploy', $scope.data.graphValues.deploy);
            fetchDataForEachStatus('build', build_filters, 'pipeline_prepare', $scope.data.graphValues.prepare);
            fetchDataForEachStatus('build', build_filters, 'test_cloud_image', $scope.data.graphValues.test_cloud_image);

            $scope.data.fetching_data = false;

            plotStatsGraph();
         };

        function plotStatsGraph() {
            $scope.data.plot_data_loading = true;
            $q.all([
                $scope.data.graphValues.total.$promise,
                $scope.data.graphValues.deploy.pass.$promise,
                $scope.data.graphValues.deploy.jobtotal.$promise,
                $scope.data.graphValues.prepare.pass.$promise,
                $scope.data.graphValues.prepare.jobtotal.$promise,
                $scope.data.graphValues.test_cloud_image.pass.$promise,
                $scope.data.graphValues.test_cloud_image.jobtotal.$promise
            ]).then(function() {
                if ($scope.data.graphValues.total.$resolved) {
                    console.log('total test runs = ' + $scope.data.graphValues.total.meta.total_count);
                    console.log('deploy passes = ' + $scope.data.graphValues.deploy.pass.meta.total_count);
                    console.log('total deploy builds = ' + $scope.data.graphValues.deploy.jobtotal.meta.total_count);
                    console.log('prepare passes = ' + $scope.data.graphValues.prepare.pass.meta.total_count);
                    console.log('total prepare builds = ' + $scope.data.graphValues.prepare.jobtotal.meta.total_count);
                    console.log('cloud_image passes = ' + $scope.data.graphValues.test_cloud_image.pass.meta.total_count);
                    console.log('total cloud_image builds = ' + $scope.data.graphValues.test_cloud_image.jobtotal.meta.total_count);

                    graphFactory.plot_stats_graph(binding, $scope.data.graphValues);
                    $scope.data.plot_data_loading = false;
                };
            });
        };


        function update(model) {
            $scope.data.fetching_data = true;
            active_filters = Common.generateActiveFilters($scope, model);
            var data = DataService.refresh(model, $scope.data.user, $scope.data.apikey).get(active_filters);
            $scope.data.fetching_data = false;
            return data
        };

        function dateToString(date) {
            return date.getUTCFullYear() + "-" + (date.getUTCMonth() + 1) + "-" + date.getUTCDate();
        };

        $scope.data.calcPercentage = function(value, number_of_test_runs) {
            return graphFactory.calcPercentage(value, number_of_test_runs);
        };

        $scope.data.getNumberOfOtherBuilds = function(values) {
            if(values.abort.$resolved && values.unknown.$resolved) {
                return (values.abort.meta.total_count + values.unknown.meta.total_count)
            };
        };

        $scope.data.getTotalNumberOfBuilds = function(values) {
            if(values.pass.$resolved && values.fail.$resolved && values.abort.$resolved && values.unknown.$resolved) {
                return (values.pass.meta.total_count + values.fail.meta.total_count + values.abort.meta.total_count + values.unknown.meta.total_count)
            };
        };

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
            $scope.data.bugs = update('bug');
            $scope.data.jobtypes = update('jobtype');
            $scope.data.testRuns = update('pipeline');
            updateGraphValues();
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
            if($scope.data.search.search('date') == -1) {
                var gap = ""
                if($scope.data.search.length > 0){ var gap = " " }
                $scope.data.search = $scope.data.search + gap + "date:(=All Time)"
            }

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

        $scope.data.highlightTab = function(tab) {
            Common.highlightTab($scope, tab);
        };

        $scope.data.highlightSection = function(section) {
            Common.highlightSection($scope, section);
        };

        $scope.data.updateFilter = function(type, value, tab) {
            console.log("Updating filter! %s %s %s", type, value, tab);

            if (type == "date") {
                // Only one date can be set at a time.
                new_value = "=" + value;
                if (($scope.data.filters["date"] && $scope.data.filters["date"][0] == new_value) || (new_value == "=All Time")){
                    $scope.data.filters["date"] = [];
                    $scope.data.start_date = null;
                    $scope.data.finish_date = null;
                    $scope.data.filters = SearchService.toggleFilter(
                        $scope.data.filters, type, "All Time", true);
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

        $scope.data.jobtypeLookup = function(jobname) {
            return Common.jobtypeLookup(jobname);
        };

        if (Object.keys($scope.data.filters).length < 2) {
            $scope.data.updateFilter('date', $scope.data.time_range, $scope.data.default_tab);
            $scope.data.highlightTab($scope.data.default_tab)
            $scope.data.highlightSection($scope.data.default_section)
            $scope.data = getMetadata($scope);
            updateFromServer();
        };
        $scope.data.sortTable('occurrence_count', 'bugs');
        $scope.data.subfilter_plot_form.type = 'cumulative';
        $scope.data.testRuns = update('pipeline');
        updateGraphValues();
        plotStatsGraph();
    }]);
