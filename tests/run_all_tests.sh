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


SELF="$(basename "$0")"
SELF_DIR="$(realpath -e "$(dirname "$0")")"

source "${SELF_DIR}/utils.sh"


# Store current time for later calculation of total execution time.
# Appending %N to date +%s gives us nanosecond accuracy.
time_start="$(current_unix_time)"

logmsg "Started \"${SELF}\""
logmsg "Executing all files in \"${SELF_DIR}\" matching \"test_*.sh\".."


find "$SELF_DIR" -mindepth 1 -maxdepth 1 -type f -name "test_*.sh" \
| while IFS='\n' read -r testscript
do
    if [ ! -x "$testscript" ]
    then
        logmsg "Missing execute permission: \"${testscript}\" .. SKIPPING"
        continue
    fi

    "$testscript"
done


time_end="$(current_unix_time)"
total_time="$((($time_end - $time_start) / 1000000))"
logmsg "Total execution time: ${total_time} ms"


if command -v "aha" >/dev/null 2>&1
then
    [ -z "${AUTONAMEOW_TEST_LOG:-}" ] && exit 1
    [ -f "$AUTONAMEOW_TEST_LOG" ] || exit 1

    _html_test_log="${AUTONAMEOW_TEST_LOG%.*}.html"

    if aha < "$AUTONAMEOW_TEST_LOG" | sed 's///g' > "$_html_test_log"
    then
        if [ -f "$_html_test_log" ]
        then
            logmsg "Wrote HTML log file: \"${_html_test_log}\""
            rm -- "$AUTONAMEOW_TEST_LOG"
        fi
    else
        logmsg 'FAILED to write HTML log file!'
    fi
else
    logmsg "The executable \"aha\" is not available on this system"
    logmsg "Skipping converting raw logfiles to HTML .."
    exit 1
fi


