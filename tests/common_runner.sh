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

if ! source "${AUTONAMEOW_ROOT_DIR}/tests/common_utils.sh"
then
    cat >&2 <<EOF

[ERROR] Unable to source "${AUTONAMEOW_ROOT_DIR}/tests/common_utils.sh"
        Shared test utility library is missing. Aborting ..

EOF
fi


# Root path used in the links that are added to the report.
REMOTE_TEST_RESULTS="https://github.com/1dv430/js224eh-project/blob/master/docs/test_results"

# Path to the local wiki page to which links are added.
WIKI_REPORT_RESULTS="${AUTONAMEOW_WIKI_ROOT_DIR}/Test-Results.md"

# Default configuration.
option_write_reports='false'
option_update_wiki='false'
option_verbose='false'


print_usage_info()
{
    cat <<EOF

"${SELF_BASENAME}"  --  autonameow test suite helper script

  USAGE:  ${SELF_BASENAME} ([OPTIONS])

  OPTIONS:  -h   Display usage information and exit.
            -u   Add test reports to the project wiki.
            -v   Enable all output from the unit/integration-runners.
                 This also increases the verbosity of this script.
            -w   Write result reports in HTML and PDF format.

  All options are optional. Default behaviour is to suppress output from
  the unit/integration/regression-runners and not write logs to disk.

EOF
}


# Append arguments to the wiki project report and print to stdout.
wiki_report_append()
{
    printf '%s\n' 'Appending to report:'
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
    _int_log_link_html="${REMOTE_TEST_RESULTS}/${_int_log_basename}"
    _int_log_link_pdf="${_int_log_link_html/.html/.pdf}"
    wiki_report_append "* \`${_int_log_timestamp}\` Integration Test Report ([pdf](${_int_log_link_pdf}), [html](${_int_log_link_html}))\n"

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
    _unit_log_link_html="${REMOTE_TEST_RESULTS}/${_unit_log_basename}"
    _unit_log_link_pdf="${_unit_log_link_html/.html/.pdf}"
    wiki_report_append "* \`${_unit_log_timestamp}\` Unit Test Report ([pdf](${_unit_log_link_pdf}), [html](${_unit_log_link_html}))\n"

    rm -v -- "${AUTONAMEOW_TESTRESULTS_DIR}/.unittestlog.toreport"
    return 0
}



# Set options to 'true' here and invert logic as necessary when testing (use
# "if not true"). Motivated by hopefully reducing bugs and weird behaviour
# caused by users setting the default option variables to unexpected values.
if [ "$#" -eq "0" ]
then
    printf '(USING DEFAULTS -- "%s -h" for usage information)\n\n' "$SELF_BASENAME"
else
    while getopts huvw opt
    do
        case "$opt" in
            h) print_usage_info ; exit 0 ;;
            u) option_update_wiki='true' ;;
            v) option_verbose='true' ;;
            w) option_write_reports='true' ;;
        esac
    done

    shift $(( OPTIND - 1 ))
fi

[ "$option_verbose" != 'true' ] && option_quiet='true' || option_quiet='false'

runner_opts='-w'
[ "$option_write_reports" != 'true' ] && runner_opts=''

count_fail=0
run_task "$option_quiet" 'Running unit test runner'        "${SELF_DIRNAME}/unit_runner.sh ${runner_opts}"
run_task "$option_quiet" 'Running regression test runner'  "${SELF_DIRNAME}/regression_runner.sh"
run_task "$option_quiet" 'Running integration test runner' "${SELF_DIRNAME}/integration_runner.sh ${runner_opts}"

printf '\n%s' "Completed in $SECONDS seconds"


if [ ! "$option_update_wiki" != 'true' ]
then
    # Do not proceed if a runner failed.
    if [ "$count_fail" -ne "0" ]
    then
        printf '\n%s tasks failed. Aborting ..\n' "$count_fail" 1>&2
        exit 1
    fi

    run_task "$option_quiet" 'Adding heading with current date to report if needed' wiki_check_add_header
    run_task "$option_quiet" 'Adding integration test log to Test Results wiki page' wiki_add_integration_link
    run_task "$option_quiet" 'Adding unit test log to Test Results wiki page' wiki_add_unit_link

    # TODO: Commit reports to version control.
fi
