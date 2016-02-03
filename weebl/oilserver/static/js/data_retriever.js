app.factory('DataService', function ($resource, $http) {
    function refresh(object, user, apikey) {
        var url = "/api/v1/" + object + "/?username=" + user + "&api_key=" + apikey;
        return $resource(url + ":id", {id: '@id'}, {
            query: {
                method: 'GET',
                isArray: true,
                transformResponse: $http.defaults.transformResponse.concat([
                    function (data, headersGetter) {
                        return data.objects;
                    }
                ])
            },
        });
    }
    return {
      refresh: refresh
    };
});
