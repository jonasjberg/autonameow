#!/usr/bin/env bash

#   Copyright(c) 2016-2018 Jonas Sjöberg
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


declare -r EXIT_SUCCESS=0
declare -r EXIT_FAILURE=1
declare -r EXIT_CRITICAL=2

SELF_BASENAME="$(basename "$0")"
SELF_DIRNAME="$(realpath -e "$(dirname "$0")")"

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


# Default configuration.
option_write_reports='false'
option_verbose='false'


print_usage_info()
{
    cat <<EOF

"${SELF_BASENAME}"  --  autonameow test suite helper script

  USAGE:  ${SELF_BASENAME} ([OPTIONS])

  OPTIONS:     -h   Display usage information and exit.
               -v   Enable all output from the unit/integration-runners.
                    This also increases the verbosity of this script.
               -w   Write result reports in HTML and PDF format.

  All flags are optional. Default behaviour is to suppress all output
  from the unit/integration/regression-runners and not write logs to disk.
  Note that temporary ("*.raw") logs might still be written --- refer to
  the individual test runners for up-to-date specifics.

  When not using "-v" (default), the individual test runners are marked
  [FAILED] if the exit status is non-zero. This *probably* means that not
  all tests/assertions passed or that the test runner itself failed.
  Conversely, if the test runner returns zero, it is marked [FINISHED].

  Refer to the individual test runners for up-to-date information on
  any special exit codes.


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
    while getopts hvw opt
    do
        case "$opt" in
            h) print_usage_info ; exit "$EXIT_SUCCESS" ;;
            v) option_verbose='true' ;;
            w) option_write_reports='true' ;;
        esac
    done

    shift $(( OPTIND - 1 ))
fi

[ "$option_verbose" != 'true' ] && option_quiet='true' || option_quiet='false'

runner_opts='-w'
[ "$option_write_reports" != 'true' ] && runner_opts=''

declare -i COUNT_FAIL=0
run_task "$option_quiet" 'Running unit test runner'        "${SELF_DIRNAME}/run_unit_tests.sh ${runner_opts}"
run_task "$option_quiet" 'Running regression test runner'  "${SELF_DIRNAME}/run_regression_tests.sh"
run_task "$option_quiet" 'Running integration test runner' "${SELF_DIRNAME}/run_integration_tests.sh ${runner_opts}"

printf '\n%s' "Completed in $SECONDS seconds"


if [ "$COUNT_FAIL" -eq "0" ]
then
    exit "$EXIT_SUCCESS"
else
    exit "$EXIT_FAILURE"
fi
