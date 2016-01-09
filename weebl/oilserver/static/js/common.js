app.factory('Common', ['$rootScope', function($rootScope) {

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

    function highlightTab(scope, tab) {
        $rootScope.title = scope.data.tabs[tab].pagetitle;
        scope.data.currentpage = tab;
    };

    function generateActiveFilters(scope, origin) {
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
            active_filters[field_to_filter[enum_field]] = enum_values;
        }
        // generate date active filters from the perspective of origin:
        if (scope.data.start_date)
            active_filters[field_to_filter['completed_at__gte']] = scope.data.start_date;
        if (scope.data.finish_date)
            active_filters[field_to_filter['completed_at__lte']] = scope.data.finish_date;

        return active_filters;
    };

    function prefixPathToFields(fields, path) {
        for (var field in fields) {
            fields[field] = path + fields[field];
        }
        return fields;
    };

    function generateFilterPaths(origin) {
        if (typeof(origin)==='undefined') origin = '';

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
        };

        // add the path from the origin model to the fields needed:
        var prefixtures = {
            'bug': 'knownbugregex__bugoccurrences__build__pipeline__',
            'build': 'pipeline__',
            'knownbugregex': 'bugoccurrences__build__pipeline__',
            'pipeline': '',
            'buildstatus': 'build__pipeline__',
        };

        return prefixPathToFields(model_fields, prefixtures[origin]);
    };

    function getFilterModels() {
        var enum_fields = Object.keys(generateFilterPaths());
        index = enum_fields.indexOf("completed_at__gte");
        enum_fields.splice(index, 1);
        index = enum_fields.indexOf("completed_at__lte");
        enum_fields.splice(index, 1);
        return enum_fields;
    };

    return {
      humaniseDate: humaniseDate,
      highlightTab: highlightTab,
      generateActiveFilters: generateActiveFilters,
      generateFilterPaths: generateFilterPaths,
      getFilterModels: getFilterModels,
    };
}]);
