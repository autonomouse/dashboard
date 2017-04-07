var app = angular.module('weebl', ['nvd3', 'ngResource', 'ngRoute']);

app.directive('onErrorSrc', function() {
    return {
        link: function(scope, element, attrs) {
            element.bind('error', function() {
            if (attrs.src != attrs.onErrorSrc) {
                attrs.$set('src', attrs.onErrorSrc);
            }
            });
        }
    }
});
