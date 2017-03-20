app.factory('FilterFactory', ['DataService', 'Common', function(DataService, Common) {

    function filterConfig(origin) {
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
            'solutiontag': 'solution__solutiontag__name__in',
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
            'testcase': 'testcaseinstances__build__pipeline__',
            'solutiontag': 'solution__'
        };
        return [model_fields, prefixtures, original_model_names]
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

    function fetchTestDataForJobname(jobname, $scope, tag, meta_only) {
        var model = 'testcaseinstance';
        if (angular.isUndefined(meta_only)) meta_only === true;
        var local_filters = metaWith(generateActiveFilters($scope, model), meta_only);
        local_filters['build__jobtype__name'] = jobname;
        local_filters['successful_jobtype'] = jobname;
        if ((angular.isDefined(tag)) && (tag != null)) local_filters['build__pipeline__solution__solutiontag__name'] = tag;
        local_filters['testcaseinstancestatus__name'] = 'success';
        var pass = DataService.refresh(model, $scope.data.user, $scope.data.apikey).get(local_filters);
        local_filters['testcaseinstancestatus__name'] = 'skipped';
        var skip = DataService.refresh(model, $scope.data.user, $scope.data.apikey).get(local_filters);
        delete local_filters['successful_jobtype'];
        delete local_filters['testcaseinstancestatus__name'];
        var jobtotal = DataService.refresh(model, $scope.data.user, $scope.data.apikey).get(local_filters);
        total = null;
        pipeline_total = null;
        return [pass, skip, jobtotal]
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

            if (!Array.isArray(enum_values)) {
                enum_values = [enum_values];
            };
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

    function generateFilterPaths(origin) {
        if (angular.isUndefined(origin)) origin = '';
        model_fields = filterConfig()[0];
        prefixtures = filterConfig()[1];
        return prefixPathToFields(model_fields, prefixtures[origin]);
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

    function getTotals($scope) {
        var local_filters = metaWith(generateActiveFilters($scope, 'testcaseinstance'), true);
        var total = DataService.refresh('testcaseinstance', $scope.data.user, $scope.data.apikey).get(local_filters);

        var local_filters = metaWith(generateActiveFilters($scope, 'pipeline'), true);
        var pipeline_total = DataService.refresh('pipeline', $scope.data.user, $scope.data.apikey).get(local_filters);
        return [total, pipeline_total];
    };

    function getQueryFieldName(field) {
        original_model_names = filterConfig()[2];
        return angular.isUndefined(original_model_names[field]) ? field : original_model_names[field]
    };

    function individual_filters() {
        return ["start_date", "finish_date"]
    };

    function metaWith(object, meta_only) {
        if (angular.isUndefined(meta_only)) meta_only === true;
        dict = {'meta_only': meta_only, 'limit': 1, 'max_limit': 1};
        return angular.extend({}, dict, object);
    }

    function updateStartDate(start_date) {
        /* update start date */
        if (start_date.includes("Ago") || start_date.includes("Time")) {
            var hours_offset = Common.dateSymbolToHours()[start_date];
            console.log("Updating to last %d hours (%d days).", hours_offset, (hours_offset / 24));
            if (hours_offset === null) {
                data_start_date = null;
            } else {
                var today = new Date();
                prior_date = new Date(new Date().setHours(today.getHours()-(hours_offset)))
                data_start_date = prior_date.toISOString();
            }
        } else {
            console.log("Taking start date literally.");
            data_start_date = start_date;
        }
        return data_start_date;
    };

    function updateFinishDate(finish_date) {
        /* update finish_date */
        if ((finish_date == 'Now') || (finish_date == null)) {
            data_finish_date = null;
        } else {
            console.log("Taking finish date literally.");
            data_finish_date = finish_date;
        }
        return data_finish_date;
    };

    return {
        fetchTestDataForJobname: fetchTestDataForJobname,
        generateActiveFilters: generateActiveFilters,
        generateFilterPaths: generateFilterPaths,
        getFilterModels: getFilterModels,
        getTotals: getTotals,
        getQueryFieldName: getQueryFieldName,
        individual_filters: individual_filters,
        metaWith: metaWith,
        updateFinishDate: updateFinishDate,
        updateStartDate: updateStartDate
    };
}]);
