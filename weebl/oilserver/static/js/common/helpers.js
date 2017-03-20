app.factory('Common', ['$rootScope', '$location', 'DataService', function($rootScope, $location, DataService) {

    function dateSymbolToHours() {
        return {
            'Now': 0,
            '3 Hours Ago': 3,
            '12 Hours Ago': 12,
            '24 Hours Ago': 24,
            '1 Day Ago': 24,
            '48 Hours Ago': 48,
            '2 Days Ago': 48,
            '7 Days Ago': 168,
            '1 Week Ago': 168,
            '2 Weeks Ago': 336,
            '3 Weeks Ago': 504,
            '4 Weeks Ago': 672,
            '30 Days Ago': 720,
            'One Year Ago': 8760,
            'Two Years Ago': 17520, // 24*365*2 Bit risky, what with leap years and all that though...
            'Dawn of Time': null
        }
    };

    function genEarliestAndLatest($scope) {
        angular.forEach(dateSymbolToHours(), function(value, key) {
            if ((angular.isUndefined($scope.data.earliest)) && (value === null)){
                $scope.data.earliest = key;
            };
            if ((angular.isUndefined($scope.data.latest)) && (value === 0)){
                $scope.data.latest = key;
            };
        });
    };

    function initialise($scope) {
        if (angular.isUndefined($scope.data.metadata)) $scope.data.metadata = {};
        if (angular.isUndefined($scope.data.successRate)) $scope.data.successRate = {};
        if (angular.isUndefined($scope.data.bugs)) $scope.data.bugs = {};
        if (angular.isUndefined($scope.data.bugs_affecting_pipeline)) $scope.data.bugs_affecting_pipeline = {};
        if (angular.isUndefined($scope.data.testRuns)) $scope.data.testRuns = {};
        if (angular.isUndefined($scope.data.regexes)) $scope.data.regexes = {};
        if (angular.isUndefined($scope.data.tabs)) {
            $scope.data.tabs = {};
            $scope.data.tabs.testRuns = {};
            $scope.data.tabs.testRuns.predicate = "completed_at";
            $scope.data.tabs.testRuns.reverse = true;
            $scope.data.tabs.bugs = {};
            $scope.data.tabs.bugs.predicate = "occurrence_count";
            $scope.data.tabs.bugs.reverse = true;
            $scope.data.tabs.qa = {};
        };
        if (angular.isUndefined($scope.data.subfilterPlotForm)) {
            $scope.data.subfilterPlotForm = {};
        };
        if (angular.isUndefined($scope.data.results)) $scope.data.results = {};
        if (angular.isUndefined($scope.data.reports)) $scope.data.reports = {};
        if (angular.isUndefined($scope.data.qa)) $scope.data.qa = {};
        $scope.data.job_details = DataService.refresh('jobtype', $scope.data.user, $scope.data.apikey).query({});
        genEarliestAndLatest($scope);
        return $scope
    };

    function arrayToObjectOnProperty(array, property) {
        var outputObject = {};
        array.map(function(o) {
            outputObject[o[property]] = o;
        });
        return outputObject;
    };

    function makeJobDetailsDict(job_details, plot_only) {
        if (angular.isUndefined(plot_only) || (plot_only === null)) {
            plot_only = false;
        };
        var jobDict = {};
        angular.forEach(job_details, function(job_info){
            if ((plot_only === false) || (job_info.plot === true)) {
                jobDict[job_info.name] = job_info;
            };
        });
        return jobDict;
    };

    function orderJobsArray(job_details) {
        return orderArray(job_details, 'order', 'name');
    };

    function orderArray(arr, field1, field2) {
        arr.sort(function(a, b) {
            return cmp(a[field1], b[field1]) || cmp(b[field2], a[field2]);
        });
        return arr;
    };

    function cmp(x, y) {
        return x > y ? 1 : x < y ? -1 : 0;
    };

    function getJobsList(job_details, plot_only) {
        if (angular.isUndefined(plot_only) || (plot_only === null)) {
            plot_only = false;
        };
        var jobsList = [];
        for (var idx in orderJobsArray(job_details)) {
            if ((plot_only === false) || (job_details[idx].plot === true)) {
                if (!angular.isUndefined(job_details[idx].order)) {
                    jobsList.push(job_details[idx].name);
                };
            };
        };
        return jobsList;
    };

    function humaniseDate(datestr) {
        if (angular.isUndefined(datestr) || (datestr === null)) {
            return "";
        };
        var date_obj = new Date(datestr);
        // Return an empty string if the date is invalid:
        if (date_obj == "Invalid Date") {
            return datestr;
        }
        var monthNames = ["Jan", "Feb", "Mar","Apr", "May", "Jun",
                          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
        var day = ('0' + date_obj.getUTCDate()).slice(-2);
        var month_name = monthNames[date_obj.getUTCMonth()];
        var year = ('0' + date_obj.getUTCFullYear()).slice(-2);
        var hours = ('0' + date_obj.getUTCHours()).slice(-2);
        var minutes = ('0' + date_obj.getUTCMinutes()).slice(-2);
        var seconds = ('0' + date_obj.getUTCSeconds()).slice(-2);
        return (day + "-" + month_name + "-" + year + " at " + hours + ":" + minutes + ":" + seconds);
    };

    function getBundleImageLocation(testRunId) {
        return '/static/img/bundles/' + testRunId + '.svg';
    };

    function getLogoURL(svg) {
        return logo_path + svg;
    };

   function checkAllInQueueIsAreResolved(queue) {
       var everything_resolved = true;
       angular.forEach(queue, function(queued_item){
            if (!queued_item.$resolved) everything_resolved = false;
        });
        if (everything_resolved) {
            return true;
        } else {
            return false;
        };
    };

    function abbreviateUUID(UUID) {
        return UUID.slice(0, 4) + "..." + UUID.slice(-5);
    };

    function colourStatus(status) {
        _status = String(status).toLowerCase();
        if (_status === "success") {
            return "green";
        } else if (_status === "unknown"){
            return "gray";
        } else {
            return "red";
        };
    };

    return {
        abbreviateUUID: abbreviateUUID,
        arrayToObjectOnProperty: arrayToObjectOnProperty,
        colourStatus: colourStatus,
        checkAllInQueueIsAreResolved: checkAllInQueueIsAreResolved,
        dateSymbolToHours: dateSymbolToHours,
        getBundleImageLocation: getBundleImageLocation,
        getJobsList: getJobsList,
        getLogoURL: getLogoURL,
        humaniseDate: humaniseDate,
        initialise: initialise,
        makeJobDetailsDict: makeJobDetailsDict,
        orderJobsArray: orderJobsArray,
        orderArray: orderArray
    };
}]);
