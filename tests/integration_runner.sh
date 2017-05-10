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


# NOTE: Requires "aha" to be installed in order to convert the "raw"
#       (containing ANSI escape codes) log files to HTML.

set -o noclobber -o nounset -o pipefail

SELF="$(basename "$0")"
SELF_DIR="$(realpath -e "$(dirname "$0")")"

if ! source "${SELF_DIR}/integration_utils.sh"
then
    echo "Integration test utility library is missing. Aborting .." 1>&2
    exit 1
fi


# Store current time for later calculation of total execution time.
time_start="$(current_unix_time)"

initialize_logging
logmsg "Started integration test runner \"${SELF}\""
logmsg "Executing all files in \"${SELF_DIR}\" matching \"integration_test_*.sh\".."


find "$SELF_DIR" -mindepth 1 -maxdepth 1 -type f -name "integration_test_*.sh" \
| while IFS='\n' read -r testscript
do
    if [ ! -x "$testscript" ]
    then
        logmsg "Missing execute permission: \"${testscript}\" .. SKIPPING"
        continue
    fi

    "$testscript"
done


# Calculate total execution time.
time_end="$(current_unix_time)"
total_time="$((($time_end - $time_start) / 1000000))"
logmsg "Total execution time: ${total_time} ms"


# Convert the test log file to HTML using executable 'aha' if available.
if command -v "aha" >/dev/null 2>&1
then
    [ -z "${AUTONAMEOW_INTEGRATION_LOG:-}" ] && exit 1
    [ -f "$AUTONAMEOW_INTEGRATION_LOG" ] || exit 1

    _html_test_log="${AUTONAMEOW_INTEGRATION_LOG%.*}.html"
    _html_title="autonameow Integration Test Log ${AUTONAMEOW_TEST_TIMESTAMP}"

    if aha --title "$_html_title" \
        < "$AUTONAMEOW_INTEGRATION_LOG" | sed 's///g' > "$_html_test_log"
    then
        if [ -s "$_html_test_log" ]
        then
            logmsg "Wrote HTML log file: \"${_html_test_log}\""
            rm -- "$AUTONAMEOW_INTEGRATION_LOG"

            # Write log file name to temporary file, used by other scripts.
            set +o noclobber
            echo "${_html_test_log}" > "${AUTONAMEOW_TESTRESULTS_DIR}/.integrationlog.toreport"
            set -o noclobber
        fi
    else
        logmsg 'FAILED to write HTML log file!'
    fi
else
    logmsg "The executable \"aha\" is not available on this system"
    logmsg "Skipping converting raw logfiles to HTML .."
    exit 1
fi


