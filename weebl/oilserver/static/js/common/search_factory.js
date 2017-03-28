app.factory('SearchFactory', ['$location', 'Common', function($location, Common) {
    function Search() {
        // Holds an empty filter object.
        var emptyFilter = { _: [] };

        // Return a new empty filter;
        this.getEmptyFilter = function() {
            return angular.copy(emptyFilter);
        };

        // Would be private, but want to access via ng-model
        this.search = "";
        this.filters = this.getEmptyFilter();
        this.individualFilters = [];
        this.defaultFilters = {}
        this.runOnUpdate = angular.noop;
        this.isValid = true;

        this._setIndividual = function () {
            angular.forEach(this.individualFilters, function(key, idx) {
                values = this.filters[key];
                if(angular.isUndefined(values)) {
                    return;
                }
                if (values.length > 1) {
                    // use the last value as it was added most recently
                    this.filters[key] = [values[values.length - 1]];
                }
            }, this);
            this._filtersToString();
        };


        this._setURLParams = function (reset) {
            if (angular.isUndefined(reset))
                reset = false;
            if (reset)
                $location.search({});
            this.params = $location.search();
            angular.forEach(this.filters, function(value, key) {
                ignore = ["_"]
                if (ignore.indexOf(key) >= 0) {
                    // pass
                } else if (this.individualFilters.indexOf(key) >= 0) {
                    this.params[key] = this.filters[key][0].replace('=', '')
                } else {
                    values = [];
                    for (var idx in this.filters[key]) {
                        values.push(this.filters[key][idx].replace('=', ''));
                    };
                    if (values != '')
                        this.params[key] = values;
                };
            }, this);
            for (var key in this.params) {
                $location.search(key, this.params[key]);
            };
        }


        this._setDefaults = function () {
            angular.forEach(this.defaultFilters, function(value, key) {
                if(angular.isUndefined(this.filters[key])) {
                    //defaults are assumed to be exact for now
                    this.toggleFilter(key, value, true, false);
                }
            }, this);
        };

        this.update = function() {
            this._getCurrentFilters();
            if (this.isValid) {
                this._setIndividual();
                this._setURLParams();
                this._setDefaults();
                this.runOnUpdate();
            }
        };

        this._setFiltersFromURL = function () {
            this.filters = this.getEmptyFilter();
            angular.forEach($location.search(), function(value, key) {
                this.toggleFilter(key, value, true, false);
            }, this);
            this._filtersToString();
        };

        this.reset = function() {
            this.search = "";
            this.update();
            this._setURLParams(true);
        };

        var _countParens = function (input) {
            var count = 0;
            var start = 0;
            var max = input.length + 1;
            while(start < max) {
                nextOpen = input.indexOf('(', start);
                nextClose = input.indexOf(')', start);
                if(nextOpen === -1) nextOpen = max;
                if(nextClose === -1) nextClose = max;
                start = Math.min(nextOpen, nextClose);
                if(start != max) {
                    if(nextOpen === start) count++;
                    if(nextClose === start) count--;
                }
                start++;
            }
            return count;
        };
        // Splits the search string into different terms based on white space.
        // This handles the ability for whitespace to be inside of '(', ')'.
        // Can't do PDA matching with regex, dumped that logic to _countParens.
        this._getSplitSearch = function() {
            var terms = this.search.split(' ');
            var fixedTerms = [];
            var spanningParentheses = 0;
            angular.forEach(terms, function(term, idx) {
                if(spanningParentheses) {
                    // Previous term had an opening '(' but not a ')'. This
                    // term should join that previous term.
                    fixedTerms[fixedTerms.length - 1] += ' ' + term;
                    spanningParentheses += _countParens(term);
                } else {
                    // Term is not part of a previous '(' span.
                    fixedTerms.push(term);
                    spanningParentheses = _countParens(term);
                }
            });

            if(spanningParentheses) {
                // Missing ending parentheses so error with terms.
                return null;
            }
            return fixedTerms;
        };

        // Return all of the currently active filters for the given search.
        this._getCurrentFilters = function() {
            var filters = this.getEmptyFilter();
            if(this.search.length === 0) {
                this.isValid = true;
                this.filters = filters;
                return this.filters;
            }
            var searchTerms = this._getSplitSearch();
            if(!searchTerms) {
                this.isValid = false;
                return this.filters;
            }
            this.isValid = true;
            angular.forEach(searchTerms, function(terms) {
                terms = terms.split(':');
                if(terms.length === 1) {
                    // Search term is not specifing a specific field. Gets
                    // add to the '_' section of the filters.
                    if(filters._.indexOf(terms[0]) === -1) {
                        filters._.push(terms[0]);
                    }
                } else {
                    var field = terms.shift();
                    var values = terms.join(":");

                    // Remove the starting '(' and ending ')'.
                    values = values.replace('(', '');
                    values = values.replace(')', '');

                    // If empty values then do nothing.
                    if(values.length === 0) {
                        return;
                    }

                    // Split the values based on comma.
                    values = values.split(',');

                    // Add the values to filters.
                    if(angular.isUndefined(filters[field])) {
                        filters[field] = [];
                    }
                    angular.forEach(values, function(value) {
                        if(filters[field].indexOf(value) === -1) {
                            filters[field].push(value);
                        }
                    });
                }
            });
            this.filters = filters;
        };

        // Convert "filters" into a search string.
        this._filtersToString = function() {
            var search = "";
            angular.forEach(this.filters, function(terms, key) {
                // Skip empty and skip "_" as it gets appended at the
                // beginning of the search.
                if(terms.length === 0 || key === "_") {
                    return;
                }
                search += key + ":(" + terms.join(",") + ") ";
            });
            if(this.filters._.length > 0) {
                search = this.filters._.join(" ") + " " + search;
            }
            this.search = search.trim();
        };

        // Return the index of the value in the key for the filter.
        this._getFilterValueIndex = function(key, value) {
            var values = this.filters[key];
            if(angular.isUndefined(values)) {
                return -1;
            }
            var lowerValues = values.map(function(value) {
                return value.toLowerCase();
            });
            return lowerValues.indexOf(value.toLowerCase());
        };

        // Return true if the key and value are in the filters.
        this.isFilterActive = function(key, value, exact) {
            var values = this.filters[key];
            if(angular.isUndefined(values)) {
                return false;
            }
            if(angular.isUndefined(exact)) {
                exact = false;
            }
            if(exact) {
                if (Array.isArray(value)) {
                    for (var idx in value) {
                        value[idx] = "=" + value[idx];
                    }
                } else {
                    value = "=" + value;
                };
            }
            return this._getFilterValueIndex(key, value) !== -1;
        };

        // Toggles a filter on or off based on key and value.
        this.toggleFilter = function(key, value, exact, runUpdate) {
            if (Array.isArray(value)) {
                for (var idx in value) {
                    this.toggleIndividualFilter(key, value[idx], exact, runUpdate);
                }
            } else {
                this.toggleIndividualFilter(key, value, exact, runUpdate);
            };
        };

        // Toggles a filter on or off based on key and value.
        this.toggleIndividualFilter = function(key, value, exact, runUpdate) {
            console.log('toggling: ' + key + ' ' + value);
            angular.isUndefined(runUpdate) ? runUpdate=true : runUpdate=runUpdate;
            if(angular.isUndefined(this.filters[key])) {
                this.filters[key] = [];
            }
            if(exact) {
                if (Array.isArray(value)) {
                    for (var idx in value) {
                        value[idx] = "=" + value[idx];
                    }
                } else {
                    value = "=" + value;
                };
            }
            var idx = this._getFilterValueIndex(key, value);
            if(key in this.individualFilters) {
                if(idx === -1) {
                    this.filters[key] = [value];
                } else {
                    this.filters[key] = [];
                }
            }
            else {
                if(idx === -1) {
                    this.filters[key].push(value);
                } else {
                    this.filters[key].splice(idx, 1);
                }
            }
            this._filtersToString();
            if(runUpdate) {
                this.update();
            }
        };

        this.init = function(defaultFilters) {
            if (angular.isDefined(defaultFilters))
                this.defaultFilters = defaultFilters;
            this.search = "";
            this._setFiltersFromURL();
            this._setDefaults();
            this.runOnUpdate();
        };
    };
    return {
        Search: Search,
    }
}]);
