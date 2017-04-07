var app = angular.module('weebl');
app.controller('qaOverviewController', [
    '$scope', '$rootScope', '$q', 'data', 'SearchFactory', 'graphFactory', 'DataService', 'Common', 'FilterFactory',
    function($scope, $rootScope, $q, data, SearchFactory, graphFactory, DataService, Common, FilterFactory) {
        binding = this;
        binding.user = $scope.data.user;
        binding.apikey = $scope.data.apikey;

        $scope.data.solutiontags = DataService.refresh(
                'solutiontag', $scope.data.user, $scope.data.apikey).get({});

        if ($scope.data.search === undefined)
            $scope.data.search = new SearchFactory.Search();
        defaultFilters = {
            "start_date": 'Dawn of Time',
            "finish_date": 'Now',
        };
        $scope = Common.initialise($scope);
        $scope.data.search.init(defaultFilters);

        $scope.data.reports.show_filters = false;
        $rootScope.data.show_filters = false;
        $scope.data.show_search = false;

        $scope.data.default_tab = 'qa';
        $scope.data.default_section = 'overview';

        $scope.data.humaniseDate = Common.humaniseDate;

        function plotSolutionsGraph(solutiontag, overview, output) {
            var tag = solutiontag.name;
            var colour = solutiontag.colour;
            $q.all([output[0].$promise, output[1].$promise, output[2].$promise]).then(function([pass, skip, jobtotal]) {
                overview.tablevalues[tag].success_rate = graphFactory.calcPercentage(
                    pass.meta.total_count,
                    jobtotal.meta.total_count,
                    skip.meta.total_count);
                $q.all([$scope.data.solutiontags.$promise]).then(function([solutiontags]) {
                     overview.tablevalues[tag].show = true;
                     for (var obj_idx in solutiontags.objects) {
                        if (solutiontags.objects[obj_idx].name === tag)
                            overview.tablevalues[tag].show = solutiontags.objects[obj_idx].show;
                    };
                    $q.all([
                        DataService.refresh('solution', $scope.data.user, $scope.data.apikey).get({
                            'solutiontag__name': tag}).$promise
                    ]).then(function([solution]) {
                        $q.all([
                            DataService.refresh('testcaseinstance', $scope.data.user, $scope.data.apikey).query({
                                'build__pipeline__solution__solutiontag__name': tag,
                                'testcase__testcaseclass__testframework__name': 'pipeline_deploy',
                                'limit':10,
                                'order_by': '-build__pipeline__completed_at'}).$promise
                        ]).then(function([latest_pipeline_tcis]) {
                            if (latest_pipeline_tcis.length) {
                                overview.tablevalues[tag].last_ten_pipelines = latest_pipeline_tcis
                                latest_pipeline_tci = latest_pipeline_tcis[0]
                                overview.tablevalues[tag].deploystatus = latest_pipeline_tci.testcaseinstancestatus.name;
                                var latest_pipeline = latest_pipeline_tci.build.pipeline
                                overview.tablevalues[tag].date = latest_pipeline.completed_at != null ? latest_pipeline.completed_at : "In progress";
                                overview.tablevalues[tag].testrun = latest_pipeline.uuid;
                                overview.tablevalues[tag].openstackversion = (
                                    latest_pipeline.versionconfiguration != null) ? latest_pipeline.versionconfiguration.openstackversion.name : "Unknown";
                                overview.tablevalues[tag].ubuntuversion = (
                                    latest_pipeline.versionconfiguration != null) ? latest_pipeline.versionconfiguration.ubuntuversion.name : "Unknown";
                                $q.all([
                                    DataService.refresh('productundertest', $scope.data.user, $scope.data.apikey).get({
                                        'machineconfigurations__units__jujuservicedeployment__pipeline__uuid': latest_pipeline.uuid,
                                        'producttype__name': 'maas'}).$promise
                                ]).then(function([maas_productundertest]) {
                                    overview.tablevalues[tag].maasversion = maas_productundertest.objects[0].name;
                                });
                                $q.all([
                                    DataService.refresh('productundertest', $scope.data.user, $scope.data.apikey).get({
                                        'machineconfigurations__units__jujuservicedeployment__pipeline__uuid': latest_pipeline.uuid,
                                        'producttype__name': 'juju'}).$promise
                                ]).then(function([juju_productundertest]) {
                                    overview.tablevalues[tag].jujuversion = juju_productundertest.objects[0].name;
                                });
                            };
                        });
                    });

                });
            }, $scope);
        };

        function updatePlotAndTableValues() {
            $scope.data.plot_data_loading = true;
            $q.all([$scope.data.solutiontags.$promise]).then(function([solutiontags]) {
                var sortedSolTags = Common.orderArray(solutiontags.objects, 'name', null);
                for (var idx in sortedSolTags) {
                    var this_tag = solutiontags.objects[idx];
                    $scope.data.overview.tablevalues[this_tag.name] = {'name': this_tag.name, 'success_rate': '0.00'};
                    plotSolutionsGraph(this_tag, $scope.data.overview, FilterFactory.fetchTestDataForJobname(
                            'pipeline_deploy', $scope, solutiontags.objects[idx].name, true));
                    /* TODO: if ($scope.data.deployedByAutopilot) then supply an extra autopilot_only arg. Once we
                    start recording autopilot as a product, we can do this to include it in the active_filters here
                    for when deployedByAutopilot is true. */
                };
                $scope.data.plot_data_loading = false
            });
        };

        $scope.data.getLogoURL = function(svg) { return Common.getLogoURL(svg) };

        $scope.data.overview = {}
        $scope.data.overview.solutions = {};
        $scope.data.overview.tablevalues = {}
        $scope.data.deployedByAutopilot = true;  // (default setting for checkbox)

        $scope.data.search.runOnUpdate = updatePlotAndTableValues;
        $scope.$watch('data.deployedByAutopilot', function(deployedByAutopilot) {
            updatePlotAndTableValues();
        });
    }]);
