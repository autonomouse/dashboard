var app = angular.module('weebl');

app.filter('keylength', function(){
    return function(input){
        if(!angular.isObject(input)){
            throw Error("Usage of non-objects with keylength filter!!")
        }
        return Object.keys(input).length;
    }
});
app.filter('namedKey', function () {
    return function (obj, keyname) {
        if (!(angular.isObject(obj))) {
            return obj;
        }

        keyname = keyname || '$key';
        return Object.keys(angular.copy(obj)).map(function (key) {
            if (obj.hasOwnProperty('$$hashKey')) {
                Object.defineProperty(obj, '$$hashKey', {enumerable: false});
            }
            return Object.defineProperty(obj[key], keyname, { enumerable: false, value: key});
        });
    };
});

app.controller('detailedReportController', [
    '$scope', '$rootScope', '$q', '$sce', 'SearchFactory', 'DataService', 'Common', 'graphFactory', 'keylengthFilter', 'namedKeyFilter',
    function($scope, $rootScope, $q, $sce, SearchFactory, DataService, Common, graphFactory, keylengthFilter, namedKeyFilter) {
        $scope = Common.initialise($scope);
        if(angular.isUndefined($scope.data.reports.search)) $scope.data.reports.search = new SearchFactory.Search();
        $scope.data.reports.search.initialPageLoad();
        if(angular.isUndefined($scope.data.reports.metadata)) $scope.data.reports.metadata = {};
        if(angular.isUndefined($scope.data.reports.detailed)) $scope.data.reports.detailed = {};
        $rootScope.data.show_reports_filters = true;
        $rootScope.data.show_filters = false;
        $rootScope.data.show_search = false;

        $scope.data.reports.search.defaultFilters = {"date": "Last 30 Days", "report": "Overall"};
        $scope.data.reports.search.individualFilters = ["date", "report"];
        $scope.data.reports.search.runOnUpdate = getDetailedData;
        getMetadata();

        var dateSymbolToDays = {
            'Last 24 Hours': 1,
            'Last 7 Days': 7,
            'Last 30 Days': 30,
            'Last Year': 365,
            'All Time': null
        };

        var colors = graphFactory.reportColors;
        var to_fraction = graphFactory.to_fraction;

        var previouslyMunged = {};

        $scope.data.reports.search.update();

        function getMetadata() {
            if ('reportPeriods' in $scope.data.reports.metadata){
                return;
            }
            $scope.data.reports.metadata.reportPeriods = DataService.refresh(
                    'reportperiod', $scope.data.user, $scope.data.apikey).query({});
            $scope.data.reports.metadata.environments = DataService.refresh(
                    'environment', $scope.data.user, $scope.data.apikey).query({});
            $scope.data.reports.metadata.reportGroups = DataService.refresh(
                    'report', $scope.data.user, $scope.data.apikey).query({});
        }

        function renameValues(object, renameMap) {
            /* extract only given items and rename them */
            var values = [];
            var keys = Object.keys(object);
            var renames = Object.keys(renameMap);
            for (keyIndex in keys) {
                var key = keys[keyIndex];
                if (key.startsWith('$')) continue; // ignore special keys
                var renamed = {};
                for (renameIndex in renames) {
                    var from = renames[renameIndex];
                    var to = renameMap[from];
                    renamed[to] = object[key][from];
                }
                values.push(renamed);
            }
            return values;
        }

        function waitForResolve(promisedResources, callback) {
            var resourceKeys = Object.keys(promisedResources);
            var resources = resourceKeys.map(function(key) {return promisedResources[key];});
            var promises = Common.getProperties(resources, '$promise');
            $q.all(promises).then(function(data) {
                resolved = {};
                for (i = 0; i < data.length; i++){
                    resolved[resourceKeys[i]] = data[i];
                }
                callback(resolved);
            });
        }

        function getReportFilter(name) {
            var filter_set = {};
            var reports = Common.arrayToObjectOnProperty($scope.data.reports.metadata.reportGroups, 'name');
            $scope.data.reports.detailed.forceReportChoice = false;
            if(!(name in reports)) {
                $scope.data.reports.detailed.forceReportChoice = true;
                return;
            } else {
                filter_set.reportname__exact = name;
            }
            return filter_set;
        }

        function getDateFilter(period) {
            var filter_set = {};
            var periods = Common.arrayToObjectOnProperty($scope.data.reports.metadata.reportPeriods, 'name');
            if(period in periods) {
                filter_set.date__gte = periods[period].start_date;
                filter_set.date__lt = periods[period].end_date;
            } else {
                var days_offset = dateSymbolToDays[period];
                if(days_offset !== null){
                    var today = new Date();
                    var prior_date = new Date(new Date().setDate(today.getDate()-days_offset));
                    filter_set.date__gte = prior_date.toISOString();
                    filter_set.date__lt = today.toISOString();
                }
            }
            return filter_set;
        }

        function getFilters(searchFilters) {
            var period = searchFilters["date"][0].slice(1);
            var date_filters = getDateFilter(period);
            var reportname = searchFilters["report"][0].slice(1);
            var report_filters = getReportFilter(reportname);
            if($scope.data.reports.detailed.forceReportChoice) {
                return;
            }
            var filter_set = angular.extend({}, date_filters, report_filters);

            if("environment" in searchFilters){
                filter_set.environmentname__in = searchFilters['environment'];
            }
            return filter_set;
        }

        function getHistoricalPeriods(searchFilters, historyLength) {
            if (angular.isUndefined(historyLength)) historyLength = 12;
            var period = searchFilters["date"][0].slice(1);
            var periods = renameValues($scope.data.reports.metadata.reportPeriods,
                    {start_date: 'start', end_date: 'end', name: 'name'});
            if (periods.length < 1) {
                return [];
            }
            periods = periods.sort(function(a, b) {
                //sort based on start date
                //['January', 'February', 'March', ..., Today]
                if (a.start < b.start) return -1;
                if (a.start > b.start) return 1;
                return 0;
            });
            var periodNames = Common.getProperties(periods, 'name');
            var selectedPeriodIndex = periodNames.indexOf(period) + 1;
            if (selectedPeriodIndex == 0) selectedPeriodIndex = period.length;
            var pastPeriods = periods.slice(Math.max(selectedPeriodIndex - historyLength, 0),
                                        selectedPeriodIndex);
            return pastPeriods;
        }

        function getHistoricalFilters(searchFilters) {
            var filters = getFilters(searchFilters);
            var historicalPeriods = getHistoricalPeriods(searchFilters);
            if (angular.isUndefined(filters) || historicalPeriods.length == 0) return null;
            $scope.data.reports.detailed.historicalPeriods = historicalPeriods;

            filters.date__gte = historicalPeriods[0].start;
            filters.date__lt = historicalPeriods[historicalPeriods.length - 1].end;
            return filters;
        }

        function historicalBinify(input) {
            bins = [];
            var historicalPeriods = $scope.data.reports.detailed.historicalPeriods;
            for (var historicalPeriodIndex in historicalPeriods) {
                var historicalPeriod = historicalPeriods[historicalPeriodIndex];
                if (historicalPeriod.start <= input && historicalPeriod.end > input) {
                    bins.push(historicalPeriod.name);
                }
            }
            return bins;
        }

        function testcaseSum(aggregate, input) {
            var output = aggregate;
            var testclassNames = Object.keys(input);
            for (var testclassNameIndex in testclassNames) {
                var testclassName = testclassNames[testclassNameIndex];
                var testclass = input[testclassName];
                var testNames = Object.keys(testclass);
                for (var testNameIndex in testNames) {
                    var testName = testNames[testNameIndex];
                    var fullTestName = testclassName + '.' + testName;
                    if (!(fullTestName in output)) {
                        output[fullTestName] = testclass[testName];
                    }
                    else {
                        var valueKeys = Object.keys(testclass[testName]);
                        for (var valueKeyIndex in valueKeys) {
                            var valueKey = valueKeys[valueKeyIndex];
                            if (!isNaN(output[fullTestName][valueKey])) {
                                output[fullTestName][valueKey] += testclass[testName][valueKey];
                            }
                        }
                    }
                }
            }
            return output;
        }

        function testcaseCategorize(input) {
            var output = {count: 0, failed: 0, skipped: 0, passed: 0, total: 0};
            keys = Object.keys(input);
            for (var keyIndex in keys) {
                var key = keys[keyIndex];
                if (!(key.endsWith('.setUpClass') || key.endsWith('.tearDownClass'))) {
                    output.count++;
                }
                output.failed += input[key].numfailed;
                output.skipped += input[key].numskipped;
                output.passed += input[key].numsuccess;
                output.total = output.failed + output.skipped + output.passed;
            }
            return output;
        }

        function sumBins(input, binningFunction, sumFunction) {
            var output = {};
            var inputKeys = Object.keys(input);
            for (var inputKeyIndex in inputKeys) {
                var key = inputKeys[inputKeyIndex];
                var bins = binningFunction(key);
                for (var binIndex in bins) {
                    var bin = bins[binIndex];
                    if (!(bin in output)) {
                        output[bin] = input[key];
                        if (angular.isDefined(sumFunction)) {
                            output[bin] = sumFunction({}, input[key]);
                        }
                    }
                    else {
                        if (angular.isDefined(sumFunction)) {
                            output[bin] = sumFunction(output[bin], input[key]);
                        }
                        else {
                            var valueKeys = Object.keys(input[key]);
                            for (var valueKeyIndex in valueKeys) {
                                var valueKey = valueKeys[valueKeyIndex];
                                if (!isNaN(input[key][valueKey])) {
                                    output[bin][valueKey] += input[key][valueKey];
                                }
                            }
                        }
                    }
                }
            }
            return output;
        }

        function ResourceFilterCall(resource, filters) {
            return DataService.refresh(
                    resource, $scope.data.user, $scope.data.apikey).get(filters);
        }

        function returnEnd(data, layout, lookup, position) {
            if(position >= layout.length) {
                return data;
            }
            attribute = layout[position];
            value = lookup[attribute];
            if(!(value in data)) {
                data[value] = {};
            }
            return returnEnd(data[value], layout, lookup, position+1);
        }

        function sumOver(data, layout, sumAttributes, passthrough) {
            angular.isUndefined(passthrough) ? passthrough=[] : passthrough=passthrough;

            output = {};
            for(dataIndex in data) {
                item = data[dataIndex];
                store = returnEnd(output, layout, item, 0);
                for(attributeIndex in sumAttributes) {
                    attribute = sumAttributes[attributeIndex];
                    if(!(attribute in store)) {
                        store[attribute] = 0;
                    }
                    store[attribute] += item[attribute];
                }
                for(passthroughIndex in passthrough) {
                    passthroughAttribute = passthrough[passthroughIndex];
                    if(item[passthroughAttribute]) {
                        store[passthroughAttribute] = item[passthroughAttribute];
                    }
                }
            }
            return output;
        }

        function getDetailedData() {
            $scope.data.reports.detailed.reportPeriod = $scope.data.reports.search.filters["date"][0].slice(1);
            $scope.data.reports.detailed.reportGroup = $scope.data.reports.search.filters["report"][0].slice(1);
            var filters = getFilters($scope.data.reports.search.filters);
            var historicalFilters = getHistoricalFilters($scope.data.reports.search.filters);
            if($scope.data.reports.detailed.forceReportChoice) {
                return;
            }
            console.log('filters: ' + JSON.stringify(filters));
            var get = {};
            var bad_tests = {'groupname__isnull': false}

            $scope.data.plot_data_loading = true;
            get.vendorExplanation = ResourceFilterCall('reportinstance',
                    {'report__name': $scope.data.reports.detailed.reportGroup,
                     'reportperiod__name': $scope.data.reports.detailed.reportPeriod,
                     'limit': 1});
            get.monthlyExplanation = ResourceFilterCall('reportperiod',
                    {'name': $scope.data.reports.detailed.reportPeriod,
                     'limit': 1});
            get.services = ResourceFilterCall('servicereportview', filters);
            get.bugs = ResourceFilterCall('bugreportview', filters);
            get.pipelines = ResourceFilterCall('pipelinereportview', filters);
            get.testcases = ResourceFilterCall('testreportview', angular.extend({}, filters, bad_tests));
            if (historicalFilters != null) {
                get.historicalPipelines = ResourceFilterCall('pipelinereportview', historicalFilters);
                get.historicalTestcases = ResourceFilterCall('testreportview', angular.extend({}, historicalFilters, bad_tests));
            }
            waitForResolve(get, resolvedetailedData);
        }

        function resolvedetailedData(data) {
            console.log(data);

            $scope.data.reports.detailed.vendorExplanation = '';
            if (data.vendorExplanation.meta.total_count > 0) {
                $scope.data.reports.detailed.vendorExplanation = $sce.trustAsHtml(data.vendorExplanation.objects[0].specific_summary);
            }
            $scope.data.reports.detailed.monthlyExplanation = '';
            if (data.monthlyExplanation.meta.total_count > 0) {
                $scope.data.reports.detailed.monthlyExplanation = $sce.trustAsHtml(data.monthlyExplanation.objects[0].overall_summary);
            }

            var sumAttributes = ['numpipelines', 'numsuccess'];
            var layout = ['producttypename'];
            var passthrough = ['producttypename'];
            var serviceDeploymentGraph = sumOver(data.services.objects, layout, sumAttributes, passthrough);
            var pipelines = renameValues(serviceDeploymentGraph,
                                  {producttypename: 'x', numpipelines: 'y'});
            var success = renameValues(serviceDeploymentGraph,
                                {producttypename: 'x', numsuccess: 'y'});
            var fails = [];
            for (serviceIndex in pipelines) {
                fail = {x: pipelines[serviceIndex].x,
                        y: pipelines[serviceIndex].y - success[serviceIndex].y}
                fails.push(fail);
            }
            $scope.data.reports.detailed.serviceDeploymentGraph = [
                {key: 'passed', color: colors.pass, values: success},
                {key: 'failed', color: colors.fail, values: fails},
            ];

            layout = ['producttypename', 'productundertestname'];
            $scope.data.reports.detailed.serviceDeploymentBreakdown = sumOver(data.services.objects, layout, sumAttributes);

            sumAttributes = ['numpipelines', 'numdeployfail', 'numtestfail', 'numpreparefail'];
            $scope.data.reports.detailed.deploymentHistoryGraph = sumOver(data.pipelines.objects, [], sumAttributes);

            layout = ['groupname', 'bug'];
            $scope.data.reports.detailed.bugInfo = sumOver(data.bugs.objects, layout, ['occurrences']);

            layout = ['groupname', 'subgroupname', 'testcaseclassname', 'testcasename'];
            sumAttributes = ['numtestcases', 'numsuccess', 'numskipped', 'numfailed'];
            passthrough = ['testcaseclassname', 'bug'];
            $scope.data.reports.detailed.testcaseInfo = sumOver(data.testcases.objects, layout, sumAttributes, passthrough);

            layout = ['groupname', 'openstackversionname', 'ubuntuversionname', 'subgroupname'];
            sumAttributes = ['numtestcases', 'numsuccess', 'numskipped', 'numfailed'];
            $scope.data.reports.detailed.subgroupTable = sumOver(data.testcases.objects, layout, sumAttributes, passthrough);

            layout = ['openstackversionname', 'ubuntuversionname', 'groupname'];
            sumAttributes = ['numtestcases', 'numsuccess', 'numskipped', 'numfailed'];
            $scope.data.reports.detailed.groupTable = sumOver(data.testcases.objects, layout, sumAttributes, passthrough);

            if ('historicalPipelines' in data && 'historicalTestcases' in data) {
                //make historical graphs
                layout = ['date'];
                sumAttributes = ['numpipelines', 'numdeployfail', 'numtestfail', 'numpreparefail'];
                var historicalPipelines = sumBins(sumOver(data.historicalPipelines.objects, layout, sumAttributes), historicalBinify);
                var historicalPipelinesGraph = [];
                for (var historicalIndex in $scope.data.reports.detailed.historicalPeriods) {
                    var period = $scope.data.reports.detailed.historicalPeriods[historicalIndex].name;
                    if (angular.isUndefined(historicalPipelines[period])) {
                        historicalPipelines[period] = {'numpipelines': 0, 'numdeployfail': 0, 'numtestfail': 0, 'numpreparefail': 0};
                    }
                    historicalPipelines[period].x = period + ' (' + historicalPipelines[period].numpipelines + ')';
                    var totalFail = historicalPipelines[period].numdeployfail + historicalPipelines[period].numtestfail + historicalPipelines[period].numpreparefail;
                    historicalPipelines[period].numpassed = historicalPipelines[period].numpipelines - totalFail;
                    historicalPipelinesGraph.push(historicalPipelines[period]);
                }
                $scope.data.reports.detailed.historicalPipelinesGraph = [
                    {key: 'Testing Completed', color: colors.tested, values: historicalPipelinesGraph.map(
                        function(val) {return {x: val.x, y: to_fraction(val.numpassed, val.numpipelines)};})},
                    {key: 'Unable to power on hardware and deploy OpenStack initially', color: colors.deployFail,
                     values: historicalPipelinesGraph.map(
                        function(val) {return {x: val.x, y: to_fraction(val.numdeployfail, val.numpipelines)};})},
                    {key: 'Unable to install images and set up network', color: colors.prepareFail,
                     values: historicalPipelinesGraph.map(
                        function(val) {return {x: val.x, y: to_fraction(val.numpreparefail, val.numpipelines)};})},
                    {key: 'Unable to start testing', color: colors.testFail,
                     values: historicalPipelinesGraph.map(
                        function(val) {return {x: val.x, y: to_fraction(val.numtestfail, val.numpipelines)};})},
                ];


                layout = ['date', 'testcaseclassname', 'testcasename'];
                sumAttributes = ['numsuccess', 'numskipped', 'numfailed'];
                // need to get # of testcases that are failed/skipped/passed
                historicalTestcases = sumBins(sumOver(data.historicalTestcases.objects, layout, sumAttributes), historicalBinify, testcaseSum);
                var historicalTestcasesGraph = [];
                for (var historicalIndex in $scope.data.reports.detailed.historicalPeriods) {
                    var period = $scope.data.reports.detailed.historicalPeriods[historicalIndex].name;
                    if (angular.isDefined(historicalTestcases[period])) {
                        historicalTestcases[period] = testcaseCategorize(historicalTestcases[period]);
                        historicalTestcases[period].x = period + ' (' + historicalTestcases[period].count + ')';
                        historicalTestcasesGraph.push(historicalTestcases[period]);
                    } else {
                        var empty = {total: 0, passed: 0, skipped: 0, failed: 0, x: period + ' (0)'};
                        historicalTestcasesGraph.push(empty);
                    }
                }
                testcaseCategorize(historicalTestcases)
                $scope.data.reports.detailed.historicalTestcasesGraph = [
                    {key: 'Passed', color: colors.pass, values: historicalTestcasesGraph.map(
                        function(val) {return {x: val.x, y: to_fraction(val.passed, val.total)};})},
                    {key: 'Skipped', color: colors.skip,
                     values: historicalTestcasesGraph.map(
                        function(val) {return {x: val.x, y: to_fraction(val.skipped, val.total)};})},
                    {key: 'Failed', color: colors.fail,
                     values: historicalTestcasesGraph.map(
                        function(val) {return {x: val.x, y: to_fraction(val.failed, val.total)};})},
                ];
            }

            previouslyMunged = {};
            console.log($scope.data.reports.detailed);
            $scope.data.plot_data_loading = false;
        }

        $scope.data.reports.detailed.serviceBarChart = graphFactory.extendBarChart(
            {'yAxis': {'ticks': 4, 'tickFormat': function(d) {return d3.format(",.2r")(d);} }});
        $scope.data.reports.detailed.historicalBarChart = graphFactory.extendBarChart(
            {'showLegend': true});

        $scope.data.reports.detailed.servicePieChart = graphFactory.extendPieChart(
            {'showLegend': true, 'height': 200, 'width': 450,
             'margin': {'top': 0, 'bottom': 0, 'left': -20, 'right': 0}});
        $scope.data.reports.detailed.testcasePieChart = graphFactory.extendPieChart(
            {'color': [colors.pass, colors.skip, colors.fail], 'width': 100, 'height': 100,
             'margin': {'top': -10, 'bottom': 0, 'left': -10, 'right': 0}});

        $scope.data.reports.detailed.mungeTestcasePie = function(input) {
            jsonKey = JSON.stringify(input);
            if(jsonKey in previouslyMunged){
                return previouslyMunged[jsonKey];
            }

            var munged = [];
            for (var keyindex in Object.keys(input)) {
                key = Object.keys(input)[keyindex];
                if(!isNaN(input[key]) && key != 'numtestcases') {
                    munged.push({'key': key.replace('num', ''), 'value': input[key]});
                }
            }
            if (munged.length > 0) {
                previouslyMunged[jsonKey] = munged;
            }
            return munged;
        };

        $scope.data.reports.detailed.mungeServicePie = function(input) {
            var jsonKey = JSON.stringify(input);
            if(jsonKey in previouslyMunged){
                return previouslyMunged[jsonKey];
            }
            var munged = [];
            for (var keyindex in Object.keys(input)) {
                key = Object.keys(input)[keyindex];
                munged.push({
                    'key': key + ' (' + Math.round(100 * input[key].numsuccess/input[key].numpipelines) + '% success)',
                    'value': input[key].numpipelines
                });
            }
            if(munged.length > 0){
                previouslyMunged[jsonKey] = munged;
            }
            return munged;
        };

        $scope.removeBrackets = function(testcasename) {
            if (angular.isUndefined(testcasename)) {
                return testcasename;
            }
            return testcasename.replace(/\[.*\]/, '').replace(/test/, '').replace(/_/g, ' ');
        }

    }]);
