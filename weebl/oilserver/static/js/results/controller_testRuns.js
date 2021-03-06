var app = angular.module('weebl');
app.controller('testRunsController', [
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
        $scope.batch_size = 20;
        $scope.batch_start = 0;

        $scope.data = getMetadata($scope);

        $rootScope.data.show_reports_filters = false;
        $rootScope.data.show_filters = true;
        $rootScope.data.show_search = true;

        $scope.data.default_tab = 'testRuns';
        $scope.data.default_section = 'results';

        function getNewTestRuns(start, end) {
            if (start < 0) start = 0;
            $scope.data.plot_data_loading = true;
            $q.all([
                update('pipeline', $scope.batch_size, start).$promise]
            ).then(function([testRuns]) {
                $scope.data.testRuns = testRuns;
                if (end > testRuns.meta.total_count)
                    end = testRuns.meta.total_count;
                $scope.batch_start = start;
                $scope.batch_end = end;
            });
        };

        $scope.data.first_batch = function() {
            start = 0;
            assumed_end = $scope.batch_start + $scope.batch_size - 1;
            if ((angular.isUndefined($scope.data.testRuns)) ||
                (angular.isUndefined($scope.data.testRuns.meta)) ||
                (angular.isUndefined($scope.batch_end))) {
                end = assumed_end;
            } else {
                var max = $scope.data.testRuns.meta.limit
                end = max < $scope.batch_end ? max : assumed_end;
            };
            getNewTestRuns(start, end);
        };

        $scope.data.prev_batch = function() {
            if ((angular.isUndefined($scope.data.testRuns)) ||
                (angular.isUndefined($scope.data.testRuns.meta)) ||
                (angular.isUndefined($scope.batch_end))) {
                // Do nothing if data is not ready (first time loading)
                return
            };
            var end = $scope.batch_start - 1;
            var start = end - $scope.batch_size + 1;
            if (start < 0) {
                return $scope.data.first_batch();
            } else {
                getNewTestRuns(start, end);
            };
        };

        $scope.data.next_batch = function() {
            if ((angular.isUndefined($scope.data.testRuns)) ||
                (angular.isUndefined($scope.data.testRuns.meta)) ||
                (angular.isUndefined($scope.batch_end))) {
                // Do nothing if data is not ready (first time loading)
                return
            };
            var start = $scope.batch_start + $scope.batch_size;
            var end = start + $scope.batch_size - 1;
            if (end > $scope.data.testRuns.meta.total_count) {
                $scope.data.last_batch();
            } else {
                getNewTestRuns(start, end);
            };
        };

        $scope.data.last_batch = function() {
            if ((angular.isUndefined($scope.data.testRuns)) ||
                (angular.isUndefined($scope.data.testRuns.meta)) ||
                (angular.isUndefined($scope.batch_end))) {
                // Do nothing if data is not ready (first time loading)
                return
            };
            var end = $scope.data.testRuns.meta.total_count;
            var start = Math.floor(end/$scope.batch_size) * $scope.batch_size;
            getNewTestRuns(start, end);
        };

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

        function dateToString(date) {
            return date.getUTCFullYear() + "-" + (date.getUTCMonth() + 1) + "-" + date.getUTCDate();
        };

        $scope.data.humaniseDate = Common.humaniseDate;
        $scope.data.abbreviateUUID = Common.abbreviateUUID;

        function updateStartDate(start_date) {
            $scope.data.start_date = FilterFactory.updateStartDate(start_date);
        };

        function updateFinishDate(finish_date) {
            $scope.data.finish_date = FilterFactory.updateFinishDate(finish_date);
        };

        function updateFromServer() {
            $scope.data.bugs = update('bug');
            $scope.data.first_batch();
            $scope.data.first_batch();
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

        // Sorts the table by predicate.
        $scope.data.sortTable = function(predicate, tab) {
            if (predicate === $scope.data.tabs[tab].predicate) {
                $scope.data.tabs[tab].reverse = !$scope.data.tabs[tab].reverse;
            } else {
                $scope.data.tabs[tab].reverse = true;
            }
            $scope.data.tabs[tab].predicate = predicate;
        };

        $scope.data.getLogoURL = function(svg) {
            return Common.getLogoURL(svg)
        };

        $scope.data.getMaasVersionForTestRun = function(pipeline) {
            if (angular.isDefined($scope.data.testRunsWithData[pipeline].maasversion)) return;
            $scope.data.testRunsWithData[pipeline].maasversion = ''
            $q.all([
                DataService.refresh('productundertest', $scope.data.user, $scope.data.apikey).get({
                    'machineconfigurations__units__jujuservicedeployment__pipeline__uuid': pipeline,
                    'producttype__name': 'maas'}).$promise
            ]).then(function([maas_productundertest]) {
                if ((maas_productundertest.objects.length > 0) && (angular.isDefined(maas_productundertest.objects[0].name))) {
                    $scope.data.testRunsWithData[pipeline].maasversion = maas_productundertest.objects[0].name;
                };
            });
        };

        $scope.data.getJujuVersionForTestRun = function(pipeline) {
            if (angular.isDefined($scope.data.testRunsWithData[pipeline].jujuversion)) return;
            $scope.data.testRunsWithData[pipeline].jujuversion = ''
            $q.all([
                DataService.refresh('productundertest', $scope.data.user, $scope.data.apikey).get({
                    'machineconfigurations__units__jujuservicedeployment__pipeline__uuid': pipeline,
                    'producttype__name': 'juju'}).$promise
            ]).then(function([juju_productundertest]) {
                if ((juju_productundertest.objects.length > 0) && (angular.isDefined(juju_productundertest.objects[0].name))) {
                    $scope.data.testRunsWithData[pipeline].jujuversion = juju_productundertest.objects[0].name;
                };
            });
        };

        $scope.data.getDeployStatusForTestRun = function(pipeline) {
            $scope.data.plot_data_loading = true;
            if (angular.isDefined($scope.data.testRunsWithData[pipeline].deploystatus)) return;
            $scope.data.testRunsWithData[pipeline].deploystatus = ''
            $q.all([
                DataService.refresh('testcaseinstance', $scope.data.user, $scope.data.apikey).get({
                    'build__pipeline__uuid': pipeline,
                    'build__jobtype__name': 'pipeline_deploy'}).$promise
            ]).then(function([testcaseinstance]) {
                if ((testcaseinstance.objects.length > 0) && (angular.isDefined(testcaseinstance.objects[0].testcaseinstancestatus.name))) {
                    $scope.data.testRunsWithData[pipeline].deploystatus = testcaseinstance.objects[0].testcaseinstancestatus.name;
                     $q.all([
                        DataService.refresh('bugoccurrence', $scope.data.user, $scope.data.apikey).get({
                            'testcaseinstance__uuid': testcaseinstance.objects[0].uuid}).$promise
                    ]).then(function([bugoccurrence]) {
                        if (bugoccurrence.objects.length > 0) {
                            $scope.data.testRunsWithData[pipeline].blockers = bugoccurrence.objects;
                        };
                        $scope.data.plot_data_loading = false;
                    });
                };
            });
        };

        $scope.data.getExtraDataForTestRun = function(testrun) {
            if (angular.isUndefined($scope.data.testRunsWithData))
                $scope.data.testRunsWithData = {};
            if (angular.isUndefined($scope.data.testRunsWithData[testrun.uuid]))
                $scope.data.testRunsWithData[testrun.uuid] = {};
            $scope.data.getMaasVersionForTestRun(testrun.uuid);
            $scope.data.getJujuVersionForTestRun(testrun.uuid);
            $scope.data.getDeployStatusForTestRun(testrun.uuid);

            if ((angular.isDefined(testrun.versionconfiguration)) && (testrun.versionconfiguration === null)) {
                $scope.data.testRunsWithData[testrun.uuid].openstackversion = "Unknown";
                $scope.data.testRunsWithData[testrun.uuid].ubuntuversion = "Unknown";
            } else {
                if ((angular.isDefined(testrun.versionconfiguration.openstackversion)) && (testrun.versionconfiguration.openstackversion != null)) {
                    $scope.data.testRunsWithData[testrun.uuid].openstackversion = testrun.versionconfiguration.openstackversion.name;
                } else {
                    $scope.data.testRunsWithData[testrun.uuid].openstackversion = "Unknown";
                };
                if ((angular.isDefined(testrun.versionconfiguration.ubuntuversion)) && (testrun.versionconfiguration.ubuntuversion != null)) {
                    $scope.data.testRunsWithData[testrun.uuid].ubuntuversion = testrun.versionconfiguration.ubuntuversion.name;
                } else {
                    $scope.data.testRunsWithData[testrun.uuid].ubuntuversion = "Unknown";
                };
            };
            $scope.data.plot_data_loading = false;
        };


        $scope.data.first_batch();
        jobDetails = Common.makeJobDetailsDict($scope.data.job_details);

        $scope.data.colourStatus = Common.colourStatus;

    }]);
