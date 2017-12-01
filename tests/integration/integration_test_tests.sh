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
if [ -z "${AUTONAMEOW_ROOT_DIR:-}" ]
then
    cat >&2 <<EOF

[ERROR] Integration test suites can no longer be run stand-alone.
        Please use use the designated integration test runner.

EOF
    exit 1
fi

source "${AUTONAMEOW_ROOT_DIR}/tests/integration/integration_utils.sh"



# Test Cases
# ____________________________________________________________________________

# Store current time for later calculation of total execution time.
time_start="$(current_unix_time)"

TESTSUITE_NAME='Test Suite'
logmsg "Started \"${SELF_BASENAME}\""
logmsg "Running the "$TESTSUITE_NAME" test suite .."



assert_true  '[ "0" -eq "0" ]' 'Expect success .. (true positive)'
#assert_true  '[ "1" -eq "0" ]' 'Expect failure .. (false negative)'
assert_false '[ "1" -eq "0" ]' 'Expect success .. (true positive)'
#assert_false '[ "1" -ne "0" ]' 'Expect failure .. (false negative)'


assert_true '[ -e "${AUTONAMEOW_ROOT_DIR}/tests/common_utils.sh" ]' \
            'Shared test utility library exists'

assert_true '[ -x "${AUTONAMEOW_ROOT_DIR}/tests/common_utils.sh" ]' \
            'Shared test utility library is executable'

assert_false '[ -z "$AUTONAMEOW_ROOT_DIR" ]' \
             'Environment variable "AUTONAMEOW_ROOT_DIR" should not be unset'

assert_true '[ -d "$AUTONAMEOW_ROOT_DIR" ]' \
            'Environment variable "AUTONAMEOW_ROOT_DIR" should be a directory'

assert_false '[ -z "$AUTONAMEOW_TESTRESULTS_DIR" ]' \
             'Environment variable "AUTONAMEOW_TESTRESULTS_DIR" should not be unset'

assert_true '[ -d "$AUTONAMEOW_TESTRESULTS_DIR" ]' \
            'Environment variable "AUTONAMEOW_TESTRESULTS_DIR" should be a directory'

assert_false '[ -z "$AUTONAMEOW_WIKI_ROOT_DIR" ]' \
             'Environment variable "AUTONAMEOW_WIKI_ROOT_DIR" should not be unset'

assert_true '[ -d "$AUTONAMEOW_WIKI_ROOT_DIR" ]' \
            'Environment variable "AUTONAMEOW_WIKI_ROOT_DIR" should be a directory'

assert_true '[ -e "${AUTONAMEOW_ROOT_DIR}/tests/integration_runner.sh" ]' \
            'The integration test runner exists'

assert_true '[ -x "${AUTONAMEOW_ROOT_DIR}/tests/integration_runner.sh" ]' \
            'The integration test runner is executable'

assert_true '[ -e "${AUTONAMEOW_ROOT_DIR}/tests/integration/integration_test_cli.sh" ]' \
            "The Command-Line Interface test suite exists"

assert_true '[ -x "${AUTONAMEOW_ROOT_DIR}/tests/integration/integration_test_cli.sh" ]' \
            'The Command-Line Interface test suite is executable'

assert_true '[ -e "${AUTONAMEOW_ROOT_DIR}/tests/integration/integration_test_docs.sh" ]' \
            'The Documentation test suite exists'

assert_true '[ -x "${AUTONAMEOW_ROOT_DIR}/tests/integration/integration_test_docs.sh" ]' \
            'The Documentation test suite is executable'

assert_true '[ -e "${AUTONAMEOW_ROOT_DIR}/tests/unit_runner.sh" ]' \
            'The unit test runner exists'

assert_true '[ -x "${AUTONAMEOW_ROOT_DIR}/tests/unit_runner.sh" ]' \
            'The unit test runner is executable'

assert_true 'command -v "aha"' \
            'The executable "aha" is available on the system'

assert_true 'command -v "pytest"' \
            'The executable "pytest" is available on the system'

_pytesthelp="$(pytest --help 2>&1)"
assert_true 'grep -q -- "--html" <<< "$_pytesthelp"' \
            'Module "pytest-html" is available on the system'

assert_true 'case $OSTYPE in darwin*) ;; linux*) ;; *) false ;; esac' \
            'Should be running a target operating system'

assert_true 'type -t get_timestamp_from_basename' \
            '"get_timestamp_from_basename" is a function'

assert_false '[ -n "$(get_timestamp_from_basename "abc")" ]' \
             '"get_timestamp_from_basename" returns empty string given "abc"'

assert_true 'get_timestamp_from_basename "unittest_log_2017-05-15T134801.html" | grep -qE -- "^2017-05-15 13:48:01$"' \
            '"get_timestamp_from_basename" returns "2017-05-15 13:48:01" given "unittest_log_2017-05-15T134801.html"'

_abspath_testfile_empty="$(abspath_testfile "empty")"
assert_false '[ -z "${_abspath_testfile_empty}" ]' \
             'abspath_testfile "empty" should return something'

assert_true '[ -e "${_abspath_testfile_empty}" ]' \
            'abspath_testfile "empty" should an existing path'

assert_true '[ -f "${_abspath_testfile_empty}" ]' \
            'abspath_testfile "empty" should the path to an existing file'

_abspath_testfile_subdir="$(abspath_testfile "subdir")"
assert_false '[ -z "${_abspath_testfile_subdir}" ]' \
             'abspath_testfile "subdir" should return something'

assert_true '[ -e "${_abspath_testfile_subdir}" ]' \
            'abspath_testfile "subdir" should an existing path'

assert_true '[ -d "${_abspath_testfile_subdir}" ]' \
            'abspath_testfile "subdir" should the path to an existing directory'

assert_true 'type -t calculate_execution_time' \
            '"calculate_execution_time" is a function'

assert_true '[ "$(calculate_execution_time 1501987087187088013 1501987087942286968)" -eq "755" ]' \
            'calculate_execution_time returns expected (755ms)'

assert_true '[ "$(calculate_execution_time 1501987193168368101 1501987208094155073)" -eq "14925" ]' \
            'calculate_execution_time returns expected (14925ms)'



# Calculate total execution time.
time_end="$(current_unix_time)"
total_time="$(calculate_execution_time "$time_start" "$time_end")"

log_test_suite_results_summary "$TESTSUITE_NAME" "$total_time"
