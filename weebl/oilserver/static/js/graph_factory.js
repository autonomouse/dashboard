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

    function updateChartData(number_of_test_runs, pass_deploy_count, total_deploy_count, pass_prepare_count, total_prepare_count, pass_test_cloud_image_count, total_test_cloud_image_count) {
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
                text: "Showing individual job percentage success rates.",
                css: {
                    width: "nullpx",
                    textAlign: "center"
                }
            }
        };
        scope.individual_stack_bar_options = individual_stack_bar_options;

        var cumulative_stack_bar_options = {
            chart: {
                type: 'discreteBarChart',
                height: 450,
                x: function(d){return d.label;},
                y: function(d){return d.value;},
                showValues: true,
                valueFormat: function(d){
                    return calcPercentage(d, number_of_test_runs) + "%"
                },
                transitionDuration: 500,
                xAxis: {
                    axisLabel: 'Job Name'
                },
                yAxis: {
                    axisLabel: 'Test Run Count',
                    tickFormat: function(d) {
                        return d3.format(',d')(d);
                    }
                },
                yDomain: [0, number_of_test_runs]
            },
            title: {
                enable: true,
                text: "Showing cumulative success rates of " + number_of_test_runs + " matching test runs.",
                css: {
                    width: "nullpx",
                    textAlign: "center"
                }
            }
        };
        scope.cumulative_stack_bar_options = cumulative_stack_bar_options;

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
        graphValues.test_cloud_image.jobtotal.meta.total_count
    )
  };

  return {
    plot_stats_graph: plot_stats_graph,
    calcPercentage: calcPercentage,
  };
}]);
