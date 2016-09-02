app.factory('graphFactory', ['DataService', function(DataService) {

var calcPercentage = function calcPercentage(value, number_of_test_runs) {
      var percentage = d3.format(',.2f')(((value / number_of_test_runs) * 100))
      if (percentage == "NaN"){
          return "0";
      } else {
          return percentage;
    }
  };

var plot_stats_graph = function(scope, graphValues) {

    function updateChartData(number_of_test_runs, pass_deploy_count, total_deploy_count, pass_prepare_count, total_prepare_count,
                             pass_test_cloud_image_count, total_test_cloud_image_count, pass_test_bundletests_count, total_test_bundletests_count) {
        var stack_bar_config = {
            visible: true,
            extended: false,
            disabled: false,
            autorefresh: true,
            refreshDataOnly: false,
            debounce: 10
        };
        scope.stack_bar_config = stack_bar_config;

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
                text: "Percentage Success Rates",
                css: {
                    width: "nullpx",
                    textAlign: "center"
                }
            }
        };
        scope.individual_stack_bar_options = individual_stack_bar_options;

        var stack_bar_data = [
            {
                key: "Test Run Success",
                values: [
                    {
                        "label" : "Deploy Openstack" ,
                        "value" : pass_deploy_count,
                        "individualPercentage" : calcPercentage(pass_deploy_count, total_deploy_count),
                        "color" : "#77216F"
                    } ,
                    {
                        "label" : "Configure Openstack for test" ,
                        "value" : pass_prepare_count,
                        "individualPercentage" : calcPercentage(pass_prepare_count, total_prepare_count),
                        "color" : "#6E3C61"
                    } ,
                    {
                        "label" : "SSH to guest instance",
                        "value" : pass_test_cloud_image_count,
                        "individualPercentage" : calcPercentage(pass_test_cloud_image_count, total_test_cloud_image_count),
                        "color" : "#411934"
                    },
                    {
                        "label" : "Tempest tests",
                        "value" : pass_test_bundletests_count,
                        "individualPercentage" : calcPercentage(pass_test_bundletests_count, total_test_bundletests_count),
                        "color" : "#314984"
                    }
                ]
            }
        ]
        scope.stack_bar_data = stack_bar_data;
    };

    updateChartData(
        graphValues.total.meta.total_count,
        graphValues.deploy.pass.meta.total_count,
        graphValues.deploy.jobtotal.meta.total_count,
        graphValues.prepare.pass.meta.total_count,
        graphValues.prepare.jobtotal.meta.total_count,
        graphValues.test_cloud_image.pass.meta.total_count,
        graphValues.test_cloud_image.jobtotal.meta.total_count,
        graphValues.test_bundletests.pass.meta.total_count,
        graphValues.test_bundletests.jobtotal.meta.total_count
    )
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
            },
            caption: {
                enable: false,
                html: "",
                css: {
                    'text-align': 'justify',
                    'margin': '10px 13px 0px 7px'
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


  return {
    plot_stats_graph: plot_stats_graph,
    plotBugHistoryGraph: plotBugHistoryGraph,
    calcPercentage: calcPercentage,
  };
}]);
