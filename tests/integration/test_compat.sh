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

source "$AUTONAMEOW_ROOT_DIR/tests/integration/utils.sh"



# Test Cases
# ____________________________________________________________________________

# Store current time for later calculation of total execution time.
time_start="$(current_unix_time)"

TESTSUITE_NAME='Compatibility'
logmsg "Started \"${SELF_BASENAME}\""
logmsg "Running the "$TESTSUITE_NAME" test suite .."



assert_true 'case $OSTYPE in darwin*) ;; linux*) ;; *) false ;; esac' \
            'Should be running a target operating system'

assert_true 'command -v python3' \
            "Python v3.x is available on the system"

assert_true 'python3 --version | grep "Python 3\.[5-9]\.[0-9]"' \
            "Python v3.5.0 or newer is available on the system"

assert_true 'command -v exiftool' \
            "exiftool is available on the system"

assert_true 'command -v tesseract' \
            "tesseract is available on the system"

assert_false '[ -z "$AUTONAMEOW_RUNNER" ]' \
             'Environment variable "AUTONAMEOW_RUNNER" should not be unset'

assert_true '[ -e "$AUTONAMEOW_RUNNER" ]' \
            "The autonameow launcher script \""$(basename -- "$AUTONAMEOW_RUNNER")"\" exists"

assert_true '[ -x "$AUTONAMEOW_RUNNER" ]' \
            "The autonameow launcher script has executable permission"

assert_true '"$AUTONAMEOW_RUNNER"' \
            "The autonameow launcher script can be started with no arguments"

assert_true '"$AUTONAMEOW_RUNNER" --version' \
            "autonameow should return zero when started with \"--version\""

assert_true '"$AUTONAMEOW_RUNNER" --version 2>&1 | grep -o -- "v[0-9]\.[0-9]\.[0-9]"' \
            "The output should contain a version string matching \"vX.X.X\" when started with \"--version\""

AUTONAMEOW_VERSION="$(( "$AUTONAMEOW_RUNNER" --version 2>&1 ) | grep -o -- "v[0-9]\.[0-9]\.[0-9]" | grep -o -- "[0-9]\.[0-9]\.[0-9]")"
assert_false '[ -z "$AUTONAMEOW_VERSION" ]' \
             'This test script should be able to retrieve the program version.'

assert_true '"$AUTONAMEOW_RUNNER" --verbose 2>&1 | grep -o -- "Using configuration: \".*\"$"' \
            "The output should include the currently used configuration file when started with \"--verbose\""

AUTONAMEOW_CONFIG_PATH="$(( "$AUTONAMEOW_RUNNER" --verbose 2>&1 ) | grep -o -- "Using configuration: \".*\"$" | grep -o -- "\".*\"")"
assert_false '[ -z "$AUTONAMEOW_CONFIG_PATH" ]' \
             'This test script should be able to retrieve the path of the used configuration file.'

# Strip quotes from configuration file path.
AUTONAMEOW_CONFIG_PATH="${AUTONAMEOW_CONFIG_PATH//\"/}"

assert_true '[ -f "$AUTONAMEOW_CONFIG_PATH" ]' \
            'The path of the used configuration file should be a existing file.'

assert_true 'grep -oE -- "autonameow_version: v?[0-9]\.[0-9]\.[0-9]$" "$AUTONAMEOW_CONFIG_PATH"' \
            "The retrieved configuration file contents should match \"autonameow_version: X.X.X$\""

CONFIG_FILE_VERSION="$(grep -oE -- "autonameow_version: v?[0-9]\.[0-9]\.[0-9]$" "$AUTONAMEOW_CONFIG_PATH" | grep -o -- "[0-9]\.[0-9]\.[0-9]")"
assert_false '[ -z "$CONFIG_FILE_VERSION" ]' \
             'This test script should be able to retrieve the configuration file version.'

assert_true '[ "$AUTONAMEOW_VERSION" = "$CONFIG_FILE_VERSION" ]' \
            'The configuration file version should equal the program version'


EMPTY_CONFIG='/tmp/autonameow_empty_config.yaml'
assert_true 'touch "$EMPTY_CONFIG"' \
            "detect_empty_config Test setup should succeed"

assert_false '"$AUTONAMEOW_RUNNER" --config-path "$EMPTY_CONFIG"' \
             "detect_empty_config Specifying a empty configuration file with \"--config-path\" should be handled properly"

assert_true '[ -f "$EMPTY_CONFIG" ] && rm -- "$EMPTY_CONFIG"' \
            "detect_empty_config Test teardown should succeed"

assert_false '"$AUTONAMEOW_RUNNER" --config-path /tmp/does_not_exist_surely.mjao' \
             "Specifying an invalid path with \"--config-path\" should be handled properly"


BAD_CONFIG_FILE="$(abspath_testfile "configs/bad_corrupt_gif.yaml")"
assert_true '[ -e "$BAD_CONFIG_FILE" ]' \
            "A known bad configuration file exists. Add suitable test file if this test fails!"

assert_false '"$AUTONAMEOW_RUNNER" --config-path "$BAD_CONFIG_FILE"' \
             "Attempting to load a invalid configuration file with \"--config-path\" should be handled properly"


assert_true '"$AUTONAMEOW_RUNNER" --dump-options --verbose' \
            "autonameow should return zero when started with \"--dump-options\" and \"--verbose\""


NONASCII_CONFIG_FILE="$(abspath_testfile "configs/autonam€öw.yaml")"
assert_true '[ -e "$NONASCII_CONFIG_FILE" ]' \
            "A non-ASCII configuration file exists. Add suitable test file if this test fails!"

