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

if [ -z "${AUTONAMEOW_ROOT_DIRPATH:-}" ]
then
    cat >&2 <<EOF

[ERROR] Integration test suites can no longer be run stand-alone.
        Please use use the designated integration test runner.

EOF
    exit 1
fi

# Resets test suite counter variables.
# shellcheck source=tests/integration/utils.sh
source "${AUTONAMEOW_ROOT_DIRPATH}/tests/integration/utils.sh"



# Test Cases
# ____________________________________________________________________________

# Store current time for later calculation of total execution time.
time_start="$(aw_utils.current_unix_time)"

TESTSUITE_NAME='Documentation'
aw_utils.log_msg "Running the $TESTSUITE_NAME test suite .."



DOC_PATH="$(realpath --canonicalize-existing -- "${AUTONAMEOW_ROOT_DIRPATH}/docs/")"
doc_path_basename="$(basename -- "$DOC_PATH")"
aw_utils.assert_true '[ -d "$DOC_PATH" ]' \
            "Documentation directory \"${doc_path_basename}\" should exist"

_srcroot_readme="${AUTONAMEOW_ROOT_DIRPATH}/README.md"
aw_utils.assert_bulk_test "$_srcroot_readme" n e f r

aw_utils.assert_true '[ -f "$_srcroot_readme" ]' \
            'The root source directory should contain a "README.md"'




# Calculate total execution time.
time_end="$(aw_utils.current_unix_time)"
total_time="$(aw_utils.calculate_execution_time "$time_start" "$time_end")"

aw_utils.log_test_suite_results_summary "$TESTSUITE_NAME" "$total_time"
aw_utils.update_global_test_results
