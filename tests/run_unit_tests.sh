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
SELF_DIRNAME="$(dirname -- "$0")"

if ! source "${SELF_DIRNAME}/setup_environment.sh"
then
    cat >&2 <<EOF

[ERROR] Unable to source "${SELF_DIRNAME}/setup_environment.sh"
        Environment variable setup script is missing. Aborting ..

EOF
    exit "$EXIT_CRITICAL"
fi

if ! source "${AUTONAMEOW_ROOT_DIR}/tests/common_utils.sh"
then
    cat >&2 <<EOF

[ERROR] Unable to source "${AUTONAMEOW_ROOT_DIR}/tests/common_utils.sh"
        Shared test utility library is missing. Aborting ..

EOF
    exit "$EXIT_CRITICAL"
fi


exit_with_error_message_if_missing_command()
{
    local -r _cmdname="$1"

    if ! command -v "${_cmdname}" &>/dev/null
    then
        cat >&2 <<EOF

    [ERROR] This program requires "${_cmdname}" to run.

EOF
        exit 1
    fi
}

exit_with_error_message_if_missing_command 'python3'
exit_with_error_message_if_missing_command 'pytest'


# Default configuration.
option_write_report=false
option_quiet=false
option_enable_coverage=false
option_run_last_failed=false

print_usage_info()
{
    cat <<EOF

"${SELF_BASENAME}"  --  autonameow unit tests runner

  USAGE:  ${SELF_BASENAME} ([OPTIONS])

  OPTIONS:     -h   Display usage information and exit.
               -c   Enable checking unit test coverage.
               -l   Run tests that failed during the last run.
                    Note: Only supported by "pytest"!
               -w   Write HTML test reports to disk.
                    Note: the "raw" log file is always written.
               -q   Suppress output from test suites.

  All options are optional. Default behaviour is to not write any
  reports and print the test results to stdout/stderr in real-time.

  EXIT CODES:   ${EXIT_SUCCESS}   All tests/assertions passed.
                ${EXIT_FAILURE}   Any tests/assertions FAILED.
                ${EXIT_CRITICAL}   Runner itself failed or aborted.


Project website: www.github.com/jonasjberg/autonameow

EOF
}


# Set options to 'true' here and invert logic as necessary when testing (use
# "if not true"). Motivated by hopefully reducing bugs and weird behaviour
# caused by users setting the default option variables to unexpected values.
if [ "$#" -eq "0" ]
then
    printf '(USING DEFAULTS -- "%s -h" for usage information)\n\n' "$SELF_BASENAME"
else
    while getopts chlwq opt
    do
        case "$opt" in
            c) option_enable_coverage=true ;;
            h) print_usage_info ; exit "$EXIT_SUCCESS" ;;
            l) option_run_last_failed=true ;;
            w) option_write_report=true ;;
            q) option_quiet='true' ;;
        esac
    done

    shift $(( OPTIND - 1 ))
fi


# Workaround for pytest crashing when writing something other than stdout ..
captured_pytest_help="$(pytest --help 2>&1)"

if $option_write_report
then
    if ! grep -q -- '--html' <<< "$captured_pytest_help"
    then
        echo 'This script requires "pytest-html" to generate HTML reports.' 1>&2
        echo 'Install using pip by executing:  pip3 install pytest-html'
        exit "$EXIT_CRITICAL"
    fi
fi

if $option_enable_coverage
then
    if ! grep -q -- '--cov' <<< "$captured_pytest_help"
    then
        echo 'This script requires "pytest-cov" to check test coverage.' 1>&2
        echo 'Install using pip by executing:  pip3 install pytest-cov'
        exit "$EXIT_CRITICAL"
    fi
fi


_timestamp="$(date "+%Y-%m-%dT%H%M%S")"
_unittest_log="${AUTONAMEOW_TESTRESULTS_DIR}/unittest_log_${_timestamp}.html"
if [ -e "$_unittest_log" ]
then
    printf 'File exists: "%s" .. Aborting\n' "$_unittest_log" >&2
    exit "$EXIT_CRITICAL"
fi


run_pytest()
{
    declare -a _pytest_opts=('')
    $option_write_report    && _pytest_opts+="--self-contained-html --html="${_unittest_log}""
    $option_enable_coverage && _pytest_opts+='--cov=autonameow --cov-report=term '
    $option_run_last_failed && _pytest_opts+='--last-failed '

    (
        cd "$AUTONAMEOW_ROOT_DIR" || return 1
        PYTHONPATH=autonameow:tests pytest ${_pytest_opts[@]} tests/unit/test_*.py
    )
}


declare -i COUNT_FAIL=0
run_task "$option_quiet" "Running \"pytest\"" run_pytest


if [ -s "$_unittest_log" ]
then
    printf 'Wrote unit test HTML log file: "%s"\n' "$_unittest_log"

    # Write log file name to temporary file, used by other scripts.
    echo "${_unittest_log}" >| "${AUTONAMEOW_TESTRESULTS_DIR}/.unittestlog.toreport"
fi


if [ "$COUNT_FAIL" -eq "0" ]
then
    exit "$EXIT_SUCCESS"
else
    exit "$EXIT_FAILURE"
fi
