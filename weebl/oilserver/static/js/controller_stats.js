var app = angular.module('weebl');
app.controller('successRateController', [
    '$scope', '$q', 'data', 'SearchFactory', 'DataService', 'graphFactory', 'Common',
    function($scope, $q, data, SearchFactory, DataService, graphFactory, Common) {
        for (var datum in $scope.data) {
            data[datum] = $scope.data[datum]
        };
        $scope.data = data;

        binding = this;
        binding.user = $scope.data.user;
        binding.apikey = $scope.data.apikey;


        $scope = Common.initialise($scope);
        if ($scope.data.results.search === undefined) $scope.data.results.search = new SearchFactory.Search();

        $scope.data.reports.show_filters = false;
        $scope.data.results.show_filters = true;
        $scope.data.results.show_search = true;

        $scope.data.default_tab = 'successRate';
        $scope.data.default_section = 'results';

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
            'Last Year': 365,
            'All Time': null
        };

        function updateDates(value) {
            var days_offset = dateSymbolToDays[value];
            console.log("Updating to last %d days.", days_offset);
            if (days_offset === null) {
                $scope.data.start_date = null;
                $scope.data.finish_date = null;
            }
            else {
                today = new Date();
                prior_date = new Date(new Date().setDate(today.getDate()-days_offset));
                $scope.data.start_date = prior_date.toISOString();
                $scope.data.finish_date = today.toISOString();
            }
        }

        function updateFromServer() {
            $scope.data.bugs = update('bug');
            $scope.data.jobtypes = update('jobtype');
            $scope.data.testRuns = update('pipeline');
            updateGraphValues();
        }

        function updateSearch() {
            // slicing to pull off the prepended '=' for exact searches
            updateDates($scope.data.results.search.filters["date"][0].slice(1));
            updateFromServer();
        }

        $scope.data.results.search.defaultFilters = {"date": "All Time"};
        $scope.data.results.search.individualFilters = ["date"];
        $scope.data.results.search.runOnUpdate = updateSearch;
        // set the first search to 24 hours
        // if not doing that run update() instead to apply the above changes
        if($scope.data.results.search.search == "") {
            $scope.data.results.search.toggleFilter("date", "Last 24 Hours", true);
        }

        $scope.data.abbreviateUUID = function(UUID) {
            return UUID.slice(0, 4) + "..." + UUID.slice(-5);
        };

        $scope.data.highlightTab = function(tab) {
            Common.highlightTab($scope, tab);
        };

        $scope.data.highlightSection = function(section) {
            Common.highlightSection($scope, section);
        };

        // Sorts the table by predicate.
        $scope.data.sortTable = function(predicate, tab) {
            $scope.data.tabs[tab].predicate = predicate;
            $scope.data.tabs[tab].reverse = !$scope.data.tabs[tab].reverse;
        };

        $scope.data.jobtypeLookup = function(jobname) {
            return Common.jobtypeLookup(jobname);
        };

        $scope.data = getMetadata($scope);
        $scope.data.sortTable('occurrence_count', 'bugs');
        $scope.data.subfilter_plot_form.type = 'cumulative';
        $scope.data.testRuns = update('pipeline');
        updateGraphValues();
        plotStatsGraph();
    }]);
