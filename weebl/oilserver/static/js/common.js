app.factory('Common', ['$rootScope', function($rootScope) {
    function humaniseDate(datestr) {
        var date_obj = new Date(datestr);
        var monthNames = ["Jan", "Feb", "Mar","Apr", "May", "Jun",
                          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
        var day = ('0' + date_obj.getUTCDate()).slice(-2);
        var month_name = monthNames[date_obj.getUTCMonth()];
        var year = ('0' + date_obj.getUTCFullYear()).slice(-2);
        var hours = ('0' + date_obj.getUTCHours()).slice(-2);
        var minutes = ('0' + date_obj.getUTCMinutes()).slice(-2);
        var seconds = ('0' + date_obj.getUTCSeconds()).slice(-2);
        return (day + "-" + month_name + "-" + year + " at " + hours + ":" + minutes + ":" + seconds);
    };
    function highlightTab(scope, tab) {
        $rootScope.title = scope.data.tabs[tab].pagetitle;
        scope.data.currentpage = tab;
    };
    return {
      humaniseDate: humaniseDate,
      highlightTab: highlightTab
    };
}]);
