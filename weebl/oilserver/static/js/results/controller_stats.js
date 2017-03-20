var app = angular.module('weebl');
app.controller('successRateController', [
    '$scope', '$q', 'data', 'SearchFactory', 'graphFactory', 'DataService', 'Common', 'FilterFactory',
    function($scope, $q, data, SearchFactory, graphFactory, DataService, Common, FilterFactory) {
        for (var datum in $scope.data) {
            data[datum] = $scope.data[datum]
        };
        if (angular.isUndefined($scope.data)) $scope.data = data;

        binding = this;
        binding.user = $scope.data.user;
        binding.apikey = $scope.data.apikey;


        $scope = Common.initialise($scope);
        $scope.data.graphValues = {"ready": false};
        if (angular.isUndefined($scope.data.results.search))  $scope.data.results.search = new SearchFactory.Search();
        $scope.data.results.search.init();

        $scope.data.reports.show_filters = false;
        $scope.data.results.show_filters = true;
        $scope.data.qa.show_filters = false;
        $scope.data.results.show_search = true;
        $scope.data.qa.show_search = false;

        $scope.data.default_tab = 'successRate';
        $scope.data.default_section = 'results';


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
                var queue = [$scope.data.graphValues.total.$promise, $scope.data.graphValues.pipeline_total.$promise];
                angular.forEach(Common.getJobsList(job_details, true), function(jobname){
                    if (!angular.isUndefined($scope.data.graphValues[jobname].pass)) queue.push($scope.data.graphValues[jobname].pass.$promise);
                    if (!angular.isUndefined($scope.data.graphValues[jobname].jobtotal)) queue.push($scope.data.graphValues[jobname].jobtotal.$promise);
                    if (!angular.isUndefined($scope.data.graphValues[jobname].skip)) queue.push($scope.data.graphValues[jobname].skip.$promise);
                });
                $q.all(queue).then(function(queue) {
                    if (Common.checkAllInQueueIsAreResolved(queue)) {
                        jobDetails = Common.makeJobDetailsDict(job_details);
                        graphFactory.plot_stats_graph(binding, $scope.data.graphValues, jobDetails);
                        $scope.data.plot_data_loading = false;
                    } else {
                        console.log("Can not plot stats graph yet, queue not completely resolved...");
                    };
                });
            });
        };


        function update(model) {
            active_filters = FilterFactory.generateActiveFilters($scope, model);
            return DataService.refresh(model, $scope.data.user, $scope.data.apikey).get(active_filters);
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

        function updateStartDate(start_date) {
            $scope.data.start_date = FilterFactory.updateStartDate(start_date);
        };

        function updateFinishDate(finish_date) {
            $scope.data.finish_date = FilterFactory.updateFinishDate(finish_date);
        };

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

        $scope.generatePDF = function() {
            $scope.data.pdf_content = angular.element("#content-view").html();
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

        $q.all([$scope.data.job_details.$promise]).then(function([job_details]) {
            $scope.data.jobtypeLookup = Common.makeJobDetailsDict(job_details);
        });

        $scope.data = getMetadata($scope);
        $scope.data.testRuns = update('pipeline');
        updateGraphValues();
        plotStatsGraph();
        jobDetails = Common.makeJobDetailsDict($scope.data.job_details);

        $scope.$watch('data.graphValues.ready', function() {
            if ($scope.data.graphValues.ready === true) {
                graphFactory.plot_stats_graph(binding, $scope.data.graphValues, jobDetails);
            }
        });
    }]);
