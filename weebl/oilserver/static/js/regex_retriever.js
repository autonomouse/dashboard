app.factory('UserService', function ($resource) {
    return $resource('/api/v1/build/?username=' + scope.user + '&api_key=' + scope.apikey, {name: "@name"});
});