assert_true '"$AUTONAMEOW_RUNNER" --config-path "$NONASCII_CONFIG_FILE"' \
             "Attempting to load a non-ASCII configuration file with \"--config-path\" should be handled properly"

assert_true '"$AUTONAMEOW_RUNNER" --verbose --config-path "$NONASCII_CONFIG_FILE"' \
             "Expect exit code 0 for non-ASCII configuration file and \"--verbose\""

assert_true '"$AUTONAMEOW_RUNNER" --debug --config-path "$NONASCII_CONFIG_FILE"' \
             "Expect exit code 0 for non-ASCII configuration file and \"--debug\""

assert_true '"$AUTONAMEOW_RUNNER" --quiet --config-path "$NONASCII_CONFIG_FILE"' \
             "Expect exit code 0 for non-ASCII configuration file and \"--quiet\""

assert_true '"$AUTONAMEOW_RUNNER" --dump-options --config-path "$NONASCII_CONFIG_FILE"' \
             "Expect exit code 0 for non-ASCII configuration file and \"--dump-options\""

assert_true '"$AUTONAMEOW_RUNNER" --dump-options --verbose --config-path "$NONASCII_CONFIG_FILE"' \
             "Expect exit code 0 for non-ASCII configuration file and \"--dump-options\", \"--verbose\""

assert_true '"$AUTONAMEOW_RUNNER" --dump-options --debug --config-path "$NONASCII_CONFIG_FILE"' \
             "Expect exit code 0 for non-ASCII configuration file and \"--dump-options\", \"--debug\""

assert_true '"$AUTONAMEOW_RUNNER" --dump-options --quiet --config-path "$NONASCII_CONFIG_FILE"' \
             "Expect exit code 0 for non-ASCII configuration file and \"--dump-options\", \"--quiet\""


set +o pipefail
BAD_CONFIG_FILE_NO_FILE_RULES="$(abspath_testfile "configs/bad_no_file_rules.yaml")"
assert_true '[ -e "$BAD_CONFIG_FILE_NO_FILE_RULES" ]' \
            "A configuration file without file rules exists. Add suitable test file if this test fails!"

assert_true '"$AUTONAMEOW_RUNNER" --config-path "$BAD_CONFIG_FILE_NO_FILE_RULES" 2>&1 | grep -q "Unable to load configuration"' \
            "Attempting to load a configuration file without any file rules should be handled properly"

BAD_CONFIG_FILE_EMPTY_BUT_SECTIONS="$(abspath_testfile "configs/bad_empty_but_sections.yaml")"
assert_true '[ -e "$BAD_CONFIG_FILE_EMPTY_BUT_SECTIONS" ]' \
            "A configuration file that contains only sections without contents exists. Add suitable test file if this test fails!"

assert_true '"$AUTONAMEOW_RUNNER" --config-path "$BAD_CONFIG_FILE_EMPTY_BUT_SECTIONS" 2>&1 | grep -q "Unable to load configuration"' \
            "Attempting to load a configuration file with just bare sections should be handled properly"
set -o pipefail


# Find all files matching "test_files/configs/bad_0*.yaml"
# and check for non-zero return codes in various options.
while IFS= read -r -d '' bad_config_file
do
    config_file_abspath="$(realpath -e -- "$bad_config_file")"
    config_file_basename="$(basename -- "$bad_config_file")"
    assert_true '[ -e "$config_file_abspath" ]' \
                "Bad configuration file exists: \"${config_file_basename}\""

    assert_false '"$AUTONAMEOW_RUNNER" --dry-run --batch --config-path "$BAD_CONFIG_FILE"' \
                 "Expect non-zero exit code for bad config: \"${config_file_basename}\""

    assert_false '"$AUTONAMEOW_RUNNER" -v --dry-run --batch --config-path "$BAD_CONFIG_FILE"' \
                 "Expect non-zero exit code for bad config: \"${config_file_basename}\" in batch, verbose mode"

    assert_false '"$AUTONAMEOW_RUNNER" --debug --dry-run --batch --config-path "$BAD_CONFIG_FILE"' \
                 "Expect non-zero exit code for bad config: \"${config_file_basename}\" in batch, debug mode"

    assert_false '"$AUTONAMEOW_RUNNER" --quiet --dry-run --batch --config-path "$BAD_CONFIG_FILE"' \
                 "Expect non-zero exit code for bad config: \"${config_file_basename}\" in batch, quiet mode"

    assert_false '"$AUTONAMEOW_RUNNER" -v --dry-run --config-path "$BAD_CONFIG_FILE"' \
                 "Expect non-zero exit code for bad config: \"${config_file_basename}\" in verbose mode"

    assert_false '"$AUTONAMEOW_RUNNER" --debug --dry-run --config-path "$BAD_CONFIG_FILE"' \
                 "Expect non-zero exit code for bad config: \"${config_file_basename}\" in debug mode"

    assert_false '"$AUTONAMEOW_RUNNER" --quiet --dry-run --config-path "$BAD_CONFIG_FILE"' \
                 "Expect non-zero exit code for bad config: \"${config_file_basename}\" in quiet mode"

done < <(find "${AUTONAMEOW_TESTFILES_DIR}/configs" -maxdepth 1 -xdev -type f -name 'bad_0*.yaml' -print0 | sort -z)



# Calculate total execution time.
time_end="$(current_unix_time)"
total_time="$(calculate_execution_time "$time_start" "$time_end")"

log_test_suite_results_summary "$TESTSUITE_NAME" "$total_time"
