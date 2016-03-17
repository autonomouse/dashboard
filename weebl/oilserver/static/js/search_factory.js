app.factory('SearchFactory', [function() {
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

        this.updateSearch = function() {
            this.getCurrentFilters();
        }
        this.setFilters = function(filters) {
            this.filters = filters;
            this.filtersToString();
        }
        // Splits the search string into different terms based on white space.
        // This handles the ability for whitespace to be inside of '(', ')'.
        //
        // XXX blake_r 28-01-15: This could be improved with a regex, but was
        // unable to come up with one that would allow me to validate the end
        // ')' in the string.
        this.getSplitSearch = function() {
            var terms = this.search.split(' ');
            var fixedTerms = [];
            var spanningParentheses = false;
            angular.forEach(terms, function(term, idx) {
                if(spanningParentheses) {
                    // Previous term had an opening '(' but not a ')'. This
                    // term should join that previous term.
                    fixedTerms[fixedTerms.length - 1] += ' ' + term;

                    // If the term contains the ending ')' then its the last
                    // in the group.
                    if(term.indexOf(')') !== -1) {
                        spanningParentheses = false;
                    }
                } else {
                    // Term is not part of a previous '(' span.
                    fixedTerms.push(term);

                    var startIdx = term.indexOf('(');
                    if(startIdx !== -1) {
                        if(term.indexOf(')', startIdx) === -1) {
                            // Contains a starting '(' but not a ending ')'.
                            spanningParentheses = true;
                        }
                    }
                }
            });

            if(spanningParentheses) {
                // Missing ending parentheses so error with terms.
                return null;
            }
            return fixedTerms;
        };

        // Return all of the currently active filters for the given search.
        this.getCurrentFilters = function() {
            var filters = this.getEmptyFilter();
            if(this.search.length === 0) {
                return filters;
            }
            var searchTerms = this.getSplitSearch();
            if(!searchTerms) {
                return null;
            }
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
            return filters;
        };

        // Convert "filters" into a search string.
        this.filtersToString = function() {
            var search = "";
            angular.forEach(this.filters, function(terms, type) {
                // Skip empty and skip "_" as it gets appended at the
                // beginning of the search.
                if(terms.length === 0 || type === "_") {
                    return;
                }
                search += type + ":(" + terms.join(",") + ") ";
            });
            if(this.filters._.length > 0) {
                search = this.filters._.join(" ") + " " + search;
            }
            this.search = search.trim();
            return this.search;
        };

        // Return the index of the value in the type for the filter.
        this._getFilterValueIndex = function(type, value) {
            var values = this.filters[type];
            if(angular.isUndefined(values)) {
                return -1;
            }
            var lowerValues = values.map(function(value) {
                return value.toLowerCase();
            });
            return lowerValues.indexOf(value.toLowerCase());
        };

        // Return true if the type and value are in the filters.
        this.isFilterActive = function(type, value, exact) {
            var values = this.filters[type];
            if(angular.isUndefined(values)) {
                return false;
            }
            if(angular.isUndefined(exact)) {
                exact = false;
            }
            if(exact) {
                value = "=" + value;
            }
            return this._getFilterValueIndex(type, value) !== -1;
        };

        // Toggles a filter on or off based on type and value.
        this.toggleFilter = function(type, value, exact) {
            console.log('toggling: ' + type + ' ' + value);
            if(angular.isUndefined(this.filters[type])) {
                this.filters[type] = [];
            }
            if(exact) {
                value = "=" + value;
            }
            var idx = this._getFilterValueIndex(type, value);
            if(idx === -1) {
                this.filters[type].push(value);
            } else {
                this.filters[type].splice(idx, 1);
            }
            return this.filters;
        };
    };
    return {
        Search: Search,
    }
}]);
