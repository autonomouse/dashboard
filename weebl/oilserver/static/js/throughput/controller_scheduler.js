var app = angular.module('weebl');
app.controller('schedulerController', [
    '$scope', '$rootScope', '$q', 'DataService',
    function($scope, $rootScope, $q, DataService) {
        binding = this;

        $rootScope.data.show_reports_filters = false;
        $rootScope.data.show_filters = false;
        $rootScope.data.show_search = false;
        $scope.data.throughput = {};
        $scope.data.throughput.scheduler = {};
        $scope.data.throughput.scheduler.job_starts = {};
        data = $scope.data.throughput.scheduler;
        today = new Date();

        function getBuildData(field_name, oldest_date) {
            $scope.data.loading = true;
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

            if (oldest_date) {
                params["build_started_at__gte"] = oldest_date;
            }

            data_field.counts = DataService.refresh(
                    'build', $scope.data.user, $scope.data.apikey
                ).get(params);
            delete params["meta_only"];
            params["limit"] = 1;
            params["order_by"] = "build_started_at";
            data_field.oldest_build = DataService.refresh(
                    'build', $scope.data.user,
                    $scope.data.apikey).get(params);

            return [
                data_field.counts.$promise,
                data_field.oldest_build.$promise]
        };

        function computeAverageDelta(field_name) {
            console.log($scope.data.all_time);
            data_field = data[field_name];
            total_count = data_field.counts.meta.total_count;
            if (total_count > 0) {
                oldest_build_date = new Date(data_field.oldest_build.objects[0].build_started_at);
                /* delta is in milliseconds */
                delta = today - oldest_build_date;
                minutes_delta = (delta / 1000) / 60;
                data.job_starts[field_name] = (minutes_delta / total_count).toFixed(1).toString() + " minutes";
            } else {
                data.job_starts[field_name] = "No runs";
            }
            $scope.data.loading = false;
        };

        four_hours_ago = new Date(new Date(today).setHours(today.getHours() - 4));
        thirty_days_ago = new Date(new Date().setDate(today.getDate() - 30));
        ranges = [
            ['all_time', null],
            ['last_thirty_days', thirty_days_ago],
            ['last_four_hours', four_hours_ago]
        ];

        promises = [];
        for (range of ranges) {
            new_promises = getBuildData(range[0], range[1]);
            promises = promises.concat(new_promises);
        };

        $q.all(promises).then(function() {
            for (range of ranges)
                computeAverageDelta(range[0]);
        });

    }]);
