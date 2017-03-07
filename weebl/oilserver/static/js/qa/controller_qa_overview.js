var app = angular.module('weebl');
app.controller('qaOverviewController', [
    '$scope', '$q', 'SearchFactory', 'graphFactory', 'DataService', 'Common',
    function($scope, $q, SearchFactory, graphFactory, DataService, Common) {
        if (angular.isUndefined($scope.data)) $scope.data = data;

        binding = this;
        binding.user = $scope.data.user;
        binding.apikey = $scope.data.apikey;

        $scope.data.qa.solutiontags = DataService.refresh('solutiontag', $scope.data.user, $scope.data.apikey).get({});
        if ($scope.data.qa.search === undefined) $scope.data.qa.search = new SearchFactory.Search();

        $scope.data.reports.show_filters = false;
        $scope.data.results.show_filters = false;
        $scope.data.qa.show_filters = true;
        $scope.data.results.show_search = false;
        $scope.data.qa.show_search = true;

        $scope.data.default_tab = 'qa';
        $scope.data.default_section = 'overview';

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

        $scope.data.humaniseDate = Common.humaniseDate;

        function updateStartDate(start_date) {
            if (start_date.includes("Ago") || start_date.includes("Time")) {
                var hours_offset = Common.dateSymbolToHours()[start_date];
                console.log("Updating to last %d hours (%d days).", hours_offset, (hours_offset / 24));
                if (hours_offset === null) {
                    $scope.data.start_date = null;
                } else {
                    var today = new Date();
                    prior_date = new Date(new Date().setHours(today.getHours()-(hours_offset)))
                    $scope.data.start_date = prior_date.toISOString();
                }
            } else {
                console.log("Taking start date literally.");
                $scope.data.start_date = start_date;
            }
        };

        function updateFinishDate(finish_date) {
            /* update finish_date */
            if ((finish_date == 'Now') || (finish_date == null)) {
                $scope.data.finish_date = null;
            } else {
                console.log("Taking finish date literally.");
                $scope.data.finish_date = finish_date;
            }
        };

        function updateSearch() {
            // slicing to pull off the prepended '=' for exact searches
            updateStartDate($scope.data.qa.search.filters["start_date"][0].slice(1));
            updateFinishDate($scope.data.qa.search.filters["finish_date"][0].slice(1));
        };

        function calcQaReportPeriod() {
            if (angular.isUndefined($scope.data.qa.search.filters["environment"])) {
                var environment = '';
            } else {
                var environment = []; //$scope.data.qa.search.filters["environment"] + ' data, ';
                for (var idx in $scope.data.qa.search.filters["environment"]) {
                    var this_env = $scope.data.qa.search.filters["environment"][idx].slice(1);
                    if (parseInt(idx) === 0) {
                        environment = this_env;
                    } else if (parseInt(idx) != ($scope.data.qa.search.filters["environment"].length) - 1) {
                        environment = environment + ", " + this_env;
                    } else {
                        environment = environment + " and " + this_env;
                    };
                    environment = environment + " data ";
                };
            };
            $scope.data.qa.overview.qaReportPeriod = (
                environment + "from " + $scope.data.qa.search.filters["start_date"][0].slice(1) +
                " to " +  $scope.data.qa.search.filters["finish_date"][0].slice(1));
        };

        function plotSolutionsGraph(solutiontag, output) {
            var tag = solutiontag.name;
            var colour = solutiontag.colour;
            $q.all([output[0].$promise, output[1].$promise, output[2].$promise]).then(function([pass, skip, jobtotal]) {
                $scope.data.qa.overview.tablevalues[tag] = {'name': tag};
                $scope.data.qa.overview.tablevalues[tag].success_rate = graphFactory.calcPercentage(
                    pass.meta.total_count,
                    jobtotal.meta.total_count,
                    skip.meta.total_count);
                $scope.data.qa.overview.graphValues.qa_stack_bar_data[0]['valueDict'][tag] = {
                    "label" : tag,
                    "value" : $scope.data.qa.overview.tablevalues[tag].success_rate,
                    "color" : colour
                };
                // only plot when have all data available:
                if ($scope.data.qa.solutiontags.objects.length === Object.keys($scope.data.qa.overview.graphValues.qa_stack_bar_data[0]['valueDict']).length) {
                    values = Object.keys($scope.data.qa.overview.graphValues.qa_stack_bar_data[0]['valueDict']).map(function(key){
                        return $scope.data.qa.overview.graphValues.qa_stack_bar_data[0]['valueDict'][key];
                    });
                    $scope.data.qa.overview.graphValues.qa_stack_bar_data[0]['values'] = values;
                    $scope.data.qa.overview.graphValues.qa_stack_bar_data[0]['valueDict'] = {};
                    graphFactory.plot_solutions_graph(binding, $scope.data.qa.overview.graphValues)
                };

                $q.all([
                    DataService.refresh('solution', $scope.data.user, $scope.data.apikey).get({
                        'solutiontag__name': tag}).$promise
                ]).then(function([solution]) {
                    $q.all([
                        DataService.refresh('testcaseinstance', $scope.data.user, $scope.data.apikey).query({
                            'build__pipeline__solution__solutiontag__name': tag,
                            'testcase__testcaseclass__testframework__name': 'pipeline_deploy',
                            'limit':1}).$promise
                    ]).then(function([latest_pipeline_tci]) {
                        $scope.data.qa.overview.tablevalues[tag].deploystatus = latest_pipeline_tci[0].testcaseinstancestatus.name;
                        var latest_pipeline = latest_pipeline_tci[0].build.pipeline
                        $scope.data.qa.overview.tablevalues[tag].date = latest_pipeline.completed_at != null ? latest_pipeline.completed_at : "In progress";
                        $scope.data.qa.overview.tablevalues[tag].testrun = latest_pipeline.uuid;
                        $scope.data.qa.overview.tablevalues[tag].openstackversion = (latest_pipeline.versionconfiguration != null) ? latest_pipeline.versionconfiguration.openstackversion.name : "Unknown";
                        $scope.data.qa.overview.tablevalues[tag].ubuntuversion = (latest_pipeline.versionconfiguration != null) ? latest_pipeline.versionconfiguration.ubuntuversion.name : "Unknown";
                        $q.all([
                            DataService.refresh('productundertest', $scope.data.user, $scope.data.apikey).get({
                                'machineconfigurations__units__jujuservicedeployment__pipeline__uuid': latest_pipeline.uuid,
                                'producttype__name': 'maas'}).$promise
                        ]).then(function([maas_productundertest]) {
                            $scope.data.qa.overview.tablevalues[tag].maasversion = maas_productundertest.objects[0].name;
                        });
                        $q.all([
                            DataService.refresh('productundertest', $scope.data.user, $scope.data.apikey).get({
                                'machineconfigurations__units__jujuservicedeployment__pipeline__uuid': latest_pipeline.uuid,
                                'producttype__name': 'juju'}).$promise
                        ]).then(function([juju_productundertest]) {
                            $scope.data.qa.overview.tablevalues[tag].jujuversion = juju_productundertest.objects[0].name;
                        });
                    });
                });
            });
        };

        function updatePlotAndTableValues() {
            $scope.data.plot_data_loading = true;
            updateSearch();
            active_filters = Common.generateActiveFilters($scope, 'pipeline');
            if ($scope.data.qa.deployedByAutopilot) {
                //TODO: Once we record autopilot as a product, we can include it in the active_filters here for when deployedByAutopilot is true.
            };
            $q.all([$scope.data.qa.solutiontags.$promise]).then(function([solutiontags]) {
                for (var idx in solutiontags.objects) {
                    plotSolutionsGraph(
                        solutiontags.objects[idx],
                        Common.fetchTestDataForJobname(
                            'pipeline_deploy', $scope, solutiontags.objects[idx].name, true));
                };
                $scope.data.plot_data_loading = false
            });
            calcQaReportPeriod();
        };

        today = new Date();
        yesterday = new Date(new Date().setDate(today.getDate() - 1));

        $scope.data.start_dates = [
            '3 Hours Ago',
            '12 Hours Ago',
            '24 Hours Ago',
            '48 Hours Ago',
            '1 Week Ago',
            '2 Weeks Ago',
            '3 Weeks Ago',
            '4 Weeks Ago',
            'Dawn of Time'
        ];
        $scope.data.finish_dates = ['Now'];
        $scope.data.qa.search.defaultFilters = {
            "start_date": '24 Hours Ago',
            "finish_date": 'Now',
        };
        $scope.data.qa.search.individualFilters = Common.individual_filters();
        // set the first search to 24 hours
        // if not doing that run update() instead to apply the above changes
        if($scope.data.qa.search.search == "") {
            $scope.data.qa.search.toggleFilter("start_date", "24 Hours Ago", true);
            $scope.data.qa.search.toggleFilter("finish_date", "Now", true);
        }

        $scope.data = getMetadata($scope);

        $scope.data.qa.getLogoURL = function(svg) {
            return Common.getLogoURL(svg)
        };

        $scope.data.qa.overview = {}
        $scope.data.qa.overview.solutions = {};
        $scope.data.qa.overview.tablevalues = {}
        $scope.data.qa.deployedByAutopilot = true;  // (default setting for checkbox)
        $scope.data.qa.overview.graphValues = {"qa_stack_bar_data": [{"key": "Test Run Success", "valueDict": {}}], "ready": false};

        $scope.data.qa.search.runOnUpdate = updatePlotAndTableValues;
        $scope.$watch('data.qa.deployedByAutopilot', function(deployedByAutopilot) {
            updatePlotAndTableValues();
        });
    }]);
