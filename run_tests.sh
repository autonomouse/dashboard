#!/bin/bash -e
PROJECTS="weebl"

for project in $PROJECTS; do
    echo "Testing $project"
    if echo "$@" | grep -q "lint" ; then
      echo "Running flake8 lint tests..."
      flake8 --exclude ${project}/tests/,${project}/oilserver/migrations/,${project}/weebl/wsgi.py ${project} --ignore=F403
      echo "OK"
    fi

    if echo "$@" | grep -q "unit" ; then
      echo "Running unit tests..."
      /usr/bin/nosetests -v --nologcapture --with-coverage ${project}/
    fi
done
