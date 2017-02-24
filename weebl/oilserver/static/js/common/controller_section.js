var app = angular.module('weebl');
app.controller('sectionController', ['$rootScope', '$scope', '$location', 'Common',
    function($rootScope, $scope, $location, common) {
        $scope.sections = [
            {'url': 'qa', 'name': 'Integrated QA',
                'tabs': [
                    {'url': 'overview', 'name': 'Overview'},
                ]
            },
            {'url': 'results', 'name': 'Results',
                'tabs': [
                    {'url': 'successRate', 'name': 'Success Rate'},
                    {'url': 'bugs', 'name': 'Bugs'},
                    {'url': 'testRuns', 'name': 'Test Runs'},
                ]
            },
            {'url': 'reports', 'name': 'OIL Reports',
                'tabs': [
                    {'url': 'overview', 'name': 'Overview'},
                    {'url': 'detailed', 'name': 'Detailed'},
                ]
            },
            {'url': 'throughput', 'name': 'Throughput',
                'tabs': [
                    {'url': 'scheduler', 'name': 'Scheduler'},
                ]
            },
        ];

        extraMappings = {
            'results/bug': 'results/bugs',
            'results/testRun': 'results/testRuns',
        };

        updateActive = function() {
            locationParts = $location.path().split('/');
            while (locationParts.indexOf('') !== -1) {
                locationParts.splice(locationParts.indexOf(''), 1);
            }
            if (locationParts.length < 2) {
                $scope.activeSection = '';
                $scope.activeTab = '';
                return;
            }
            cleanedLocation = locationParts[0] + '/' + locationParts[1];
            if (! angular.isUndefined(extraMappings[cleanedLocation])) {
                cleanedLocation = extraMappings[cleanedLocation];
            }
            $scope.activeSection = cleanedLocation.split('/')[0];
            $rootScope.activeSection = $scope.activeSection;
            $scope.tabs = common.arrayToObjectOnProperty($scope.sections, 'url')[$scope.activeSection].tabs;
            $scope.activeTab = cleanedLocation.split('/')[1];
            $rootScope.title = common.arrayToObjectOnProperty($scope.tabs, 'url')[$scope.activeTab].name;
        };

        $scope.$on("$locationChangeSuccess", function (event, newUrl, oldUrl) {
            updateActive();
        });

        if (angular.isUndefined($scope.activeSection)) {
            updateActive();
        }

        if (angular.isUndefined($scope.activeTab)) {
            updateActive();
        }

    }]);
