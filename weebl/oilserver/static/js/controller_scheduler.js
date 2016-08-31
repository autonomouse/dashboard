var app = angular.module('weebl');
app.controller('schedulerController', [
    '$scope', '$q', 'DataService',
    function($scope, $q, DataService) {
        binding = this;

        $scope.data.reports.show_filters = false;
        $scope.data.results.show_filters = false;
        $scope.data.results.show_search = false;
        $scope.data.throughput = {};
        $scope.data.throughput.scheduler = {};
        $scope.data.throughput.scheduler.job_starts = {};

        function getAverageStartDelta(field_name) {
            $scope.data.loading = true;
            data = $scope.data.throughput.scheduler;
            /* Find the number of starts and the date of the first
             * start, so we can calculate the average time for a job
             * to start over that time period.
             */
            data[field_name] = {}
            data_field = data[field_name];
            params = {
                "jobtype__name": "pipeline_start",
                "meta_only": true
            };
            data_field.counts = DataService.refresh(
                    'build', $scope.data.user, $scope.data.apikey
                ).get(params);
            delete params["meta_only"];
            params["limit"] = 1;
            params["order_by"] = "build_started_at";
            data_field.oldest_build = DataService.refresh(
                    'build', $scope.data.user, $scope.data.apikey).get(params);
            $q.all([
                data_field.counts.$promise,
                data_field.oldest_build.$promise,
            ]).then(function() {
                console.log($scope.data.all_time);
                total_count = data_field.counts.meta.total_count;
                if (total_count > 0) {
                    today = new Date();
                    oldest_build_date = new Date(data_field.oldest_build.objects[0].build_started_at);
                    /* delta is in milliseconds */
                    delta = today - oldest_build_date;
                    minutes_delta = (delta / 1000) / 60;
                    data.job_starts[field_name] = (minutes_delta / total_count).toFixed(2);
                } else {
                    data.job_starts[field_name] = "No runs.";
                }
                $scope.data.loading = false;
            });
        };

        getAverageStartDelta('all_time');
    }]);
