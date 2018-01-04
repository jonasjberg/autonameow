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

if [ -z "${AUTONAMEOW_ROOT_DIR:-}" ]
then
    cat >&2 <<EOF

[ERROR] Integration test suites can no longer be run stand-alone.
        Please use use the designated integration test runner.

EOF
    exit 1
fi

# Resets test suite counter variables.
source "${AUTONAMEOW_ROOT_DIR}/tests/integration/utils.sh"



# Test Cases
# ____________________________________________________________________________

# Store current time for later calculation of total execution time.
time_start="$(current_unix_time)"

TESTSUITE_NAME='Test Suite'
logmsg "Running the ${TESTSUITE_NAME} test suite .."



assert_true  '[ "0" -eq "0" ]' 'Expect success .. (true positive)'
#assert_true  '[ "1" -eq "0" ]' 'Expect failure .. (false negative)'
assert_false '[ "1" -eq "0" ]' 'Expect success .. (true positive)'
#assert_false '[ "1" -ne "0" ]' 'Expect failure .. (false negative)'


# ______________________________________________________________________________
#
# Check shared environment variables, used by all tests.

assert_bulk_test "$AUTONAMEOW_ROOT_DIR" n e d r w x

assert_false '[ -z "$AUTONAMEOW_ROOT_DIR" ]' \
             'Environment variable "AUTONAMEOW_ROOT_DIR" should not be unset'

assert_true '[ -d "$AUTONAMEOW_ROOT_DIR" ]' \
            'Environment variable "AUTONAMEOW_ROOT_DIR" should be a directory'

assert_true '[ -r "$AUTONAMEOW_ROOT_DIR" ]' \
            'Environment variable "AUTONAMEOW_ROOT_DIR" should be a existing readable path'


_common_utils_path="${AUTONAMEOW_ROOT_DIR}/tests/common_utils.sh"
assert_bulk_test "$_common_utils_path" e r x

_setup_environment_path="${AUTONAMEOW_ROOT_DIR}/tests/setup_environment.sh"
assert_bulk_test "$_setup_environment_path" e r x

assert_true '[ -e "$_setup_environment_path" ]' \
            'Shared test environment setup script exists'

assert_true '[ -r "$_setup_environment_path" ]' \
            'Shared test environment setup script exists and is readable'

assert_true '[ -x "$_setup_environment_path" ]' \
            'Shared test environment setup script is executable'


assert_bulk_test "$AUTONAMEOW_TESTRESULTS_DIR" n e d

assert_false '[ -z "$AUTONAMEOW_TESTRESULTS_DIR" ]' \
             'Environment variable "AUTONAMEOW_TESTRESULTS_DIR" should not be unset'

assert_true '[ -d "$AUTONAMEOW_TESTRESULTS_DIR" ]' \
            'Environment variable "AUTONAMEOW_TESTRESULTS_DIR" should be a directory'


assert_bulk_test "$AUTONAMEOW_WIKI_ROOT_DIR" n e d

assert_false '[ -z "$AUTONAMEOW_WIKI_ROOT_DIR" ]' \
             'Environment variable "AUTONAMEOW_WIKI_ROOT_DIR" should not be unset'

assert_true '[ -d "$AUTONAMEOW_WIKI_ROOT_DIR" ]' \
            'Environment variable "AUTONAMEOW_WIKI_ROOT_DIR" should be a directory'


# ______________________________________________________________________________
#
# Check environment variables used by specific types of tests.

assert_bulk_test "$AUTONAMEOW_INTEGRATION_STATS" n e f
assert_false '[ -z "$AUTONAMEOW_INTEGRATION_STATS" ]' \
             'Environment variable "AUTONAMEOW_INTEGRATION_STATS" should not be unset'

assert_true '[ -f "$AUTONAMEOW_INTEGRATION_STATS" ]' \
            'Environment variable "AUTONAMEOW_INTEGRATION_STATS" should be a file'

assert_bulk_test "$AUTONAMEOW_INTEGRATION_LOG" n
assert_false '[ -z "$AUTONAMEOW_INTEGRATION_LOG" ]' \
             'Environment variable "AUTONAMEOW_INTEGRATION_LOG" should not be unset'

assert_false '[ -d "$AUTONAMEOW_INTEGRATION_LOG" ]' \
             'Environment variable "AUTONAMEOW_INTEGRATION_LOG" should not be a directory'

assert_bulk_test "$AUTONAMEOW_INTEGRATION_TIMESTAMP" n
assert_false '[ -z "$AUTONAMEOW_INTEGRATION_TIMESTAMP" ]' \
             'Environment variable "AUTONAMEOW_INTEGRATION_TIMESTAMP" should not be unset'


# ______________________________________________________________________________
#
# Check the test runner scripts.

_integration_runner_path="${AUTONAMEOW_ROOT_DIR}/tests/integration_runner.sh"
assert_bulk_test "$_integration_runner_path" n e r x

_unit_runner_path="${AUTONAMEOW_ROOT_DIR}/tests/unit_runner.sh"
assert_bulk_test "$_unit_runner_path" n e r x

_regression_runner_path="${AUTONAMEOW_ROOT_DIR}/tests/regression_runner.sh"
assert_bulk_test "$_regression_runner_path" n e r x


