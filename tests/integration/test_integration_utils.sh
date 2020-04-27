#!/usr/bin/env bash

#   Copyright(c) 2016-2020 Jonas Sjöberg <autonameow@jonasjberg.com>
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

if [ -z "${AUTONAMEOW_ROOT_DIRPATH:-}" ]
then
    cat >&2 <<EOF

[ERROR] Integration test suites can no longer be run stand-alone.
        Please use use the designated integration test runner.

EOF
    exit 1
fi

# Resets test suite counter variables.
# shellcheck source=tests/integration/utils.sh
source "${AUTONAMEOW_ROOT_DIRPATH}/tests/integration/utils.sh"



# Test Cases
# ____________________________________________________________________________

# Store current time for later calculation of total execution time.
time_start="$(aw_utils.current_unix_time)"

TESTSUITE_NAME='Integration Test Utilities'
aw_utils.log_msg "Running the $TESTSUITE_NAME test suite .."



# ______________________________________________________________________________
#
# Test shared test functionality in 'common_utils.sh'.

_integration_utils_path="${AUTONAMEOW_ROOT_DIRPATH}/tests/integration/utils.sh"
assert_bulk_test "$_integration_utils_path" e r x

aw_utils.assert_true 'type -t aw_utils.command_exists' \
            '"aw_utils.command_exists" is defined after sourcing the common integration test utilities'


# ______________________________________________________________________________
#
# Test function 'aw_utils.command_exists()'

aw_utils.assert_true 'aw_utils.command_exists cd' \
            'Expect aw_utils.command_exists to return success when given "cd"'

aw_utils.assert_false 'aw_utils.command_exists this_is_not_a_command_surely' \
             'Expect aw_utils.command_exists to return failure when given "this_is_not_a_command_surely"'


# ______________________________________________________________________________
#
# Test function 'aw_utils.assert_has_command()'

aw_utils.assert_has_command 'cd'




# Calculate total execution time.
time_end="$(aw_utils.current_unix_time)"
total_time="$(aw_utils.calculate_execution_time "$time_start" "$time_end")"

aw_utils.log_test_suite_results_summary "$TESTSUITE_NAME" "$total_time"
aw_utils.update_global_test_results
