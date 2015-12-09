app.factory('DataService', function ($resource, $http) {
    function refresh(object, user, apikey) {
        var url = "/api/v1/" + object + "/?username=" + user + "&api_key=" + apikey;
        return $resource(url, {}, {
            query: {
                method: 'GET',
                isArray: true,
                transformResponse: $http.defaults.transformResponse.concat([
                    function (data, headersGetter) {
                        return data.objects;
                    }
                ])
            },
            query_metadata: {
                method: 'GET',
                transformResponse: $http.defaults.transformResponse.concat([
                    function (data, headersGetter) {
                        return data.meta;
                    }
                ])
            },
        });
    }
    return {
      refresh: refresh
    };
});
