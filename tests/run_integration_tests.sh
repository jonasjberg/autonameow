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


declare -r EXIT_SUCCESS=0
declare -r EXIT_FAILURE=1
declare -r EXIT_CRITICAL=2

SELF_BASENAME="$(basename -- "$0")"
SELF_DIRPATH="$(realpath -e -- "$(dirname -- "$0")")"

if ! source "${SELF_DIRPATH}/setup_environment.sh"
then
    cat >&2 <<EOF

[ERROR] Unable to source "${SELF_DIRPATH}/setup_environment.sh"
        Environment variable setup script is missing. Aborting ..

EOF
    exit "$EXIT_CRITICAL"
fi

if ! source "${AUTONAMEOW_ROOT_DIR}/tests/integration/utils.sh"
then
    cat >&2 <<EOF

[ERROR] Unable to source "${AUTONAMEOW_ROOT_DIR}/tests/integration/utils.sh"
        Integration test utility library is missing. Aborting ..

EOF
    exit "$EXIT_CRITICAL"
fi

# Default configuration.
option_quiet=false
optionarg_filter=''


print_usage_info()
{
    cat <<EOF

"${SELF_BASENAME}"  --  autonameow integration test suite runner

  USAGE:  ${SELF_BASENAME} ([OPTIONS])

  OPTIONS:     -f [EXP]   Execute scripts by filtering basenames.
                          Argument [EXP] is passed to grep as-is.
                          Scripts whose basename does not match the
                          expression are skipped.
               -h         Display usage information and exit.
               -q         Suppress output from test suites.

  All options are optional. Default behaviour is to print the test
  results to stdout/stderr in real-time.
  Note: The "raw" log file is always written.

  EXIT CODES:   ${EXIT_SUCCESS}         All tests/assertions passed.
                ${EXIT_FAILURE}         Any tests/assertions FAILED.
                ${EXIT_CRITICAL}         Runner itself failed or aborted.

  Project website: www.github.com/jonasjberg/autonameow

EOF
}


if [ "$#" -eq "0" ]
then
    printf '(USING DEFAULTS -- "%s -h" for usage information)\n\n' "${SELF_BASENAME}"
else
    while getopts f:hq opt
    do
        case "$opt" in
            f) optionarg_filter="${OPTARG:-}"
               if [ -z "$optionarg_filter" ]
               then
                   printf '[ERROR] Expected non-empty argument for option "-f"\n' >&2
                   exit "$EXIT_CRITICAL"
               fi ;;
            h) print_usage_info ; exit "$EXIT_SUCCESS" ;;
            q) option_quiet=true ;;
        esac
    done

    shift $(( OPTIND - 1 ))
fi


# Store current time for later calculation of total execution time.
time_start="$(current_unix_time)"

aw_utils.initialize_logging
initialize_global_stats
search_dir="${SELF_DIRPATH}/integration"
log_msg_timestamped "Started integration test runner \"${SELF_BASENAME}\""
aw_utils.log_msg "Collecting files in \"${search_dir}\" matching \"test_*.sh\".."


find "$search_dir" -maxdepth 1 -type f -name "test_*.sh" | sort -r |
while IFS=$'\n' read -r testscript
do
    if [ ! -x "$testscript" ]
    then
        aw_utils.log_msg "Missing execute permission: \"${testscript}\" .. SKIPPING"
        continue
    fi

    # Skip scripts not matching filtering expression, if any.
    _testscript_base="$(basename -- "$testscript")"
    if [ -n "$optionarg_filter" ]
    then
        if ! grep -q -- "$optionarg_filter" <<< "${_testscript_base}"
        then
            aw_utils.log_msg "Skipped \"${_testscript_base}\" (filter expression \"${optionarg_filter}\")"
            continue
        fi
    fi

    # !! # TODO: Fix all descendant processes not killed.
    # !! # Catch SIGUP (1) SIGINT (2) and SIGTERM (15)
    # !! trap kill_running_task SIGHUP SIGINT SIGTERM
    # !!
    # !! # Run task and check exit code.
    # !! if $option_quiet
    # !! then
    # !!     eval "${testscript}" 2>&1 >/dev/null &
    # !!     TASK_PID="$!"
    # !! else
    # !!     eval "${testscript}" &
    # !!     TASK_PID="$!"
    # !! fi
    # !! wait "$TASK_PID"

    aw_utils.log_msg_timestamped "Starting \"${_testscript_base}\" .."
    if $option_quiet
    then
        source "${testscript}" &>/dev/null
    else
        source "${testscript}"
    fi
    aw_utils.log_msg_timestamped "Finished \"${_testscript_base}\""
done


# Calculate total execution time.
time_end="$(current_unix_time)"
total_time="$(((time_end - time_start) / 1000000))"
aw_utils.log_msg "Total execution time: ${total_time} ms"


while read -r _count _pass _fail
do
    _total_count="$_count"
    _total_passed="$_pass"
    _total_failed="$_fail"
done < "$AUTONAMEOW_INTEGRATION_STATS"

log_total_results_summary "$total_time" "$_total_count" "$_total_passed" "$_total_failed"
log_msg_timestamped "Exiting integration test runner \"${SELF_BASENAME}\""

if [ "$_total_failed" -eq "0" ]
then
    exit "$EXIT_SUCCESS"
else
    exit "$EXIT_FAILURE"
fi

