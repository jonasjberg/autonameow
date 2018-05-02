#!/usr/bin/env bash

#   Copyright(c) 2016-2018 Jonas Sjöberg
#   Personal site:   http://www.jonasjberg.com
#   GitHub:          https://github.com/jonasjberg
#   University mail: js224eh[a]student.lnu.se
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

set -o noclobber -o nounset -o pipefail

if [ -z "${AUTONAMEOW_ROOT_DIR:-}" ]
then
    cat >&2 <<EOF

[ERROR] Integration test suites can no longer be run stand-alone.
        Please use use the designated integration test runner.

EOF
    exit 1
fi

# Resets test suite counter variables.
source "${AUTONAMEOW_ROOT_DIR}/tests/integration/utils.sh"



# Test Cases
# ____________________________________________________________________________

# Store current time for later calculation of total execution time.
time_start="$(current_unix_time)"

TESTSUITE_NAME='Regression Tests'
logmsg "Running the ${TESTSUITE_NAME} test suite .."



# ______________________________________________________________________________
#
# Check shared environment variables, used by all tests.

assert_false '[ -z "$AUTONAMEOW_ROOT_DIR" ]' \
             'Environment variable "AUTONAMEOW_ROOT_DIR" should not be unset'

assert_true '[ -d "$AUTONAMEOW_ROOT_DIR" ]' \
            'Environment variable "AUTONAMEOW_ROOT_DIR" should be a directory'

assert_true '[ -r "$AUTONAMEOW_ROOT_DIR" ]' \
            'Environment variable "AUTONAMEOW_ROOT_DIR" should be a existing readable path'


# ______________________________________________________________________________
#
# Smoke-test the regression runner.


_regression_runner_path="${AUTONAMEOW_ROOT_DIR}/tests/run_regression_tests.sh"
assert_bulk_test "$_regression_runner_path" n e r x

_regression_runner_basename="$(basename -- "$_regression_runner_path")"
assert_true '[ -n "$_regression_runner_basename" ]' \
            "Regression runner basename is captured by the integration test"

assert_true '"$_regression_runner_path" -h' \
            "Expect exit code 0 when running \"${_regression_runner_basename} -h\""

assert_true '"$_regression_runner_path" --help' \
            "Expect exit code 0 when running \"${_regression_runner_basename} --help\""


# ______________________________________________________________________________
#
# Check listing of regression test suites.

_regression_test_listing="$("$_regression_runner_path" --list)"
assert_true '[ -n "$_regression_test_listing" ]' \
            "Output of \"${_regression_runner_basename} --list\" is captured by the integration test"

_regression_test_listing_line_count="$(wc -l <<< "$_regression_test_listing")"
assert_true '[ "$_regression_test_listing_line_count" -gt "1" ]' \
            "Expect \"${_regression_runner_basename} --list\" to print at least 1 line"

assert_true '[ "$_regression_test_listing_line_count" -gt "10" ]' \
            "Expect \"${_regression_runner_basename} --list\" to print at least 10 lines"

assert_true '[ "$_regression_test_listing_line_count" -gt "20" ]' \
            "Expect \"${_regression_runner_basename} --list\" to print at least 20 lines"

assert_true '[ "$_regression_test_listing_line_count" -gt "30" ]' \
            "Expect \"${_regression_runner_basename} --list\" to print at least 30 lines"

assert_true 'grep -- 0000_unittest_dummy <<< "$_regression_test_listing"' \
            "Output of \"${_regression_runner_basename} --list\" should contain 0000_unittest_dummy"

assert_false '"$_regression_runner_path" -f "!0000_unittest_dummy" --list | grep -- 0000_unittest_dummy' \
             'Filtering with an inverted expression should not include tests matching that expression in the listing'

assert_false '"$_regression_runner_path" -f "!0000" --list | grep -- 0000_unittest_dummy' \
             'Filtering with an inverted expression should not include tests partially matching that expression in the listing'

assert_false '"$_regression_runner_path" -f "!*0000_unittest_dummy*" --list | grep -- 0000_unittest_dummy' \
             'Filtering with an inverted expression containing wildcards should not include tests matching that expression in the listing'

assert_false '"$_regression_runner_path" -f "!*0000*" --list | grep -- 0000_unittest_dummy' \
             'Filtering with an inverted expression containing wildcards should not include tests partially matching that expression in the listing'

assert_true 'grep -- 0001 <<< "$_regression_test_listing"' \
            "Output of \"${_regression_runner_basename} --list\" should contain 0001"

assert_true '"$_regression_runner_path" -f "!0000" --list | grep -- 0001' \
            'Filtering using a inverted match should pass through another arbitrary test to the output'

assert_true '[ "$("$_regression_runner_path" -f 0000_unittest_dummy -f 0000_unittest_dummy --list | wc -l)" -eq "1" ]' \
            'Filtering should not produce duplicate results in the listing when repeating the same filter expression'

assert_false '"$_regression_runner_path" -f 0000_unittest_dummy -f '!0000_unittest_dummy' --list | grep -- 0000_unittest_dummy' \
             'Filtering is ANDed, tests matched by previous filter is removed by the same inverted expression, and not included in the listing'




# Calculate total execution time.
time_end="$(current_unix_time)"
total_time="$(calculate_execution_time "$time_start" "$time_end")"

log_test_suite_results_summary "$TESTSUITE_NAME" "$total_time"
update_global_test_results
