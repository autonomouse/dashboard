var app = angular.module('weebl');
app.controller('testRunController', [
    '$scope', '$q', '$rootScope', '$routeParams', 'data', 'DataService', 'Common',
    function($scope, $q, $rootScope, $routeParams, data, DataService, Common) {

        for (var datum in $scope.data) {
            data[datum] = $scope.data[datum]
        };
        $scope.data = data;

        $scope = Common.initialise($scope);

        $scope.data.plot_data_loading = true;

        $scope.data.testRunId = $routeParams.testRunId;
        $scope.data.reports.show_filters = false;
        $scope.data.results.show_filters = false;
        $scope.data.results.show_search = false;

        $scope.data.individual_testRun = DataService.refresh(
                'pipeline', $scope.data.user, $scope.data.apikey).get({id: $scope.data.testRunId});

        active_filters_for_bug = {'knownbugregexes__bugoccurrences__testcaseinstance__build__pipeline__uuid': $scope.data.testRunId};
        $scope.data.bugs_affecting_pipeline = DataService.refresh(
            'bug', $scope.data.user, $scope.data.apikey).get(active_filters_for_bug);

        active_filters_for_build = {'pipeline__uuid': $scope.data.testRunId};
        $scope.data.pipeline_builds = DataService.refresh(
            'build', $scope.data.user, $scope.data.apikey).get(active_filters_for_build);

        active_filters_for_machine = {
            'machineconfigurations__units__jujuservicedeployment__pipeline__uuid': $scope.data.testRunId};
        $scope.data.pipeline_machines = DataService.refresh(
            'machine', $scope.data.user, $scope.data.apikey).get(active_filters_for_machine);

        active_filters_for_testcaseinstance = {'build__pipeline__uuid__in': $scope.data.testRunId,
                                               'testcase__testcaseclass__testframework__version': 'notapplicable'};
        $scope.data.pipeline_testcaseinstance = DataService.refresh(
            'testcaseinstance', $scope.data.user, $scope.data.apikey).get(active_filters_for_testcaseinstance);

        $scope.data.image = Common.getBundleImageLocation($scope.data.testRunId);

        function getJobBuildOutcome(jobDictionary) {
            $q.all([$scope.data.pipeline_testcaseinstance.$promise]).then(function([pipeline_testcaseinstance]) {
                for (var num in pipeline_testcaseinstance.objects) {
                    build = pipeline_testcaseinstance.objects[num].build
                    jobtype_name = build.jobtype.name;
                    if (angular.isUndefined($scope.data.job_build_outcome[jobtype_name])) $scope.data.job_build_outcome[jobtype_name] = {};
                    $scope.data.job_build_outcome[jobtype_name]['jobtype_description'] = jobDictionary[jobtype_name].description;
                    $scope.data.job_build_outcome[jobtype_name]['build_number'] = build.build_id;
                    $scope.data.job_build_outcome[jobtype_name]['jenkinsBuildUrl'] = build.jenkins_build_url;
                    $scope.data.job_build_outcome[jobtype_name]['jobstatus'] = pipeline_testcaseinstance.objects[num].testcaseinstancestatus.name;
                }
                $scope.data.plot_data_loading = false;
            });
        };

        $scope.data.job_build_outcome = {};
        $scope.data.test_results = {};

        $q.all([$scope.data.job_details.$promise]).then(function([job_details]) {
            jobDictionary = Common.makeJobDetailsDict(job_details);
            getJobBuildOutcome(jobDictionary);
            $scope.data.orderedJobsList = Common.getJobsList(job_details);
            $scope.data.jobDictionary = jobDictionary;
        });

    }]);
