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

# Default configuration.
option_write_report='false'
option_quiet='false'


print_usage_info()
{
    cat <<EOF

"${SELF}"  --  autonameow unit tests runner

  USAGE:  ${SELF} ([OPTIONS])

  OPTIONS:  -h   Display usage information and exit.
            -w   Write HTML test reports to disk.
                 Note: the "raw" log file is always written.
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
    while getopts hwq opt
    do
        case "$opt" in
            h) print_usage_info ; exit 0 ;;
            w) option_write_report='true' ;;
            q) option_quiet='true' ;;
        esac
    done

    shift $(( $OPTIND - 1 ))
fi


HAS_PYTEST='false'
if command -v "pytest" >/dev/null 2>&1
then
    HAS_PYTEST='true'
fi


if [ "$option_write_report" == 'true' ]
then
    # Make sure required executables are available.
    if [ "$HAS_PYTEST" != 'true' ]
    then
        echo "This script requires \"pytest\" to generate HTML reports." 1>&2
        echo "Install using pip by executing:  pip3 install pytest"
        exit 1
    fi

    # Workaround for pytest crashing when writing something other than stdout ..
    _pytesthelp="$(pytest --help 2>&1)"
    if ! grep -q -- '--html' <<< "$_pytesthelp"
    then
        echo "This script requires \"pytest-html\" to generate HTML reports." 1>&2
        echo "Install using pip by executing:  pip3 install pytest-html"
        exit 1
    fi
fi


_timestamp="$(date "+%Y-%m-%dT%H%M%S")"
_unittest_log="${AUTONAMEOW_TESTRESULTS_DIR}/unittest_log_${_timestamp}.html"
if [ -e "$_unittest_log" ]
then
    echo "File exists: \"${_unittest_log}\" .. Aborting" >&2
    exit 1
fi


run_unittest()
{
    (
      cd "$AUTONAMEOW_ROOT_DIR" || return 1
      PYTHONPATH=autonameow:tests python3 -m unittest discover --catch --buffer --start-directory tests --pattern "unit_test_*.py" --top-level-directory .
    )
}

run_pytest()
{
    _pytest_report_opts=''
    [ "$option_write_report" != 'true' ] || _pytest_report_opts="--self-contained-html --html="${_unittest_log}""
    (
      cd "$AUTONAMEOW_ROOT_DIR" || return 1
      PYTHONPATH=autonameow:tests pytest ${_pytest_report_opts} tests/unit_test_*.py
    )
}


count_fail=0
if [ "$HAS_PYTEST" != 'true' ]
then
    run_task "$option_quiet" "Running \"unittest\"" run_unittest
else
    run_task "$option_quiet" "Running \"pytest\"" run_pytest
fi


if [ -s "$_unittest_log" ]
then
    echo "Wrote unit test HTML log file: \"${_unittest_log}\""

    # Write log file name to temporary file, used by other scripts.
    set +o noclobber
    echo "${_unittest_log}" > "${AUTONAMEOW_TESTRESULTS_DIR}/.unittestlog.toreport"
    set -o noclobber

    exit 0
fi

