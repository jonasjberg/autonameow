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

SELF_BASENAME="$(basename -- "$0")"
self_dirpath="$(realpath -e -- "$(dirname -- "$0")")"
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


# Default configuration.
option_write_reports=false
option_verbose=false


print_usage_info()
{
    cat <<EOF

"$SELF_BASENAME"  --  autonameow test suite helper script

  USAGE:  $SELF_BASENAME ([OPTIONS])

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


if [ "$#" -eq "0" ]
then
    printf '(USING DEFAULTS -- "%s -h" for usage information)\n\n' "$SELF_BASENAME"
else
    while getopts hvw opt
    do
        case "$opt" in
            h) print_usage_info ; exit "$EXIT_SUCCESS" ;;
            v) option_verbose=true ;;
            w) option_write_reports=true ;;
        esac
    done

    shift $(( OPTIND - 1 ))
fi

option_quiet=true
$option_verbose && option_quiet=false

runner_opts=''
$option_write_reports && runner_opts='-w'

declare -i COUNT_FAIL=0
run_task "$option_quiet" 'Running unit test runner'        '${self_dirpath}/run_unit_tests.sh $runner_opts'
run_task "$option_quiet" 'Running regression test runner'  '${self_dirpath}/run_regression_tests.sh -f "!*LOCAL*"'
run_task "$option_quiet" 'Running integration test runner' '${self_dirpath}/run_integration_tests.sh'

printf '\n%s\n' "Completed in $SECONDS seconds"


if [ "$COUNT_FAIL" -eq "0" ]
then
    exit "$EXIT_SUCCESS"
else
    exit "$EXIT_FAILURE"
fi
