#!/usr/bin/env bash

#   Copyright(c) 2016-2018 Jonas Sjöberg <autonameow@jonasjberg.com>
#   Source repository: https://github.com/jonasjberg/autonameow
#
#   This file is part of autonameow.
#
#   autonameow is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation.
#
#   autonameow is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with autonameow.  If not, see <http://www.gnu.org/licenses/>.

set -o pipefail -o errexit

ITERATIONS=10


run_local_regression_tests_get_runtime()
{
    tests/run_regression_tests.sh -f '!*LOCAL*' \
        | grep 'Regression Test Summary' | grep -o '  in .* seconds$' \
        | cut -f4 -d' '
}


total=0
for ((n=1; n<=$ITERATIONS; n++))
do
    runtime="$(run_local_regression_tests_get_runtime)"
    [ -z "$runtime" ] && exit 1

    printf 'Iteration %s/%s runtime :: %s\n' "$n" "$ITERATIONS" "$runtime"
    total="$(echo $runtime + $total | bc)"
done

average="$(echo "scale=6; $total/$ITERATIONS" | bc)"
printf '\nAVERAGE RUNTIME :: %s\n' "$average"
