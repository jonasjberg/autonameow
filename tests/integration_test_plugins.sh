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
TESTSUITE_NAME='Plugins'

# Source 'integration_utils.sh', which in turn sources 'common_utils.sh'.
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
logmsg "Running the "$TESTSUITE_NAME" test suite .."



assert_true 'command -v guessit' \
            "guessit is available on the system"

assert_true 'guessit -h ; [ "$?" -eq "0" ]' \
            'Executing "guessit -h" returns success'



# Calculate total execution time.
time_end="$(current_unix_time)"
total_time="$(calculate_execution_time "$time_start" "$time_end")"

log_test_suite_results_summary "$TESTSUITE_NAME" "$total_time"
