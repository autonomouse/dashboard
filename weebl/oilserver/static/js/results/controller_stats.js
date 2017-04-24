var app = angular.module('weebl');
app.controller('successRateController', [
    '$scope', '$rootScope', '$q', 'data', 'SearchFactory', 'graphFactory', 'DataService', 'Common', 'FilterFactory',
    function($scope, $rootScope, $q, data, SearchFactory, graphFactory, DataService, Common, FilterFactory) {
        for (var datum in $scope.data) {
            data[datum] = $scope.data[datum]
        };
        if (angular.isUndefined($scope.data))
            $scope.data = data;

        binding = this;
        binding.user = $scope.data.user;
        binding.apikey = $scope.data.apikey;

        $scope = Common.initialise($scope);

        $scope.data = getMetadata($scope);

        $scope.data.graphValues = {"ready": false};

        $rootScope.data.show_reports_filters = false;
        $rootScope.data.show_filters = true;
        $rootScope.data.show_search = true;

        $scope.data.default_tab = 'successRate';
        $scope.data.default_section = 'results';

        if (angular.isUndefined($scope.data.search))
            $scope.data.search = new SearchFactory.Search();

        $scope.data.start_dates = [
            '24 Hours Ago',
            '7 Days Ago',
            '30 Days Ago',
            'One Year Ago'
        ];

        $scope.data.finish_dates = [
            'Now'
        ];

        $scope.data.search.defaultFilters = {
            "start_date": '24 Hours Ago',
            "finish_date": 'Now',
        }
        $scope.data.search.individualFilters = ["start_date", "finish_date"];
        $scope.data.search.runOnUpdate = updateSearch;
        $scope.data.search.initialPageLoad();

        function getMetadata($scope) {
            var enum_fields = FilterFactory.getFilterModels();

            for (i = 0; i < enum_fields.length; i++) {
                field = enum_fields[i];
                query_field = FilterFactory.getQueryFieldName(field);
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

        function updateGraphValues() {
            $scope.data.plot_data_loading = true;
            [$scope.data.graphValues.total, $scope.data.graphValues.pipeline_total] = FilterFactory.getTotals($scope);
            $q.all([$scope.data.job_details.$promise]).then(function([job_details]) {
                jobs = Common.getJobsList(job_details, true);
                angular.forEach(jobs, function(jobname){
                    $scope.data.graphValues[jobname] = {};
                    [$scope.data.graphValues[jobname].pass,
                     $scope.data.graphValues[jobname].skip,
                     $scope.data.graphValues[jobname].jobtotal
                 ] = FilterFactory.fetchTestDataForJobname(jobname, $scope);
                });
            });
            plotStatsGraph();
         };

        function plotStatsGraph() {
            $q.all([$scope.data.job_details.$promise]).then(function([job_details]) {
                var queue = [$scope.data.graphValues.total.$promise,
                             $scope.data.graphValues.pipeline_total.$promise];
                angular.forEach(Common.getJobsList(job_details, true), function(jobname){
                    if (angular.isDefined($scope.data.graphValues[jobname].pass))
                        queue.push($scope.data.graphValues[jobname].pass.$promise);
                    if (angular.isDefined($scope.data.graphValues[jobname].jobtotal))
                        queue.push($scope.data.graphValues[jobname].jobtotal.$promise);
                    if (angular.isDefined($scope.data.graphValues[jobname].skip))
                        queue.push($scope.data.graphValues[jobname].skip.$promise);
                });
                $q.all(queue).then(function(queue) {
                    if (Common.checkAllInQueueAreResolved(queue)) {
                        jobDetails = Common.makeJobDetailsDict(job_details);
                        graphFactory.plot_stats_graph(binding, $scope.data.graphValues, jobDetails);
                        $scope.data.plot_data_loading = false;

                        /*
                        FIXME: The following requires a lot of if statements for now. They can be removed once Common.checkAllInQueueAreResolved has been updated.
                        See the comment in checkAllInQueueAreResolved for the full explaination.
                        */

                        console.log('----------------------------');
                        console.log("Stats from " +
                                    $scope.data.search.filters["start_date"][0].slice(1) +
                                    " to " + $scope.data.search.filters["finish_date"][0].slice(1) +
                                    ":");
                        if (angular.isDefined($scope.data.graphValues.pipeline_deploy.jobtotal.meta))
                            console.log("deploy total: " +
                                    $scope.data.graphValues.pipeline_deploy.jobtotal.meta.total_count);
                        if (angular.isDefined($scope.data.graphValues.pipeline_deploy.pass.meta))
                            console.log("deploy pass: " +
                                    $scope.data.graphValues.pipeline_deploy.pass.meta.total_count);
                        if (angular.isDefined($scope.data.graphValues.pipeline_prepare.jobtotal.meta))
                            console.log("prepare total: " +
                                    $scope.data.graphValues.pipeline_prepare.jobtotal.meta.total_count);
                        if (angular.isDefined($scope.data.graphValues.pipeline_prepare.pass.meta))
                            console.log("prepare pass: " +
                                    $scope.data.graphValues.pipeline_prepare.pass.meta.total_count);
                        if (angular.isDefined($scope.data.graphValues.test_bundletests.jobtotal.meta) &&
                            angular.isDefined($scope.data.graphValues.test_bundletests.skip.meta))
                            console.log('non-skipped bundletest (tempest) testcases = ' +
                                    ($scope.data.graphValues.test_bundletests.jobtotal.meta.total_count -
                                    $scope.data.graphValues.test_bundletests.skip.meta.total_count));
                        if (angular.isDefined($scope.data.graphValues.test_bundletests.pass.meta))
                            console.log("bundletest (tempest) passed testcases: " +
                                    $scope.data.graphValues.test_bundletests.pass.meta.total_count);
                        if (angular.isDefined($scope.data.graphValues.test_cloud_image.jobtotal.meta) &&
                            angular.isDefined($scope.data.graphValues.test_cloud_image.skip.meta))
                            console.log('non-skipped cloud image testcases = ' +
                                    ($scope.data.graphValues.test_cloud_image.jobtotal.meta.total_count -
                                     $scope.data.graphValues.test_cloud_image.skip.meta.total_count));
                        if (angular.isDefined($scope.data.graphValues.test_cloud_image.pass.meta))
                            console.log("cloud image passed testcases: " +
                                    $scope.data.graphValues.test_cloud_image.pass.meta.total_count);

                    } else {
                        console.log("Can not plot stats graph yet, queue not completely resolved...");
                    };
                });
            });
        };

        function update(model, limit, offset) {
            if (angular.isUndefined(limit))
                limit = 1000;
            if (angular.isUndefined(offset))
                offset = 0;
            active_filters = FilterFactory.generateActiveFilters($scope, model);
            active_filters['limit'] = limit;
            active_filters['offset'] = offset;
            return DataService.refresh(model, $scope.data.user, $scope.data.apikey).get(active_filters)
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

        function updateStartDate(start_date) {
            $scope.data.start_date = FilterFactory.updateStartDate(start_date);
        };

        function updateFinishDate(finish_date) {
            $scope.data.finish_date = FilterFactory.updateFinishDate(finish_date);
        };

        function updateFromServer() {
            updateGraphValues();
        }

        function updateSearch() {
            $scope.data.plot_data_loading = true;
            // slicing to pull off the prepended '=' for exact searches:
            updateStartDate($scope.data.search.filters["start_date"][0].slice(1));
            updateFinishDate($scope.data.search.filters["finish_date"][0].slice(1));
            updateFromServer();
        }

        $scope.data.highlightTab = function(tab) {
            Common.highlightTab($scope, tab);
        };

        $scope.data.highlightSection = function(section) {
            Common.highlightSection($scope, section);
        };

        $q.all([$scope.data.job_details.$promise]).then(function([job_details]) {
            $scope.data.jobtypeLookup = Common.makeJobDetailsDict(job_details);
        });

        updateGraphValues();
        jobDetails = Common.makeJobDetailsDict($scope.data.job_details);

        $scope.data.colourStatus = Common.colourStatus;

        $scope.$watch('data.graphValues.ready', function() {
            if ($scope.data.graphValues.ready === true) {
                graphFactory.plot_stats_graph(binding, $scope.data.graphValues, jobDetails);
            }
        });

    }]);
