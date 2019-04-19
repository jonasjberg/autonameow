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

TESTSUITE_NAME='Integration Test Utilities'
aw_utils.log_msg "Running the ${TESTSUITE_NAME} test suite .."



# ______________________________________________________________________________
#
# Test shared test functionality in 'common_utils.sh'.

_integration_utils_path="${AUTONAMEOW_ROOT_DIR}/tests/integration/utils.sh"
assert_bulk_test "$_integration_utils_path" e r x

source "$_integration_utils_path"

assert_true 'type -t command_exists' \
            '"command_exists" is defined after sourcing the common integration test utilities'

assert_true 'type -t assert_bash_function' \
            '"assert_bash_function" is defined after sourcing the common integration test utilities'


# ______________________________________________________________________________
#
# Test function 'assert_bash_function()'

__func_always_true() { true ; }
assert_bash_function '__func_always_true'

__func_always_false() { false ; }
assert_bash_function '__func_always_false'


# ______________________________________________________________________________
#
# Test function 'command_exists()'

assert_true 'command_exists cd' \
            'Expect command_exists to return success when given "cd"'

assert_false 'command_exists this_is_not_a_command_surely' \
             'Expect command_exists to return failure when given "this_is_not_a_command_surely"'


# ______________________________________________________________________________
#
# Test function 'assert_has_command()'

assert_has_command 'cd'




# Calculate total execution time.
time_end="$(current_unix_time)"
total_time="$(calculate_execution_time "$time_start" "$time_end")"

log_test_suite_results_summary "$TESTSUITE_NAME" "$total_time"
update_global_test_results
