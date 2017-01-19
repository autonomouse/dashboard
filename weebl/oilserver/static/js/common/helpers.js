app.factory('Common', ['$rootScope', '$location', function($rootScope, $location) {

    function filterConfig(origin) {
        // It might be sensible to add this stuff to a config file, maybe?

        var model_fields = {
            'completed_at__gte': 'completed_at__gte',
            'completed_at__lte': 'completed_at__lte',
            'openstackversion': 'configurationchoices__openstackversion__in',
            'ubuntuversion': 'configurationchoices__ubuntuversion__in',
            'sdn': 'configurationchoices__sdn__in',
            'compute': 'configurationchoices__compute__in',
            'blockstorage': 'configurationchoices__blockstorage__in',
            'imagestorage': 'configurationchoices__imagestorage__in',
            'database': 'configurationchoices__database__in',
            'environment': 'buildexecutor__jenkins__environment__name__in',
            'testcaseinstancestatus': 'testcaseinstances__testcaseinstancestatus__name__in',
            'machine': 'jujuservicedeployments__units__machineconfiguration__machine__hostname__in',
            'productundertest': 'jujuservicedeployments__units__machineconfiguration__productundertests__name__in|jujuservicedeployments__productundertest__name__in',
            'failedjobs': 'failed_jobtype',
        };

        // Some model fields are actually called something else in the DB, add them here:
        var original_model_names = {
            'failedjobs': 'jobtype',
        };

        // add the path from the origin model to the fields needed:
        var prefixtures = {
            'bug': 'knownbugregexes__bugoccurrences__testcaseinstance__build__pipeline__',
            'build': 'pipeline__',
            'knownbugregex': 'bugoccurrences__testcaseinstance__build__pipeline__',
            'pipeline': '',
            'testcaseinstancestatus': 'testcaseinstances__build__pipeline__',
            'machine': 'machineconfigurations__units__jujuservicedeployment__pipeline__',
            'testcaseinstance': 'build__pipeline__',
            'testframework': 'testcaseclasses__testcases__testcaseinstances__build__pipeline__',
            'testcaseclass': 'testcases__testcaseinstances__build__pipeline__',
            'testcase': 'testcaseinstances__build__pipeline__'
        };

        return [model_fields, prefixtures, original_model_names]
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
        };
        if (angular.isUndefined($scope.data.subfilterPlotForm)) {
            $scope.data.subfilterPlotForm = {};
        };
        if (angular.isUndefined($scope.data.results)) $scope.data.results = {};
        if (angular.isUndefined($scope.data.reports)) $scope.data.reports = {};
        return $scope
    };

    function arrayToObjectOnProperty(array, property) {
        var outputObject = {};
        array.map(function(o) {
            outputObject[o[property]] = o;
        });
        return outputObject;
    };

    function jobtypeLookup(jobname) {
        var dictionary = {
            'pipeline_deploy': 'Deploy Openstack',
            'pipeline_prepare': 'Configure Openstack for test',
            'pipeline_start': 'Initialise test run',
            'test_bundletests': 'Bundletest',
            'test_cloud_image': 'SSH to guest instance',
            'test_tempest_smoke': 'Tempest test suite',
        };
        return dictionary[jobname] != null ? dictionary[jobname] : jobname
    };

    function humaniseDate(datestr) {
        if (angular.isUndefined(datestr) || (datestr === null)) {
            return "";
        };
        var date_obj = new Date(datestr);
        // Return an empty string if the date is invalid:
        if (date_obj == "Invalid Date") {
            return "";
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

    function generateFilterPaths(origin) {
        if (angular.isUndefined(origin)) origin = '';
        model_fields = filterConfig()[0];
        prefixtures = filterConfig()[1];
        return prefixPathToFields(model_fields, prefixtures[origin]);
    };

    function getQueryFieldName(field) {
        original_model_names = filterConfig()[2];
        return angular.isUndefined(original_model_names[field]) ? field : original_model_names[field]
    };


    function generateActiveFilters(scope, origin, exclude_dates) {
        angular.isUndefined(exclude_dates) ? exclude_dates=false : exclude_dates=exclude_dates
        var active_filters = {};
        var field_to_filter = generateFilterPaths(origin);

        for (var enum_field in scope.data.results.search.filters) {
            if (!(enum_field in scope.data.metadata))
                continue;

            enum_values = [];
            scope.data.results.search.filters[enum_field].forEach(function(enum_value) {
                enum_values.push(enum_value.substr(1));
            });

            // generate active filters from the perspective of origin:
            query_field = getQueryFieldName(enum_field);
            if (enum_field != query_field){
                active_filters[field_to_filter[enum_field]] = enum_values;
            } else {
                active_filters[field_to_filter[query_field]] = enum_values;
            };
        };
        // generate date active filters from the perspective of origin:
        if (exclude_dates != true) {
            if (scope.data.start_date)
                active_filters[field_to_filter['completed_at__gte']] = scope.data.start_date;
            if (scope.data.finish_date)
                active_filters[field_to_filter['completed_at__lte']] = scope.data.finish_date;
        };
        return active_filters;
    };

    function prefixPathToFields(fields, path) {
        for (var field in fields) {
            expandedFieldParts = [];
            fieldParts = fields[field].split("|");
            for (index in fieldParts) {
                expandedFieldParts.push(path + fieldParts[index]);
            }
            fields[field] = expandedFieldParts.join("|");
        }
        return fields;
    };

    function getFilterModels() {
        var enum_fields = Object.keys(generateFilterPaths());
        var ignores = [
            'completed_at__gte',
            'completed_at__lte',
            'sdn',
            'compute',
            'blockstorage',
            'imagestorage',
            'database',
        ];
        for (var i in ignores) {
            index = enum_fields.indexOf(ignores[i]);
            enum_fields.splice(index, 1);
        }
        return enum_fields;
    };

    function getBundleImageLocation(testRunId) {
    return '/static/img/bundles/' + testRunId + '.svg';
    };

    return {
      initialise: initialise,
      arrayToObjectOnProperty: arrayToObjectOnProperty,
      humaniseDate: humaniseDate,
      generateActiveFilters: generateActiveFilters,
      generateFilterPaths: generateFilterPaths,
      getFilterModels: getFilterModels,
      jobtypeLookup: jobtypeLookup,
      getQueryFieldName: getQueryFieldName,
      getBundleImageLocation: getBundleImageLocation,
    };
}]);
