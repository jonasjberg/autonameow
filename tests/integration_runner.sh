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

# Default configuration.
option_skip_report='false'
option_quiet='false'


print_usage_info()
{
    cat <<EOF

"${SELF}"  --  autonameow integration test suite runner

  USAGE:  ${SELF} ([OPTIONS])

  OPTIONS:  -h   Display usage information and exit.
            -n   Do not write HTML test reports to disk.
                 Note: "raw" log file is always written.
            -q   Suppress output from test suites.

  All options are optional. Default behaviour is to export test result
  reports and print the test results to stdout/stderr in real-time.

EOF
}

# Set options to 'true' here and invert logic as necessary when testing (use
# "if not true"). Motivated by hopefully reducing bugs and weird behaviour
# caused by users setting the default option variables to unexpected values.
if [ "$#" -eq "0" ]
then
    printf "(USING DEFAULTS -- "${SELF} -h" for usage information)\n\n"
else
    while getopts hnq opt
    do
        case "$opt" in
            h) print_usage_info ; exit 0 ;;
            n) option_skip_report='true' ;;
            q) option_quiet='true' ;;
        esac
    done

    shift $(( $OPTIND - 1 ))
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

convert_raw_log_to_html

