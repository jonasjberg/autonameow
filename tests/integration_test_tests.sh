#!/usr/bin/env bash

#   Copyright(c) 2016-2017 Jonas Sjöberg
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

SELF="$(basename "$0")"
SELF_DIR="$(dirname "$0")"

if ! source "${SELF_DIR}/integration_utils.sh"
then
    echo "Integration test utility library is missing. Aborting .." 1>&2
    exit 1
fi



# Test Cases
# ____________________________________________________________________________

# Store current time for later calculation of total execution time.
time_start="$(current_unix_time)"

logmsg "Started \"${SELF}\""
logmsg "Running the Test Suite test suite .."



assert_true  '[ "0" -eq "0" ]' 'Expect success .. (true positive)'
assert_true  '[ "1" -eq "0" ]' 'Expect failure .. (false negative)'
assert_false '[ "1" -eq "0" ]' 'Expect success .. (true positive)'
assert_false '[ "1" -ne "0" ]' 'Expect failure .. (false negative)'


assert_true '[ -e "${SELF_DIR}/integration_runner.sh" ]' \
            'The integration test runner exists'

assert_true '[ -x "${SELF_DIR}/integration_runner.sh" ]' \
            'The integration test runner is executable'

assert_true '[ -e "${SELF_DIR}/integration_test_cli.sh" ]' \
            "The Command-Line Interface test suite exists"

assert_true '[ -x "${SELF_DIR}/integration_test_cli.sh" ]' \
            'The Command-Line Interface test suite is executable'

assert_true '[ -e "${SELF_DIR}/integration_test_docs.sh" ]' \
            'The Documentation test suite exists'

assert_true '[ -x "${SELF_DIR}/integration_test_docs.sh" ]' \
            'The Documentation test suite is executable'

assert_true 'command -v "aha" >/dev/null 2>&1' \
            'The executable "aha" is available on the system'



# Calculate total execution time.
time_end="$(current_unix_time)"
total_time="$((($time_end - $time_start) / 1000000))"

calculate_statistics
logmsg "Completed the Test Suite test suite tests in ${total_time} ms"
