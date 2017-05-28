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
SELF_DIR="$(dirname "$0")"

# Source 'integration_utils.sh', which in turn sources 'common_utils.sh'.
if ! source "${SELF_DIR}/integration_utils.sh"
then
    echo "Integration test utility library is missing. Aborting .." 1>&2
    exit 1
fi



# Test Cases
# ____________________________________________________________________________

# Store current time for later calculation of total execution time.
time_start="$(current_unix_time)"

logmsg "Started \"${SELF}\""
logmsg "Running the Command-Line Interface test suite .."



assert_true 'case $OSTYPE in darwin*) ;; linux*) ;; *) false ;; esac' \
            'Should be running a target operating system'

assert_true 'command -v python3 >/dev/null 2>&1' \
            "Python v3.x is available on the system"

AUTONAMEOW_RUNNER="$( ( cd "$SELF_DIR" && realpath -e "../run.sh" ) )"
assert_false '[ -z "$AUTONAMEOW_RUNNER" ]' \
             'Environment variable "AUTONAMEOW_RUNNER" should not be unset'

assert_true '[ -e "$AUTONAMEOW_RUNNER" ]' \
            "The autonameow launcher script \""$(basename -- "$AUTONAMEOW_RUNNER")"\" exists"

assert_true '[ -x "$AUTONAMEOW_RUNNER" ]' \
            "The autonameow launcher script has executable permission"

assert_true '"$AUTONAMEOW_RUNNER" >/dev/null' \
            "The autonameow launcher script can be started with no arguments"

assert_true '"$AUTONAMEOW_RUNNER" | grep -q -- "--help"' \
            "[TC005] autonameow should print how to get help when started with no arguments"

assert_true '"$AUTONAMEOW_RUNNER" --help | head -n 1 | grep -q -- "usage"' \
            "[TC005] autonameow should display usage information when started with \"--help\""

assert_true '"$AUTONAMEOW_RUNNER" --help | grep -q -- "dry-run"' \
            "[TC001] autonameow should provide a \"--dry-run\" option"

assert_true '( "$AUTONAMEOW_RUNNER" --interactive 2>&1 ) >/dev/null' \
            "[TC013] autonameow should provide a \"--interactive\" option"

assert_false '( "$AUTONAMEOW_RUNNER" --automagic 2>&1 ) >/dev/null' \
             "autonameow should return non-zero when started with \"--automagic\" without specifying files"


SAMPLE_JPG_FILE="$( ( cd "$SELF_DIR" && realpath -e "../test_files/smulan.jpg" ) )"
assert_true '[ -e "$SAMPLE_JPG_FILE" ]' \
            "The test sample jpg file exists. Add suitable test file if this test fails!"

assert_true '( "$AUTONAMEOW_RUNNER" --automagic --dry-run -- "$SAMPLE_JPG_FILE" 2>&1 ) >/dev/null' \
             "[TC011][TC001] autonameow should return zero when started with \"--automagic\", \"--dry-run\" and a valid file"

_expected_name="/tmp/2010-01-31T161251 a cat lying on a rug.jpg"
assert_true 'cp -n -- "$SAMPLE_JPG_FILE" /tmp/autonameow_sample 2>&1 >/dev/null' \
            "[rename_sample_jpg_file] Test setup should succeed"

assert_true '( "$AUTONAMEOW_RUNNER" --automagic --dry-run -- /tmp/autonameow_sample 2>&1 ) >/dev/null && [ -f "$_expected_name" ]' \
            "[rename_sample_jpg_file] [TC010][TC011] \""$(basename -- "${SAMPLE_JPG_FILE}")"\" should be renamed to \"${_expected_name}\""

assert_true '[ -f "/tmp/autonameow_sample" ] && rm -- "/tmp/autonameow_sample" ; [ -f "$_expected_name" ] && rm -- "$_expected_name" || true' \
            "[rename_sample_jpg_file] Test teardown should succeed"


assert_true '( "$AUTONAMEOW_RUNNER" --version 2>&1 ) >/dev/null' \
            "autonameow should return zero when started with \"--version\""

assert_true '( "$AUTONAMEOW_RUNNER" --version --verbose 2>&1 ) >/dev/null' \
            "autonameow should return zero when started with \"--version\" and \"--verbose\""

assert_true '( "$AUTONAMEOW_RUNNER" --version --debug 2>&1 ) >/dev/null' \
            "autonameow should return zero when started with \"--version\" and \"--debug\""



# Calculate total execution time.
time_end="$(current_unix_time)"
total_time="$((($time_end - $time_start) / 1000000))"

calculate_statistics
logmsg "Completed the Command-Line Interface test suite tests in ${total_time} ms"
