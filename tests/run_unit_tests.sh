#!/usr/bin/env bash

#   Copyright(c) 2016-2019 Jonas Sjöberg <autonameow@jonasjberg.com>
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

self_basename="$(basename -- "$0")"
self_dirpath="$(realpath --canonicalize-existing -- "$(dirname -- "$0")")"
readonly self_basename
readonly self_dirpath

# shellcheck source=tests/setup_environment.sh
if ! source "${self_dirpath}/setup_environment.sh"
then
    cat >&2 <<EOF

[ERROR] Unable to source "${self_dirpath}/setup_environment.sh"
        Environment variable setup script is missing. Aborting ..

EOF
    exit "$EXIT_CRITICAL"
fi

# shellcheck source=tests/common_utils.sh
if ! source "${AUTONAMEOW_ROOT_DIRPATH}/tests/common_utils.sh"
then
    cat >&2 <<EOF

[ERROR] Unable to source "${AUTONAMEOW_ROOT_DIRPATH}/tests/common_utils.sh"
        Shared test utility library is missing. Aborting ..

EOF
    exit "$EXIT_CRITICAL"
fi


exit_with_error_message_if_missing_command()
{
    local -r _cmdname="$1"

    if ! command -v "$_cmdname" &>/dev/null
    then
        cat >&2 <<EOF

    [ERROR] This program requires "$_cmdname" to run.

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

"$self_basename"  --  autonameow unit tests runner

  USAGE:  $self_basename ([OPTIONS])

  OPTIONS:     -h   Display usage information and exit.
               -c   Enable checking unit test coverage.
               -l   Run tests that failed during the last run.
                    Note: Only supported by "pytest"!
               -w   Write HTML test reports to disk.
                    Note: the "raw" log file is always written.
               -q   Suppress output from test suites.

  All options are optional. Default behaviour is to not write any
  reports and print the test results to stdout/stderr in real-time.

  EXIT CODES:   $EXIT_SUCCESS    All tests/assertions passed.
                $EXIT_FAILURE    Any tests/assertions FAILED.
                $EXIT_CRITICAL   Runner itself failed or aborted.


Project website: www.github.com/jonasjberg/autonameow

EOF
}


if [ "$#" -eq "0" ]
then
    printf '(USING DEFAULTS -- "%s -h" for usage information)\n\n' "$self_basename"
else
    while getopts chlwq opt
    do
        case "$opt" in
            c) option_enable_coverage=true ;;
            h) print_usage_info ; exit "$EXIT_SUCCESS" ;;
            l) option_run_last_failed=true ;;
            w) option_write_report=true ;;
            q) option_quiet=true ;;
        esac
    done

    shift $(( OPTIND - 1 ))
fi


# Workaround for pytest crashing when writing something other than stdout ..
captured_pytest_help="$(pytest --help 2>&1)"

if [ "$option_write_report" = 'true' ]
then
    if ! grep -q -- '--html' <<< "$captured_pytest_help"
    then
        command cat 1>&2 <<'EOF'
This script requires "pytest-html" to generate HTML reports.
Install by executing:

    $ pip3 install pytest-html

EOF
        exit "$EXIT_CRITICAL"
    fi
fi

if [ "$option_enable_coverage" = 'true' ]
then
    if ! grep -q -- '--cov' <<< "$captured_pytest_help"
    then
        command cat 1>&2 <<'EOF'
This script requires "pytest-cov" to check test coverage.
Install by executing:

    $ pip3 install pytest-cov

EOF
        exit "$EXIT_CRITICAL"
    fi
fi


_timestamp="$(date "+%Y-%m-%dT%H%M%S.%N")"
_unittest_log="${AUTONAMEOW_TESTRESULTS_DIRPATH}/unittest_log_${_timestamp}.html"
if [ -e "$_unittest_log" ]
then
    printf 'File exists: "%s" .. Aborting\n' "$_unittest_log" >&2
    exit "$EXIT_CRITICAL"
fi


run_pytest()
{
    declare -a _pytest_opts=('')

    if [ "$option_write_report" = 'true' ]
    then
        _pytest_opts+=('--self-contained-html')
        _pytest_opts+=(--html="$_unittest_log")
    fi

    if [ "$option_enable_coverage" = 'true' ]
    then
        _pytest_opts+=('--cov=autonameow')
        _pytest_opts+=('--cov-report=term')
    fi

    if [ "$option_run_last_failed" = 'true' ]
    then
        _pytest_opts+=('--last-failed')
    fi

    (
        cd "$AUTONAMEOW_ROOT_DIRPATH" || return 1
        PYTHONPATH=autonameow:tests pytest ${_pytest_opts[@]} tests/unit/test_*.py
    )
}


declare -i COUNT_FAIL=0
run_task "$option_quiet" "Running \"pytest\"" run_pytest


if [ "$COUNT_FAIL" -eq "0" ]
then
    exit "$EXIT_SUCCESS"
else
    exit "$EXIT_FAILURE"
fi
