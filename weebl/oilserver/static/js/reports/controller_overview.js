var app = angular.module('weebl');
app.controller('overviewReportController', [
    '$scope', '$q', 'SearchFactory', 'DataService', 'Common',
    function($scope, $q, SearchFactory, DataService, Common) {
        $scope = Common.initialise($scope);
        if(angular.isUndefined($scope.data.reports.search)) $scope.data.reports.search = new SearchFactory.Search();
        $scope.data.reports.search.init();
        if(angular.isUndefined($scope.data.reports.metadata)) $scope.data.reports.metadata = {};
        if(angular.isUndefined($scope.data.reports.overview)) $scope.data.reports.overview = {};
        $scope.data.reports.show_filters = true;
        $scope.data.results.show_filters = false;
        $scope.data.qa.show_filters = false;
        $scope.data.results.show_search = false;
        $scope.data.qa.show_search = false;

        $scope.data.reports.search.defaultFilters = {"date": "Last 30 Days", "report": "Overall"};
        $scope.data.reports.search.individualFilters = ["date", "report"];
        $scope.data.reports.search.runOnUpdate = getOverviewData;
        getMetadata();

        var dateSymbolToDays = {
            'Last 24 Hours': 1,
            'Last 7 Days': 7,
            'Last 30 Days': 30,
            'Last Year': 365,
            'All Time': null
        };

        var expansionTemplates = {
            'pipeline': {
                'productundertest': 'jujuservicedeployments__units__machineconfiguration__productundertests__|jujuservicedeployments__productundertest__',
                'environment': 'buildexecutor__jenkins__environment__'},
            'testcaseinstance': {
                'productundertest':'build__pipeline__jujuservicedeployments__units__machineconfiguration__productundertests__|build__pipeline__jujuservicedeployments__productundertest__',
                'pipeline': 'build__pipeline__',
                'environment': 'build__pipeline__buildexecutor__jenkins__environment__'},
            'versionconfiguration': {
                'productundertest':'pipelines__jujuservicedeployments__units__machineconfiguration__productundertests__|pipelines__jujuservicedeployments__productundertest__',
                'pipeline': 'pipelines__',
                'environment': 'pipelines__buildexecutor__jenkins__environment__'},
            'configurationchoices': {
                'productundertest':'pipeline__jujuservicedeployments__units__machineconfiguration__productundertests__|pipeline__jujuservicedeployments__productundertest__',
                'pipeline': 'pipeline__',
                'environment': 'pipeline__buildexecutor__jenkins__environment__'},
            'vendor': {
                'productundertest': 'productundertests__machineconfigurations__units__jujuservicedeployment__pipeline__jujuservicedeployments__units__machineconfiguration__productundertests__|productundertests__machineconfigurations__units__jujuservicedeployment__pipeline__jujuservicedeployments__productundertest__',
                'pipeline': 'productundertests__machineconfigurations__units__jujuservicedeployment__pipeline__',
                'environment': 'productundertests__machineconfigurations__units__jujuservicedeployment__pipeline__buildexecutor__jenkins__environment__'},
            'hardwareProducts': {
                'productundertest': 'machineconfigurations__units__jujuservicedeployment__pipeline__jujuservicedeployments__units__machineconfiguration__productundertests__|machineconfigurations__units__jujuservicedeployment__pipeline__jujuservicedeployments__productundertest__',
                'pipeline': 'machineconfigurations__units__jujuservicedeployment__pipeline__',
                'environment': 'machineconfigurations__units__jujuservicedeployment__pipeline__buildexecutor__jenkins__environment__'},
            'producttype': {
                'productundertest': 'productundertests__jujuservicedeployments__pipeline__jujuservicedeployments__units__machineconfiguration__productundertests__|productundertests__',
                'pipeline': 'productundertests__machineconfigurations__units__jujuservicedeployment__pipeline__|productundertests__jujuservicedeployments__pipeline__',
                'environment': 'productundertests__jujuservicedeployments__pipeline__buildexecutor__jenkins__environment__|productundertests__machineconfigurations__units__jujuservicedeployment__pipeline__buildexecutor__jenkins__environment__'},
            'jujuservice': {
                'productundertest': 'jujuservicedeployments__pipeline__jujuservicedeployments__units__machineconfiguration__productundertests__',
                'pipeline': 'jujuservicedeployments__pipeline__',
                'environment': 'jujuservicedeployments__pipeline__buildexecutor__jenkins__environment__'},
            'productundertest': {
                'productundertest': '',
                'environment': 'jujuservicedeployments__pipeline__buildexecutor__jenkins__environment__|machineconfigurations__units__jujuservicedeployment__pipeline__buildexecutor__jenkins__environment__'},
        };

        if($scope.data.reports.search.search == "") {
            $scope.data.reports.search.update();
        }

        function getMetadata() {
            $scope.data.reports.metadata.reportPeriods = DataService.refresh(
                    'reportperiod', $scope.data.user, $scope.data.apikey).query({});
            $scope.data.reports.metadata.environments = DataService.refresh(
                    'environment', $scope.data.user, $scope.data.apikey).query({});
            $scope.data.reports.metadata.reportGroups = DataService.refresh(
                    'report', $scope.data.user, $scope.data.apikey).query({});
            $scope.data.reports.metadata.vendors = DataService.refresh(
                    'vendor', $scope.data.user, $scope.data.apikey).query({});
        }

        function getProperties(object, property) {
            return object.map(function(o) {
                return o[property];
            });
        }

        function waitForResolve(promisedResources, callback) {
            resourceKeys = Object.keys(promisedResources);
            resources = resourceKeys.map(function(key) {return promisedResources[key];});
            promises = getProperties(resources, '$promise');
            $q.all(promises).then(function(data) {
                resolved = {};
                for (i = 0; i < data.length; i++){
                    resolved[resourceKeys[i]] = data[i];
                }
                callback(resolved);
            });
        }

        function crossProduct(objects) {
            value = {};
            totals = [];
            for(objectIndex in objects){
                object = objects[objectIndex]
                keys = Object.keys(object).sort();
                total = []
                for(keyIndex in keys){
                    key = keys[keyIndex]
                    if(!(key in value)){
                        value[key] = d3.set();
                    }
                    if(angular.isObject(object[key]) && "name" in object[key]) {
                        value[key].add(object[key].name);
                        total.push(object[key].name);
                    }
                }
                totals[total.join("")] = true;
            }
            valueKeys = Object.keys(value);
            for(valueIndex in valueKeys){
                value[valueKeys[valueIndex]] = value[valueKeys[valueIndex]].values().sort();
            }
            return {'axes': value, 'items': totals};
        }

        function getProductsFilter(name) {
            productundertest = {};
            reports = Common.arrayToObjectOnProperty($scope.data.reports.metadata.reportGroups, 'name');
            vendors = Common.arrayToObjectOnProperty($scope.data.reports.metadata.vendors, 'name');
            if(!(name in reports)) {
                return productundertest;
            }
            if(reports[name].productundertests.length == 0 && name in vendors) {
                productundertest.vendor__name__exact = name;
            } else {
                productundertest.reports__name__exact = name;
            }
            return productundertest;
        }

        function getDateFilter(period) {
            filter_set = {};
            periods = Common.arrayToObjectOnProperty($scope.data.reports.metadata.reportPeriods, 'name');
            filter_set.pipeline = {};
            if(period in periods) {
                filter_set.pipeline.completed_at__gte = periods[period].start_date;
                filter_set.pipeline.completed_at__lte = periods[period].end_date;
            } else {
                var days_offset = dateSymbolToDays[period];
                if(days_offset !== null){
                    today = new Date();
                    prior_date = new Date(new Date().setDate(today.getDate()-days_offset));
                    filter_set.pipeline.completed_at__gte = prior_date.toISOString();
                    filter_set.pipeline.completed_at__lte = today.toISOString();
                }
            }
            return filter_set
        }

        function getFilters(searchFilters) {
            //returns a dict of form {'<resource>' : {'<resourceFilterPostfix>': '<resourceFilterValue>', ...}
            //for all of the set filters for reports
            period = searchFilters["date"][0].slice(1);
            name = searchFilters["report"][0].slice(1);
            filter_set = {};
            filter_set.pipeline = getDateFilter(period);
            filter_set.productundertest = getProductsFilter(name);
            if("environment" in searchFilters){
                filter_set['environment'] = {'name__in': searchFilters['environment']};
            }
            return filter_set;
        }

        function expandFilters(expansionTemplate, expandableFilters) {
            expanded = {};
            for(resource in expandableFilters) {
                for(postfix in expandableFilters[resource]) {
                    prefix = '';
                    if(resource in expansionTemplate) {
                        prefix = expansionTemplate[resource];
                    }
                    value = expandableFilters[resource][postfix];
                    expandedNameParts = [];
                    nameParts = prefix.split("|");
                    for (index in nameParts) {
                        expandedNameParts.push(nameParts[index] + postfix);
                    }
                    expanded[expandedNameParts.join("|")] = value;
                }
            }
            return expanded;
        }

        function ResourceFilterCall(resource, expansionTemplate, expandableFilters, extraFilters) {
            expandedFilters = expandFilters(expansionTemplate, expandableFilters);
            angular.extend(expandedFilters, extraFilters);
            return DataService.refresh(
                    resource, $scope.data.user, $scope.data.apikey).get(expandedFilters);
        }


        function getOverviewData() {
            $scope.data.plot_data_loading = true;
            $scope.data.reports.overview.reportPeriod = $scope.data.reports.search.filters["date"][0].slice(1);
            $scope.data.reports.overview.reportGroup = $scope.data.reports.search.filters["report"][0].slice(1);

            expandableFilters = getFilters($scope.data.reports.search.filters);
            console.log('expandableFilters');
            console.log(expandableFilters);
            get = {};
            everything = {};
            metaOnly = Common.metaWith({});

            //from period
            get.testcasesPeriod = ResourceFilterCall('testcaseinstance', expansionTemplates['testcaseinstance'], expandableFilters, metaOnly);
            get.pipelinesPeriod = ResourceFilterCall('pipeline', expansionTemplates['pipeline'], expandableFilters, metaOnly);
            get.versions = ResourceFilterCall('versionconfiguration', expansionTemplates['versionconfiguration'], expandableFilters, everything);

            //from all time
            delete expandableFilters['pipeline'];
            get.testcasesTotal = ResourceFilterCall('testcaseinstance', expansionTemplates['testcaseinstance'], expandableFilters, metaOnly);
            get.pipelinesTotal = ResourceFilterCall('pipeline', expansionTemplates['pipeline'], expandableFilters, metaOnly);
            get.hardwareProducts = ResourceFilterCall('productundertest', expansionTemplates['hardwareProducts'], expandableFilters, Common.metaWith({'machineconfigurations__isnull': 'False'}));
            get.hardwareVendors = ResourceFilterCall('vendor', expansionTemplates['vendor'], expandableFilters, Common.metaWith({'productundertests__machineconfigurations__isnull': 'False'}));
            get.servicesTested = ResourceFilterCall('jujuservice', expansionTemplates['jujuservice'], expandableFilters, {'jujuservicedeployments__productundertest__isnull': 'True'});
            get.testedSwift = ResourceFilterCall('jujuservice', expansionTemplates['jujuservice'], expandableFilters, Common.metaWith({'name__exact': 'swift'}));
            get.productTypes = ResourceFilterCall('producttype', expansionTemplates['producttype'], expandableFilters, everything);
            get.configs = ResourceFilterCall('configurationchoices', expansionTemplates['configurationchoices'], expandableFilters, Common.metaWith({'count_runs': 'True', 'exclude_versions': 'True'}));

            //get all products for the report directly, not the number of 'other' products in pipelines
            get.productsUnderTest = ResourceFilterCall('productundertest', expansionTemplates['productundertest'], expandableFilters, everything);
            waitForResolve(get, resolveOverviewData);
        }

        function resolveOverviewData(data) {
            console.log(data);
            $scope.data.reports.overview.productsUnderTest = getProperties(data.productsUnderTest.objects, "name").join(", ");
            $scope.data.reports.overview.servicesTested = getProperties(data.servicesTested.objects, "name").join(", ");
            $scope.data.reports.overview.testcasesTotal = data.testcasesTotal.meta.total_count;
            $scope.data.reports.overview.pipelinesTotal = data.pipelinesTotal.meta.total_count;
            $scope.data.reports.overview.testcasesPeriod = data.testcasesPeriod.meta.total_count;
            $scope.data.reports.overview.pipelinesPeriod = data.pipelinesPeriod.meta.total_count;
            $scope.data.reports.overview.hardwareProducts = data.hardwareProducts.meta.total_count;
            $scope.data.reports.overview.hardwareVendors = data.hardwareVendors.meta.total_count;
            $scope.data.reports.overview.cloudConfigs = data.configs.meta.total_count;
            versionCrossProduct = crossProduct(data.versions.objects);
            $scope.data.reports.overview.ubuntuCrossOpenstack = versionCrossProduct;
            $scope.data.reports.overview.productTypes = getProperties(data.productTypes.objects, "name");
            $scope.data.reports.overview.testedSwift = data.testedSwift.meta.total_count > 0;

            $scope.data.plot_data_loading = false;
        }

    }]);
