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
SELF_DIR="$(realpath -e "$(dirname "$0")")"

# Source 'regression_utils.sh', which in turn sources 'common_utils.sh'.
if ! source "${SELF_DIR}/regression_utils.sh"
then
    echo "Regression test utility library is missing. Aborting .." 1>&2
    exit 1
fi


# Default configuration.
option_quiet='false'


print_usage_info()
{
    cat <<EOF

"${SELF}"  --  autonameow regression test runner

  USAGE:  ${SELF} ([OPTIONS])

  OPTIONS:  -h   Display usage information and exit.
            -q   Suppress output from test suites.

  All options are optional. Default behaviour is to
  print the test results to stdout/stderr in real-time.

EOF
}

# Set options to 'true' here and invert logic as necessary when testing (use
# "if not true"). Motivated by hopefully reducing bugs and weird behaviour
# caused by users setting the default option variables to unexpected values.
if [ "$#" -eq "0" ]
then
    printf "(USING DEFAULTS -- "${SELF} -h" for usage information)\n\n"
else
    while getopts hwq opt
    do
        case "$opt" in
            h) print_usage_info ; exit 0 ;;
            q) option_quiet='true' ;;
        esac
    done

    shift $(( $OPTIND - 1 ))
fi



count_fail=0

# Store current time for later calculation of total execution time.
time_start="$(current_unix_time)"

initialize_logging
logmsg "Started regression test runner \"${SELF}\""
logmsg "Executing regression tests in \"${AUTONAMEOW_REGRESSIONTESTS_DIR}\" .."

# Find directories in 'AUTONAMEOW_REGRESSIONTESTS_DIR', not including the
# search root or any contain sub-directories, whose names start with 4 digits.
find "$AUTONAMEOW_REGRESSIONTESTS_DIR" -mindepth 1 -maxdepth 1 -type d -regex '.*/[[:digit:]]\{4\}.*' \
| while IFS='\n' read -r regdir
do
    _regdir="$(realpath -- "$regdir")"
    if [ -z "$_regdir" ] || [ ! -d "$_regdir" ]
    then
        logmsg "Not a directory: \"${regdir}\" .. SKIPPING"
        continue
    fi

    echo "TODO: Run test \"${_regdir}\" .."
done



# Calculate total execution time.
time_end="$(current_unix_time)"
total_time="$((($time_end - $time_start) / 1000000))"
logmsg "Total execution time: ${total_time} ms"


