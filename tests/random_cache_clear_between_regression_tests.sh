#!/usr/bin/env bash

set -o noclobber -o nounset -o pipefail


cd ~/dev/projects/autonameow.git || exit 1

while true
do
    # Randomly delete cached Python bytecode before running.
    [ "$(( $RANDOM % 2 ))" -eq "0" ] && { printf '\n\n===========================\nDeleting cached bytecode ..\n\n' ; devscripts/delete-python-caches.sh --force ; }

    tests/run_regression_tests.sh || break

    sleep 3
done