# ______________________________________________________________________________
#
# Verify that required (or preferred) commands are available.

assert_true 'case $OSTYPE in darwin*) ;; linux*) ;; *) false ;; esac' \
            'Should be running a target operating system'

assert_false '[ -z "$TERM" ]' \
             'Environment variable "$TERM" should be set'

assert_true 'command -v python3' \
            'Python v3.x is available on the system'

assert_true 'python3 --version | grep "Python 3\.[5-9]\.[0-9]"' \
            'Python v3.5.0 or newer is available on the system'

assert_bulk_test "$AUTONAMEOW_RUNNER" n e r x

assert_true 'command -v exiftool' \
            'exiftool is available on the system'

assert_true 'command -v tesseract' \
            'tesseract is available on the system'

assert_true 'command -v sed' \
            'sed is available on the system'

assert_true 'man sed | grep -- "^ \+.*-i\b"' \
            'sed supports the "-i" option, required by some integration tests'

assert_true 'command -v git' \
            'git is available on the system'

assert_true 'command -v aha' \
            'The executable "aha" is available on the system'

assert_true 'command -v pytest' \
            'The executable "pytest" is available on the system'

_pytesthelp="$(pytest --help 2>&1)"
assert_true 'grep -q -- "--html" <<< "$_pytesthelp"' \
            'Module "pytest-html" is available on the system'

assert_true 'command -v pylint' \
            'The executable "pylint" is available on the system'

assert_true 'case $OSTYPE in darwin*) ;; linux*) ;; *) false ;; esac' \
            'Should be running a target operating system'


# ______________________________________________________________________________
#
# Shared bash script (integration test) functionality.

assert_true 'type -t get_timestamp_from_basename' \
            'get_timestamp_from_basename is a function'

assert_false '[ -n "$(get_timestamp_from_basename "abc")" ]' \
             'get_timestamp_from_basename returns empty string given "abc"'

assert_true 'get_timestamp_from_basename "unittest_log_2017-05-15T134801.html" | grep -qE -- "^2017-05-15 13:48:01$"' \
            'get_timestamp_from_basename returns "2017-05-15 13:48:01" given "unittest_log_2017-05-15T134801.html"'

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
            'calculate_execution_time is a function'

assert_true '[ "$(calculate_execution_time 1501987087187088013 1501987087942286968)" -eq "755" ]' \
            'calculate_execution_time returns expected (755ms)'

assert_true '[ "$(calculate_execution_time 1501987193168368101 1501987208094155073)" -eq "14925" ]' \
            'calculate_execution_time returns expected (14925ms)'

assert_bulk_test "$AUTONAMEOW_ROOT_DIR"
assert_bulk_test "$AUTONAMEOW_ROOT_DIR" e
assert_bulk_test "$AUTONAMEOW_ROOT_DIR" d
assert_bulk_test "$AUTONAMEOW_ROOT_DIR" r
assert_bulk_test "$AUTONAMEOW_ROOT_DIR" w
assert_bulk_test "$AUTONAMEOW_ROOT_DIR" x
assert_bulk_test "$AUTONAMEOW_ROOT_DIR" e d
assert_bulk_test "$AUTONAMEOW_ROOT_DIR" e d r
assert_bulk_test "$AUTONAMEOW_ROOT_DIR" e d r w
assert_bulk_test "$AUTONAMEOW_ROOT_DIR" e d r x
assert_bulk_test "$AUTONAMEOW_ROOT_DIR" e r
assert_bulk_test "$AUTONAMEOW_ROOT_DIR" e r w
assert_bulk_test "$AUTONAMEOW_ROOT_DIR" e r x
assert_bulk_test "$AUTONAMEOW_ROOT_DIR" e w
assert_bulk_test "$AUTONAMEOW_ROOT_DIR" e w x
assert_bulk_test "$AUTONAMEOW_ROOT_DIR" e x


_temporary_file='.___temporary__file__'
[ -f "$_temporary_file" ] || touch "$_temporary_file"
assert_true '[ -e "${_temporary_file}" ]' \
            'Reference dummy temporary was created'

assert_bulk_test "$_temporary_file"
assert_bulk_test "$_temporary_file" e
assert_bulk_test "$_temporary_file" f
assert_bulk_test "$_temporary_file" r
assert_bulk_test "$_temporary_file" w
assert_bulk_test "$_temporary_file" e f
assert_bulk_test "$_temporary_file" e f r
assert_bulk_test "$_temporary_file" e f r w
assert_bulk_test "$_temporary_file" e r
assert_bulk_test "$_temporary_file" e r w
assert_bulk_test "$_temporary_file" e w
assert_bulk_test "$_temporary_file" e w
assert_bulk_test "$_temporary_file" e
assert_bulk_test "$_temporary_file" f
assert_bulk_test "$_temporary_file" f r
assert_bulk_test "$_temporary_file" f r w
assert_bulk_test "$_temporary_file" f w

rm "$_temporary_file"
assert_false '[ -e "${_temporary_file}" ]' \
             'Reference dummy temporary file was deleted'




# Calculate total execution time.
time_end="$(current_unix_time)"
total_time="$(calculate_execution_time "$time_start" "$time_end")"

log_test_suite_results_summary "$TESTSUITE_NAME" "$total_time"
update_global_test_results
