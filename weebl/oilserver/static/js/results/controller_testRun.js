var app = angular.module('weebl');
app.controller('testRunController', [
    '$scope', '$q', '$rootScope', '$routeParams', 'data', 'DataService', 'Common', 'FilterFactory',
    function($scope, $q, $rootScope, $routeParams, data, DataService, Common, FilterFactory) {

        for (var datum in $scope.data) {
            data[datum] = $scope.data[datum]
        };
        $scope.data = data;

        $scope = Common.initialise($scope);

        var img = document.getElementById("bundle_svg");
        img.onerror = function () {
            this.style.display = "none";
        }

        $scope.data.plot_data_loading = true;

        $scope.data.testRunId = $routeParams.testRunId;
        $scope.data.reports.show_filters = false;
        $scope.data.results.show_filters = false;
        $scope.data.qa.show_filters = false;
        $scope.data.results.show_search = false;
        $scope.data.qa.show_search = false;
        $scope.data.producttypes = {}
        $q.all([
            DataService.refresh('producttype', $scope.data.user, $scope.data.apikey).query({}).$promise
        ]).then(function([producttype]) {
            angular.forEach(producttype, function(product){
                $scope.data.producttypes[product.name] = {'type': product.name, 'name': []};
                $q.all([
                    DataService.refresh('productundertest', $scope.data.user, $scope.data.apikey).get({
                        'machineconfigurations__units__jujuservicedeployment__pipeline__uuid': $scope.data.testRunId,
                        'producttype__name': product.name}).$promise
                ]).then(function([productundertest]) {
                    var put = productundertest.objects[0];
                    if (angular.isDefined(put)) $scope.data.producttypes[product.name]['name'].push(put.name);
                });
                $q.all([
                    DataService.refresh('productundertest', $scope.data.user, $scope.data.apikey).get({
                        'jujuservicedeployments__pipeline__uuid': $scope.data.testRunId,
                        'producttype__name': product.name}).$promise
                ]).then(function([productundertest]) {
                    var put = productundertest.objects[0];
                    if (angular.isDefined(put)) $scope.data.producttypes[product.name]['name'].push(put.name);
                });
            });
        });

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
                    jobstatus = pipeline_testcaseinstance.objects[num].testcaseinstancestatus.name;
                    $scope.data.job_build_outcome[jobtype_name]['jobstatus'] = jobstatus;
                    getIndividualTestResults(jobtype_name, jobstatus);
                }
                $scope.data.plot_data_loading = false;
            });
            $scope.data.pipeline_testcaseinstance;
        };

        function replaceZeroesWithEmptyString(count) {
            /* Increase signal-to-noise by removing all these zeroes everywhere...*/
            return count > 0 ? count : "";
        };

        function getTrueTestCount(pass_tci_meta, fail_tci_meta, skip_tci_meta, err_tci_meta, abort_tci_meta, jobstatus) {
            /*Remove the job itself (recorded in the DB as a testcaseinstance), so we get an accurate number of the subtests conducted.*/
            var pass = jobstatus != "success" ? pass_tci_meta.meta.total_count : pass_tci_meta.meta.total_count - 1;
            var fail = jobstatus != "failure" ? fail_tci_meta.meta.total_count : fail_tci_meta.meta.total_count - 1;
            var skip = jobstatus != "skipped" ? skip_tci_meta.meta.total_count : skip_tci_meta.meta.total_count - 1;
            var err = jobstatus != "error" ? err_tci_meta.meta.total_count : err_tci_meta.meta.total_count - 1;
            var abort = jobstatus != "aborted" ? abort_tci_meta.meta.total_count : abort_tci_meta.meta.total_count - 1;
            // Don't worry about "Unknown" as it is not listed in the table.
            return [replaceZeroesWithEmptyString(pass),
                    replaceZeroesWithEmptyString(fail),
                    replaceZeroesWithEmptyString(skip),
                    replaceZeroesWithEmptyString(err),
                    replaceZeroesWithEmptyString(abort)]
        };

        $scope.data.colourStatus = Common.colourStatus;
        $scope.data.joinURLs = Common.joinURLs;

        function getIndividualTestResults(jobname, jobstatus) {
            if (angular.isUndefined($scope.data.test_results[jobname])) $scope.data.test_results[jobname] = {};
            var detail_params = {'build__pipeline__uuid': $scope.data.testRunId, 'build__jobtype__name': jobname};
            var meta_params = FilterFactory.metaWith(detail_params, true);

            // Get numbers of tests that passed, failed, etc...
            $q.all([
                DataService.refresh('testcaseinstance', $scope.data.user, $scope.data.apikey).get(angular.extend({}, {
                    'testcaseinstancestatus__name': 'success'}, meta_params)).$promise,
                DataService.refresh('testcaseinstance', $scope.data.user, $scope.data.apikey).get(angular.extend({}, {
                    'testcaseinstancestatus__name': 'failure'}, meta_params)).$promise,
                DataService.refresh('testcaseinstance', $scope.data.user, $scope.data.apikey).get(angular.extend({}, {
                    'testcaseinstancestatus__name': 'skipped'}, meta_params)).$promise,
                DataService.refresh('testcaseinstance', $scope.data.user, $scope.data.apikey).get(angular.extend({}, {
                    'testcaseinstancestatus__name': 'error'}, meta_params)).$promise,
                DataService.refresh('testcaseinstance', $scope.data.user, $scope.data.apikey).get(angular.extend({}, {
                    'testcaseinstancestatus__name': 'aborted'}, meta_params)).$promise
            ]).then(function([pass_tci_meta, fail_tci_meta, skip_tci_meta, err_tci_meta, abort_tci_meta]) {
                [$scope.data.test_results[jobname].pass_count,
                $scope.data.test_results[jobname].fail_count,
                $scope.data.test_results[jobname].skip_count,
                $scope.data.test_results[jobname].err_count,
                $scope.data.test_results[jobname].abort_count]  = getTrueTestCount(
                    pass_tci_meta, fail_tci_meta, skip_tci_meta, err_tci_meta, abort_tci_meta, jobstatus);
            });

            // Get details of test that failed
            var fail_tci_params = angular.extend({}, {'testcaseinstancestatus__name': 'failure'}, detail_params)
            $q.all([DataService.refresh('testcaseinstance', $scope.data.user, $scope.data.apikey).get(fail_tci_params).$promise
            ]).then(function([failed_testcaseinstances]) {
                angular.forEach(failed_testcaseinstances.objects, function(testcaseinstance){
                    if (angular.isUndefined($scope.data.test_results[jobname]['failed_tests'])) {
                        $scope.data.test_results[jobname]['failed_tests'] = [];
                    };
                    if (testcaseinstance.testcase.name != jobname) {
                        var testcase = testcaseinstance.testcase.name != "" ? testcaseinstance.testcase.name : "N/A";
                        var testcaseclass = testcaseinstance.testcase.testcaseclass.name != "" ? testcaseinstance.testcase.testcaseclass.name : "N/A";
                        var test = [testcaseclass, testcase];
                        $scope.data.test_results[jobname]['failed_tests'].push(test);
                    };
                    $scope.data.test_results[jobname]['failed_tests'].sort();
                });
            });

            // Get details of test that erred
            var err_tci_params = angular.extend({}, {'testcaseinstancestatus__name': 'error'}, detail_params)
            $q.all([DataService.refresh('testcaseinstance', $scope.data.user, $scope.data.apikey).get(err_tci_params).$promise
            ]).then(function([erred_testcaseinstances]) {
                angular.forEach(erred_testcaseinstances.objects, function(testcaseinstance){
                    if (angular.isUndefined($scope.data.test_results[jobname]['erred_tests'])) {
                        $scope.data.test_results[jobname]['erred_tests'] = [];
                    };
                    if (testcaseinstance.testcase.name != jobname) {
                        var testcase = testcaseinstance.testcase.name != "" ? testcaseinstance.testcase.name : "N/A";
                        var testcaseclass = testcaseinstance.testcase.testcaseclass.name != "" ? testcaseinstance.testcase.testcaseclass.name : "N/A";
                        var test = [testcaseclass, testcase];
                        $scope.data.test_results[jobname]['erred_tests'].push(test);
                    };
                    $scope.data.test_results[jobname]['erred_tests'].sort();
                });
            });
        };
        $scope.data.job_build_outcome = {};
        $scope.data.test_results = {};

        $q.all([$scope.data.job_details.$promise]).then(function([job_details]) {
            jobDictionary = Common.makeJobDetailsDict(job_details);
            $scope.data.orderedJobsList = Common.getJobsList(job_details);
            $scope.data.jobDictionary = jobDictionary;
            getJobBuildOutcome(jobDictionary);
        });

    }]);
