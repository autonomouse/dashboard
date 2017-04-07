var app = angular.module('weebl');

app.filter('showTagFilter', function() {
    return function(obj) {
        filtered_obj = {}
        for (var item in obj) {
            if ((angular.isDefined(obj[item])) && (angular.isDefined(obj[item].show)) && (obj[item].show))
                filtered_obj[item] = obj[item];
        };
        return filtered_obj;
    };
});
