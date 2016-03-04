app.factory('Common', ['$rootScope', function($rootScope) {

    function filterConfig(origin) {
        // It might be sensible to add this stuff to a config file, maybe?

        var model_fields = {
            'completed_at__gte': 'completed_at__gte',
            'completed_at__lte': 'completed_at__lte',
            'openstackversion': 'openstackversion__name__in',
            'ubuntuversion': 'ubuntuversion__name__in',
            'sdn': 'sdn__name__in',
            'compute': 'compute__name__in',
            'blockstorage': 'blockstorage__name__in',
            'imagestorage': 'imagestorage__name__in',
            'database': 'database__name__in',
            'environment': 'buildexecutor__jenkins__environment__name__in',
            'buildstatus': 'build__buildstatus__name__in',
            'machine': 'machineconfiguration__machine__hostname__in',
            'productundertest': 'machineconfiguration__productundertest__name__in',
            'failedjobs': 'build__jobtype__name__in',
        };

        // Some model fields are actually called something else in the DB, add them here:
        var original_model_names = {
            'failedjobs': 'jobtype',
        };

        // Some fields may be linked to specific instances of other fields, add here:
        var linked_fields = {
            'failedjobs': ['buildstatus', 'failure'],
        };

        // add the path from the origin model to the fields needed:
        var prefixtures = {
            'bug': 'knownbugregex__bugoccurrences__build__pipeline__',
            'build': 'pipeline__',
            'knownbugregex': 'bugoccurrences__build__pipeline__',
            'pipeline': '',
            'buildstatus': 'build__pipeline__',
            'machine': 'machineconfiguration__pipeline__',
        };

        return [model_fields, prefixtures, original_model_names, linked_fields]
    };

    function initialise($scope) {
        if (typeof($scope.data.metadata)==='undefined') $scope.data.metadata = {};
        if (typeof($scope.data.successRate)==='undefined') $scope.data.successRate = {};
        if (typeof($scope.data.bugs)==='undefined') $scope.data.bugs = {};
        if (typeof($scope.data.bugs_affecting_pipeline)==='undefined') $scope.data.bugs_affecting_pipeline = {};
        if (typeof($scope.data.testRuns)==='undefined') $scope.data.testRuns = {};
        if (typeof($scope.data.regexes)==='undefined') $scope.data.regexes = {};

        if (typeof($scope.data.sections)==='undefined') {
            $scope.data.sections = {};
            $scope.data.sections.results = {};
            $scope.data.sections.results.pagetitle = "Results";
        };

        if (typeof($scope.data.tabs)==='undefined') {
            $scope.data.tabs = {};
            $scope.data.tabs.successRate = {};
            $scope.data.tabs.successRate.pagetitle = "Success Rate";
            $scope.data.tabs.testRuns = {};
            $scope.data.tabs.testRuns.pagetitle = "Test Runs";
            $scope.data.tabs.testRuns.predicate = "completed_at";
            $scope.data.tabs.testRuns.reverse = true;
            $scope.data.tabs.bugs = {};
            $scope.data.tabs.bugs.pagetitle = "Bugs";
            $scope.data.tabs.bugs.predicate = "occurrences";
            $scope.data.tabs.bugs.reverse = true;
            $scope.data.subfilter_plot_form = {}
        };
        return $scope
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
        var date_obj = new Date(datestr);
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

    function highlightSection(scope, section) {
        $rootScope.section = scope.data.sections[section].pagetitle;
        scope.data.currentsection = section;
    };

    function highlightTab(scope, tab) {
        $rootScope.title = scope.data.tabs[tab].pagetitle;
        scope.data.currentpage = tab;
    };

    function generateFilterPaths(origin) {
        if (typeof(origin)==='undefined') origin = '';
        model_fields = filterConfig()[0];
        prefixtures = filterConfig()[1];
        return prefixPathToFields(model_fields, prefixtures[origin]);
    };

    function getQueryFieldName(field) {
        original_model_names = filterConfig()[2];
        return original_model_names[field] != undefined ? original_model_names[field] : field
    };


    function generateActiveFilters(scope, origin, exclude_dates) {
        exclude_dates === undefined ? exclude_dates=false : exclude_dates=exclude_dates
        linked_fields = filterConfig()[3];
        var active_filters = {};
        var field_to_filter = generateFilterPaths(origin);

        for (var enum_field in scope.data.filters) {
            if (!(enum_field in scope.data.metadata))
                continue;

            enum_values = [];
            scope.data.filters[enum_field].forEach(function(enum_value) {
                enum_values.push(enum_value.substr(1));
            });

            // generate active filters from the perspective of origin:
            query_field = getQueryFieldName(enum_field);
            if (enum_field != query_field){
                active_filters[field_to_filter[enum_field]] = enum_values;
                for (var key in linked_fields) {
                    active_filters[field_to_filter[linked_fields[key][0]]] = linked_fields[key][1]
                };
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
            fields[field] = path + fields[field];
        }
        return fields;
    };

    function getFilterModels() {
        var enum_fields = Object.keys(generateFilterPaths());
        index = enum_fields.indexOf("completed_at__gte");
        enum_fields.splice(index, 1);
        index = enum_fields.indexOf("completed_at__lte");
        enum_fields.splice(index, 1);
        return enum_fields;
    };

    function getBundleImageLocation(testRunId) {
	return '/static/img/bundles/' + testRunId + '.svg';
    };

    return {
      initialise: initialise,
      humaniseDate: humaniseDate,
      highlightTab: highlightTab,
      highlightSection: highlightSection,
      generateActiveFilters: generateActiveFilters,
      generateFilterPaths: generateFilterPaths,
      getFilterModels: getFilterModels,
      jobtypeLookup: jobtypeLookup,
      getQueryFieldName: getQueryFieldName,
      getBundleImageLocation: getBundleImageLocation,
    };
}]);
