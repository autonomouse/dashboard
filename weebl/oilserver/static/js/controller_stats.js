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

            var configurationchoices = [
                'sdn',
                'compute',
                'blockstorage',
                'imagestorage',
                'database',
            ];
            for (var i in configurationchoices) {
                field = configurationchoices[i];
                $scope.data.metadata[field] = DataService.refresh(
                    'productundertest', $scope.data.user, $scope.data.apikey).query({'producttype__name': field});
            }


            return $scope.data;
        };

        function fetchTestDataForJobname(jobname, graphValues) {
            var model = 'testcaseinstance';
            var local_filters = Common.generateActiveFilters($scope, model);
            local_filters['meta_only'] = true;
            local_filters['limit'] = 1;
            local_filters['max_limit'] = 1;
            local_filters['build__jobtype__name'] = jobname;
            if(jobname == "test_bundletests")
                local_filters['testcase__testcaseclass__testframework__name'] = 'bundletests';
            local_filters['successful_jobtype'] = jobname;
            local_filters['testcaseinstancestatus__name'] = 'success';
            graphValues.pass = DataService.refresh(model, $scope.data.user, $scope.data.apikey).get(local_filters);
            local_filters['testcaseinstancestatus__name'] = 'skipped';
            graphValues.skip = DataService.refresh(model, $scope.data.user, $scope.data.apikey).get(local_filters);
            delete local_filters['successful_jobtype'];
            delete local_filters['testcaseinstancestatus__name'];
            graphValues.jobtotal = DataService.refresh(model, $scope.data.user, $scope.data.apikey).get(local_filters);
        };

        function fetchDataForEachStatus(jobname, graphValues) {
            var model = 'pipeline';
            var local_filters = Common.generateActiveFilters($scope, model);
            local_filters['meta_only'] = true;
            local_filters['limit'] = 1;
            local_filters['max_limit'] = 1;
            if(jobname === null) {
                graphValues.total = DataService.refresh(model, $scope.data.user, $scope.data.apikey).get(local_filters);
            } else {
                local_filters['successful_jobtype'] = jobname;
                graphValues.pass = DataService.refresh(model, $scope.data.user, $scope.data.apikey).get(local_filters);
                delete local_filters['successful_jobtype'];
                local_filters['builds__jobtype__name'] = jobname;
                graphValues.jobtotal = DataService.refresh(model, $scope.data.user, $scope.data.apikey).get(local_filters);
            };
        };

        function updateGraphValues(total, pass_deploy_count, pass_prepare_count, pass_test_cloud_image_count, pass_test_bundletests_count) {
            $scope.data.fetching_data = true;
            $scope.data.graphValues = {};
            $scope.data.graphValues.total = {};
            $scope.data.graphValues.deploy = {};
            $scope.data.graphValues.prepare = {};
            $scope.data.graphValues.test_cloud_image = {};
            $scope.data.graphValues.test_bundletests = {};

            fetchDataForEachStatus(null, $scope.data.graphValues);
            fetchDataForEachStatus('pipeline_deploy', $scope.data.graphValues.deploy);
            fetchDataForEachStatus('pipeline_prepare', $scope.data.graphValues.prepare);
            fetchDataForEachStatus('test_cloud_image', $scope.data.graphValues.test_cloud_image);
            fetchTestDataForJobname('test_bundletests', $scope.data.graphValues.test_bundletests);

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
                $scope.data.graphValues.test_cloud_image.jobtotal.$promise,
                $scope.data.graphValues.test_bundletests.pass.$promise,
                $scope.data.graphValues.test_bundletests.jobtotal.$promise
            ]).then(function() {
                if ($scope.data.graphValues.total.$resolved) {
                    console.log('total test runs = ' + $scope.data.graphValues.total.meta.total_count);
                    console.log('deploy passes = ' + $scope.data.graphValues.deploy.pass.meta.total_count);
                    console.log('total deploy builds = ' + $scope.data.graphValues.deploy.jobtotal.meta.total_count);
                    console.log('prepare passes = ' + $scope.data.graphValues.prepare.pass.meta.total_count);
                    console.log('total prepare builds = ' + $scope.data.graphValues.prepare.jobtotal.meta.total_count);
                    console.log('cloud_image passes = ' + $scope.data.graphValues.test_cloud_image.pass.meta.total_count);
                    console.log('total cloud_image builds = ' + $scope.data.graphValues.test_cloud_image.jobtotal.meta.total_count);
                    if($scope.data.results.search.filters.failedjobs)
                        $scope.data.graphValues.test_bundletests.pass.meta.total_count = 0;
                    console.log('bundletests testcases passes = ' + $scope.data.graphValues.test_bundletests.pass.meta.total_count);
                    console.log('bundletests testcases skipped = ' + $scope.data.graphValues.test_bundletests.skip.meta.total_count);
                    console.log('total bundletests testcases = ' + $scope.data.graphValues.test_bundletests.jobtotal.meta.total_count);
                    $scope.data.graphValues.test_bundletests.jobtotal.meta.total_count = $scope.data.graphValues.test_bundletests.jobtotal.meta.total_count
                        - $scope.data.graphValues.test_bundletests.skip.meta.total_count;
                    console.log('non-skipped bundletests testcases = ' + $scope.data.graphValues.test_bundletests.jobtotal.meta.total_count);
                    console.log('----------------------------');

                    graphFactory.plot_stats_graph(binding, $scope.data.graphValues);
                    $scope.data.plot_data_loading = false;
                };
            });
        };


        function update(model) {
            $scope.data.fetching_data = true;
            active_filters = Common.generateActiveFilters($scope, model);
            var datum = DataService.refresh(model, $scope.data.user, $scope.data.apikey).get(active_filters);
            $scope.data.fetching_data = false;
            return datum
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
            '24 Hours Ago': 1,
            '7 Days Ago': 7,
            '30 Days Ago': 30,
            'One Year Ago': 365,
            'Dawn of Time': null
        };

        function updateStartDate(start_date) {
            if (start_date.includes("Ago") || start_date.includes("Time")) {
                var days_offset = dateSymbolToDays[start_date];
                console.log("Updating to last %d days.", days_offset);
                if (days_offset === null) {
                    $scope.data.start_date = null;
                } else {
                    var today = new Date();
                    prior_date = new Date(new Date().setDate(today.getDate()-days_offset));
                    $scope.data.start_date = prior_date.toISOString();
                }
            } else {
                console.log("Taking start date literally.");
                $scope.data.start_date = start_date;
            }
        }

        function updateFinishDate(finish_date) {
            /* update finish_date */
            if ((finish_date == 'Now') || (finish_date == null)) {
                $scope.data.finish_date = null;
            } else {
                console.log("Taking finish date literally.");
                $scope.data.finish_date = finish_date;
            }
        }

        function updateFromServer() {
            $scope.data.bugs = update('bug');
            $scope.data.testRuns = update('pipeline');
            updateGraphValues();
        }

        function updateSearch() {
            // slicing to pull off the prepended '=' for exact searches
            updateStartDate($scope.data.results.search.filters["start_date"][0].slice(1));
            updateFinishDate($scope.data.results.search.filters["finish_date"][0].slice(1));
            updateFromServer();
        }

        today = new Date();
        yesterday = new Date(new Date().setDate(today.getDate() - 1));

        $scope.data.start_dates = [
            '24 Hours Ago',
            '7 Days Ago',
            '30 Days Ago',
            'One Year Ago',
            'Dawn of Time'
        ];

        $scope.data.finish_dates = [
            'Now'
        ];

        $scope.data.results.search.defaultFilters = {
            "start_date": '24 Hours Ago',
            "finish_date": 'Now',
        }
        $scope.data.results.search.individualFilters = ["start_date", "finish_date"];
        $scope.data.results.search.runOnUpdate = updateSearch;
        // set the first search to 24 hours
        // if not doing that run update() instead to apply the above changes
        if($scope.data.results.search.search == "") {
            $scope.data.results.search.toggleFilter("start_date", "24 Hours Ago", true);
            $scope.data.results.search.toggleFilter("finish_date", "Now", true);
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
            if (predicate === $scope.data.tabs[tab].predicate) {
                $scope.data.tabs[tab].reverse = !$scope.data.tabs[tab].reverse;
            } else {
                $scope.data.tabs[tab].reverse = true;
            }
            $scope.data.tabs[tab].predicate = predicate;
        };

        $scope.data.jobtypeLookup = function(jobname) {
            return Common.jobtypeLookup(jobname);
        };

        $scope.data = getMetadata($scope);
        $scope.data.testRuns = update('pipeline');
        updateGraphValues();
        plotStatsGraph();
    }]);
