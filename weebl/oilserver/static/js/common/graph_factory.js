app.factory('graphFactory', ['Common', function(Common) {

var calcPercentage = function calcPercentage(value, total, number_of_tests_skipped) {
    var d3formatting = ',.2f';
    if (angular.isUndefined(number_of_tests_skipped))  number_of_tests_skipped = 0;
    total = total - number_of_tests_skipped;
    var percentage = d3.format(d3formatting)(((value / total) * 100))
    if (percentage == "NaN"){
        return d3.format(d3formatting)(0);
    } else {
        return percentage;
    }
};

var plot_stats_graph = function(scope, graphValues, jobDetails) {

    function updateChartData(graphValues, stack_bar_data) {
        var stack_bar_config = {
            visible: true,
            extended: false,
            disabled: false,
            autorefresh: true,
            refreshDataOnly: false,
            debounce: 10
        };
        scope.stack_bar_config = stack_bar_config;

        var total_count = angular.isDefined(graphValues.total.meta) ? graphValues.total.meta.total_count: "";
        var pipeline_total_count = angular.isDefined(graphValues.pipeline_total.meta) ? graphValues.pipeline_total.meta.total_count: "";
        var individual_stack_bar_options = {
            chart: {
                type: 'discreteBarChart',
                height: 450,
                x: function(d){return d.label;},
                y: function(d){return d.individualPercentage;},
                showValues: true,
                valueFormat: function(d){return d + "%";},
                transitionDuration: 500,
                xAxis: {
                    axisLabel: 'Job Name'
                },
                yAxis: {
                    axisLabel: 'Percentage Success Rate',
                    tickFormat: function(d) {
                        return d3.format(',d')(d);
                    }
                },
                yDomain: [0, 100]
            },
            title: {
                enable: true,
                text: "Percentage Success Rates for " + total_count + " Matching Tests in " + pipeline_total_count + " Test Runs",
                css: {
                    textAlign: "center"
                }
            }
        };
        scope.individual_stack_bar_options = individual_stack_bar_options;
        scope.stack_bar_data = stack_bar_data;
    };

    var vals = new Array(Object.keys(jobDetails).length);
    angular.forEach(jobDetails, function(job_info){
        job = job_info.name;
        if (angular.isDefined(graphValues[job]) &&
            angular.isDefined(graphValues[job].pass.meta) &&
            angular.isDefined(graphValues[job].jobtotal.meta) &&
            angular.isDefined(graphValues[job].skip.meta)) {
                vals.push({
                    "label" : jobDetails[job].description,
                    "value" : graphValues[job].pass.meta.total_count,
                    "individualPercentage" : calcPercentage(
                        graphValues[job].pass.meta.total_count,
                        graphValues[job].jobtotal.meta.total_count,
                        graphValues[job].skip.meta.total_count),
                    "color" : '#' + jobDetails[job].colour
                });
        };
    });
    var stack_bar_data = [{
        key: "Test Run Success",
        values: vals.filter(function(n){ return n != undefined })
    }];

    updateChartData(graphValues, stack_bar_data);

};

var plotBugHistoryGraph = function(scope, graphValues) {
    function updateBugChartData(title, subtitle, bugnumber, description, values, maxNum, minDate) {
        var LineChart_config = {
            visible: true,
            extended: false,
            disabled: false,
            autorefresh: true,
            refreshDataOnly: false,
            debounce: 10
        };
        scope.LineChart_config = LineChart_config;

        var LineChart_options = {
            chart: {
                type: 'lineChart',
                height: 450,
                margin : {
                    top: 20,
                    right: 20,
                    bottom: 40,
                    left: 55
                },
                x: function(d){ return new Date(d.date).getTime(); },
                y: function(d){ return d.count; },
                useInteractiveGuideline: true,
                dispatch: {
                    stateChange: function(e){ console.log("stateChange"); },
                    changeState: function(e){ console.log("changeState"); },
                    tooltipShow: function(e){ console.log("tooltipShow"); },
                    tooltipHide: function(e){ console.log("tooltipHide"); }
                },
                xAxis: {
                    axisLabel: 'Date',
                    tickFormat: function(d) {
                        return d3.time.format('%d-%B-%y')(new Date(d))
                    },
                    showMaxMin: false,
                    staggerLabels: false
                },
                yAxis: {
                    axisLabel: 'Number of Occurrences',
                    axisLabelDistance: -10
                },
                xDomain: [minDate, new Date().getTime()],
                yDomain: [0, maxNum],
                callback: function(chart){
                    console.log("Plotting " + title);
                }
            },
            title: {
                enable: true,
                text: title,
                css: {
                    'font-weight': 'bold'
                }
            },
            subtitle: {
                enable: true,
                text: subtitle,
                css: {
                    'text-align': 'center',
                    'margin': '10px 13px 0px 7px',
                    'font-size': '75%'
                }
            }
        };
        scope.LineChart_options = LineChart_options;

        var LineChart_data = [
            {
                key: "Bug #" + bugnumber,
                values: values,
                area: true,
                color: "#411934"
            }
        ];
        scope.LineChart_data = LineChart_data;
    };

    updateBugChartData(
        graphValues.title,
        graphValues.subtitle,
        graphValues.bugnumber,
        graphValues.description,
        graphValues.data,
        graphValues.maxNum + 5,
        graphValues.minDate
    )
};

var plot_solutions_graph = function(scope, graphValues) {

    function updateSolutionsChartData(graphValues) {
        var qa_stack_bar_config = {
            visible: true,
            extended: false,
            disabled: false,
            autorefresh: true,
            refreshDataOnly: false,
            debounce: 10
        };
        scope.qa_stack_bar_config = qa_stack_bar_config;

        var qa_stack_bar_options = {
            chart: {
                type: 'discreteBarChart',
                height: 450,
                x: function(d){return d.label;},
                y: function(d){return d.value;},
                showValues: true,
                valueFormat: function(d){return d + "%";},
                transitionDuration: 500,
                xAxis: {
                    axisLabel: 'Solution'
                },
                yAxis: {
                    axisLabel: 'Percentage Confidence',
                    tickFormat: function(d) {
                        return d3.format(',d')(d);
                    }
                },
                yDomain: [0, 100]
            },
            title: {
                enable: true,
                text: "Percentage Confidence For Each Solution",
                css: {
                    width: "nullpx",
                    textAlign: "center"
                }
            }
        };
        scope.qa_stack_bar_options = qa_stack_bar_options;
        graphValues.qa_stack_bar_data[0].values = Common.orderArray(graphValues.qa_stack_bar_data[0].values, 'label', null);                        
        scope.qa_stack_bar_data = graphValues.qa_stack_bar_data;
    };
    updateSolutionsChartData(graphValues);
    scope.qa_stack_bar_data
  };

  return {
    plot_stats_graph: plot_stats_graph,
    plotBugHistoryGraph: plotBugHistoryGraph,
    calcPercentage: calcPercentage,
    plot_solutions_graph: plot_solutions_graph
  };
}]);
