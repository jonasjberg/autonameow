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
source "$AUTONAMEOW_ROOT_DIR/tests/integration/utils.sh"



# Test Cases
# ____________________________________________________________________________

# Store current time for later calculation of total execution time.
time_start="$(current_unix_time)"

TESTSUITE_NAME='Stand-alone Extraction'
logmsg "Running the ${TESTSUITE_NAME} test suite .."



EXTRACT_RUNNER="${AUTONAMEOW_ROOT_DIR}/bin/extract.sh"
assert_bulk_test "$EXTRACT_RUNNER" n e f r x

assert_true '"$EXTRACT_RUNNER"' \
            'The autonameow launcher script can be started with no arguments'

assert_true '"$EXTRACT_RUNNER" 2>&1 | grep -- "--help"' \
            'Stand-alone extraction should print how to get help when started with no arguments'

assert_true '"$EXTRACT_RUNNER" --help -- 2>&1 | head -n 1 | grep -i -- "Usage"' \
            'Stand-alone extraction should display usage information when started with "--help"'

assert_true '"$EXTRACT_RUNNER"' \
            'Stand-alone extraction should return 0 when started without specifying files'

assert_true '"$EXTRACT_RUNNER" --verbose' \
            'Stand-alone extraction should return 0 when started with "--verbose" without specifying files'

assert_true '"$EXTRACT_RUNNER" --debug' \
            'Stand-alone extraction should return 0 when started with "--debug" without specifying files'

assert_false '"$EXTRACT_RUNNER" --verbose --debug' \
             'Mutually exclusive options "--verbose" and "--debug" should generate an error'

assert_false '"$EXTRACT_RUNNER" --verbose --quiet' \
             'Mutually exclusive options "--verbose" and "--quiet" should generate an error'

assert_false '"$EXTRACT_RUNNER" --debug --quiet' \
             'Mutually exclusive options "--debug" and "--quiet" should generate an error'


# ______________________________________________________________________________
#
# Check that the log format is not garbled due to multiple logger roots (?)

assert_false '"$EXTRACT_RUNNER" 2>&1 | grep -- " :root:"' \
             'Output should not contain " :root:"'

assert_false '"$EXTRACT_RUNNER" 2>&1 | grep -- ":root:"' \
             'Output should not contain ":root:"'

assert_false '"$EXTRACT_RUNNER" --verbose 2>&1 | grep -- " :root:"' \
             'Output should not contain " :root:" when starting with "--verbose"'

assert_false '"$EXTRACT_RUNNER" --verbose 2>&1 | grep -- ":root:"' \
             'Output should not contain ":root:" when starting with "--verbose"'

assert_false '"$EXTRACT_RUNNER" --debug 2>&1 | grep -- " :root:"' \
             'Output should not contain " :root:" when starting with "--debug"'

assert_false '"$EXTRACT_RUNNER" --debug 2>&1 | grep -- ":root:"' \
             'Output should not contain ":root:" when starting with "--debug"'



# Calculate total execution time.
time_end="$(current_unix_time)"
total_time="$(calculate_execution_time "$time_start" "$time_end")"

log_test_suite_results_summary "$TESTSUITE_NAME" "$total_time"
update_global_test_results
