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

SELF_BASENAME="$(basename "$0")"
SELF_DIRNAME="$(realpath -e "$(dirname "$0")")"

if ! source "${SELF_DIRNAME}/setup_environment.sh"
then
    cat >&2 <<EOF

[ERROR] Unable to source "${SELF_DIRNAME}/setup_environment.sh"
        Environment variable setup script is missing. Aborting ..

EOF
    exit 1
fi

if ! source "${AUTONAMEOW_ROOT_DIR}/tests/integration/utils.sh"
then
    cat >&2 <<EOF

[ERROR] Unable to source "${AUTONAMEOW_ROOT_DIR}/tests/integration/utils.sh"
        Integration test utility library is missing. Aborting ..

EOF
    exit 1
fi

# Default configuration.
option_write_report='false'
option_quiet='false'
optionarg_filter=''


print_usage_info()
{
    cat <<EOF

"${SELF_BASENAME}"  --  autonameow integration test suite runner

  USAGE:  ${SELF_BASENAME} ([OPTIONS])

  OPTIONS:  -f [EXP]   Execute scripts by filtering basenames.
                       Argument [EXP] is passed to grep as-is.
                       Scripts whose basename does not match the
                       expression are skipped.
            -h         Display usage information and exit.
            -q         Suppress output from test suites.
            -w         Write HTML test reports to disk.
                       Note: The "raw" log file is always written.

  All options are optional. Default behaviour is to export test result
  reports and print the test results to stdout/stderr in real-time.

EOF
}

# Set options to 'true' here and invert logic as necessary when testing (use
# "if not true"). Motivated by hopefully reducing bugs and weird behaviour
# caused by users setting the default option variables to unexpected values.
if [ "$#" -eq "0" ]
then
    printf '(USING DEFAULTS -- "%s -h" for usage information)\n\n' "${SELF_BASENAME}"
else
    while getopts f:hwq opt
    do
        case "$opt" in
            f) optionarg_filter="${OPTARG:-}"
               if [ -z "$optionarg_filter" ]
               then
                   printf '[ERROR] Expected non-empty argument for option "-f"\n' >&2
                   exit 1
               fi ;;
            h) print_usage_info ; exit 0 ;;
            w) option_write_report='true' ;;
            q) option_quiet='true' ;;
        esac
    done


    shift $(( OPTIND - 1 ))
fi


# Store current time for later calculation of total execution time.
time_start="$(current_unix_time)"

initialize_logging
initialize_global_stats
search_dir="${SELF_DIRNAME}/integration"
logmsg "Started integration test runner \"${SELF_BASENAME}\""
logmsg "Collecting files in \"${search_dir}\" matching \"test_*.sh\".."


find "$search_dir" -mindepth 1 -maxdepth 1 -type f -name "test_*.sh" \
| sort -r | while IFS=$'\n' read -r testscript
do
    if [ ! -x "$testscript" ]
    then
        logmsg "Missing execute permission: \"${testscript}\" .. SKIPPING"
        continue
    fi

    # Skip scripts not matching filtering expression, if any.
    _testscript_base="$(basename -- "$testscript")"
    if [ -n "$optionarg_filter" ]
    then
        if ! grep -q -- "$optionarg_filter" <<< "${_testscript_base}"
        then
            logmsg "Skipped \"${_testscript_base}\" (filter expression \"${optionarg_filter}\")"
            continue
        fi
    fi

    # !! # TODO: Fix all descendant processes not killed.
    # !! # Catch SIGUP (1) SIGINT (2) and SIGTERM (15)
    # !! trap kill_running_task SIGHUP SIGINT SIGTERM
    # !!
    # !! # Run task and check exit code.
    # !! if [ "$option_quiet" != 'true' ]
    # !! then
    # !!     eval "${testscript}" &
    # !!     TASK_PID="$!"
    # !! else
    # !!     eval "${testscript}" 2>&1 >/dev/null &
    # !!     TASK_PID="$!"
    # !! fi
    # !! wait "$TASK_PID"

    logmsg "Starting \"${_testscript_base}\" .."
    if [ "$option_quiet" != 'true' ]
    then
        source "${testscript}"
    else
        source "${testscript}" >/dev/null 2>&1
    fi
    logmsg "Finished \"${_testscript_base}\""
done


# Calculate total execution time.
time_end="$(current_unix_time)"
total_time="$(((time_end - time_start) / 1000000))"
logmsg "Total execution time: ${total_time} ms"


while read -r _count _pass _fail
do
    _total_count="$((_count + suite_tests_count))"
    _total_passed="$((_pass + suite_tests_passed))"
    _total_failed="$((_fail + suite_tests_failed))"
done < "$AUTONAMEOW_INTEGRATION_STATS"

log_total_results_summary "$total_time" "$_total_count" "$_total_passed" "$_total_failed"


# if [ ! "$option_write_report" != 'true' ]
# then
#     run_task "$option_quiet" 'Converting raw log to HTML' convert_raw_log_to_html
# fi

