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

if ! source "${SELF_DIR}/common_utils.sh"
then
    echo "Shared test utility library is missing. Aborting .." 1>&2
    exit 1
fi


# Root path used in the links that are added to the report.
REMOTE_TEST_RESULTS="https://github.com/1dv430/js224eh-project/blob/master/docs/test_results"

# Path to the local wiki page to which links are added.
WIKI_REPORT_RESULTS="${AUTONAMEOW_WIKI_ROOT_DIR}/Test-Results.md"

# Default configuration.
option_skip_report='false'
option_verbose='false'


print_usage_info()
{
    cat <<EOF

"${SELF}"  --  autonameow test suite helper script

  USAGE:  ${SELF} ([OPTIONS])"

  OPTIONS:  -h   Display usage information and exit.
            -n   Do not add test reports to project wiki.
            -v   Enable all output from the unit/integration-runners.
                 This also increases the verbosity of this script.

  All options are optional. Default behaviour is to add test reports to
  the project wiki and suppress output from the unit/integration-runners.

EOF
}

# Prints a message describing a task that is about to start.
# Message formatting depends on the option 'option_verbose'.
msg_task_start()
{
    local FMT
    [ "$option_verbose" != 'true' ] && FMT='%s ..' || FMT='%s ..\n'
    printf "$FMT" "$*"
}

# Prints a message when a task has ended.
# First argument is the exit status of the task. Non-zero is considered a
# failure. Any arguments following the first is a message describing the task.
# Message formatting depends on the option 'option_verbose'.
msg_task_end()
{
    local _status="$1"
    shift
    local _msg="$*"

    [ "$option_verbose" != 'true' ] || printf "\n${_msg} .."
    if [ "$_status" -eq '0' ]
    then
        printf " ${C_GREEN}[FINISHED]${C_RESET}\n"
    else
        printf " ${C_RED}[FAILED]${C_RESET}\n"
    fi
}

# Runs a "task" and prints a message,
# First argument is a message to print before running the task.
# Second argument is an arbitrary expression to evalute.
# If the expression evaluates to 0 the task is considered to have succeeded,
# any other return code is considered a failure. Suppresses the eval output
# based on the 'option_verbose' option.
run_task()
{
    local _msg="$1"
    msg_task_start "$_msg"

    if [ "$option_verbose" != 'true' ]
    then
        eval "$2" 2>&1 >/dev/null
    else
        eval "$2"
    fi

    local _retcode="$?"
    if [ "$_retcode" -ne '0' ]
    then
        count_fail="$((count_fail + 1))"
    fi

    msg_task_end "$_retcode" "$_msg"
}

# Append arguments to the wiki project report and print to stdout.
wiki_report_append()
{
    printf "Appending to report:\n"
    printf "$*" | tee -a "$WIKI_REPORT_RESULTS"
}

# Add a header with todays date to the project wiki if not already present.
wiki_check_add_header()
{
    # Insert heading with todays date if not already present.
    local _date="$(date "+%Y-%m-%d")"
    if ! grep -q "^### ${_date}$" "$WIKI_REPORT_RESULTS"
    then
        wiki_report_append "\n### ${_date}\n\n"
    fi
}

# Add link to the newest integration test report to the project wiki.
wiki_add_integration_link()
{
    [ ! -f "${AUTONAMEOW_TESTRESULTS_DIR}/.integrationlog.toreport" ] && return 1

    # Read file contents; the path to the most recent integration test log.
    _int_log_path="$( < "${AUTONAMEOW_TESTRESULTS_DIR}/.integrationlog.toreport" )"
    [ ! -f "$_int_log_path" ] && return 1

    _int_log_basename="$(basename -- "${_int_log_path}")"
    _int_log_timestamp="$(get_timestamp_from_basename "${_int_log_basename}")"
    _int_log_link="${REMOTE_TEST_RESULTS}/${_int_log_basename}"
    wiki_report_append "* \`${_int_log_timestamp}\` [Integration Test Report](${_int_log_link})\n"

    rm -v -- "${AUTONAMEOW_TESTRESULTS_DIR}/.integrationlog.toreport"
    return 0
}

# Add link to the newest unit test report to the project wiki.
wiki_add_unit_link()
{
    [ ! -f "${AUTONAMEOW_TESTRESULTS_DIR}/.unittestlog.toreport" ] && return 1

    # Read file contents; the path to the most recent unit test log.
    _unit_log_path="$( < "${AUTONAMEOW_TESTRESULTS_DIR}/.unittestlog.toreport" )"
    [ ! -f "$_unit_log_path" ] && return 1

    _unit_log_basename="$(basename -- "${_unit_log_path}")"
    _unit_log_timestamp="$(get_timestamp_from_basename "${_unit_log_basename}")"
    _unit_log_link="${REMOTE_TEST_RESULTS}/${_unit_log_basename}"
    wiki_report_append "* \`${_unit_log_timestamp}\` [Unit Test Report](${_unit_log_link})\n"

    rm -v -- "${AUTONAMEOW_TESTRESULTS_DIR}/.unittestlog.toreport"
    return 0
}



# Set options to 'true' here and invert logic as necessary when testing (use
# "if not true"). Motivated by hopefully reducing bugs and weird behaviour
# caused by users setting the default option variables to unexpected values.
if [ "$#" -eq "0" ]
then
    printf "(USING DEFAULTS -- "${SELF} -h" for usage information)\n\n"
else
    while getopts hnv opt
    do
        case "$opt" in
            h) print_usage_info ; exit 0 ;;
            n) option_skip_report='true' ;;
            v) option_verbose='true' ;;
        esac
    done

    shift $(( $OPTIND - 1 ))
fi


count_fail=0

run_task 'Running integration test runner' ${SELF_DIR}/integration_runner.sh
run_task 'Running unit test runner' ${SELF_DIR}/unit_runner.sh

# Do not proceed if a runner failed.
if [ "$count_fail" -ne "0" ]
then
    printf '\nAn error occurred; Aborting ..\n' 1>&2
    exit 1
fi


if [ "$option_skip_report" != 'true' ]
then
    run_task 'Adding heading with current date to report if needed' wiki_check_add_header
    run_task 'Adding integration test log to Test Results wiki page' wiki_add_integration_link
    run_task 'Adding unit test log to Test Results wiki page' wiki_add_unit_link

    # TODO: Commit reports to version control.
fi

printf "\nCompleted in $SECONDS seconds\n"
