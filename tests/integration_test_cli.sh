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

assert_true '( "$AUTONAMEOW_RUNNER" 2>&1 ) >/dev/null' \
            "The autonameow launcher script can be started with no arguments"

assert_true '( "$AUTONAMEOW_RUNNER" 2>&1 | grep -q -- "--help" ) >/dev/null' \
            "[TC005] autonameow should print how to get help when started with no arguments"

assert_true '( "$AUTONAMEOW_RUNNER" --help -- 2>&1 | head -n 1 | grep -q -- "usage" ) >/dev/null' \
            "[TC005] autonameow should display usage information when started with \"--help\""

assert_true '( "$AUTONAMEOW_RUNNER" --help -- 2>&1 | grep -q -- "dry-run" ) >/dev/null' \
            "[TC001] autonameow should provide a \"--dry-run\" option"

assert_true '( "$AUTONAMEOW_RUNNER" --help -- 2>&1 | grep -q -- "--interactive" ) >/dev/null' \
            "[TC013] autonameow should provide a \"--interactive\" option"

assert_true '( "$AUTONAMEOW_RUNNER" --interactive -- 2>&1 ) >/dev/null' \
            "[TC013] autonameow should return zero when started with \"--interactive\" without specifying files"

assert_true '( "$AUTONAMEOW_RUNNER" --interactive --verbose -- 2>&1 ) >/dev/null' \
            "[TC013] autonameow should return zero when started with \"--interactive\" and \"--verbose\" without specifying files"

assert_true '( "$AUTONAMEOW_RUNNER" --interactive --debug -- 2>&1 ) >/dev/null' \
            "[TC013] autonameow should return zero when started with \"--interactive\" and \"--debug\" without specifying files"

assert_true '( "$AUTONAMEOW_RUNNER" --automagic -- 2>&1 ) >/dev/null' \
            "autonameow should return zero when started with \"--automagic\" without specifying files"

assert_true '( "$AUTONAMEOW_RUNNER" --automagic --verbose -- 2>&1 ) >/dev/null' \
            "autonameow should return zero when started with \"--automagic\" and \"--verbose\" without specifying files"

assert_true '( "$AUTONAMEOW_RUNNER" --automagic --debug -- 2>&1 ) >/dev/null' \
            "autonameow should return zero when started with \"--automagic\" and \"--debug\" without specifying files"

assert_false '( "$AUTONAMEOW_RUNNER" --verbose --debug -- 2>&1 ) >/dev/null' \
             "Starting with mutually exclusive options \"--verbose\" and \"--debug\" should generate an error"

assert_false '( "$AUTONAMEOW_RUNNER" --verbose --quiet -- 2>&1 ) >/dev/null' \
             "Starting with mutually exclusive options \"--verbose\" and \"--quiet\" should generate an error"

assert_false '( "$AUTONAMEOW_RUNNER" --debug --quiet -- 2>&1 ) >/dev/null' \
             "Starting with mutually exclusive options \"--debug\" and \"--quiet\" should generate an error"


SAMPLE_JPG_FILE="$( ( cd "$SELF_DIR" && realpath -e "../test_files/smulan.jpg" ) )"
assert_true '[ -e "$SAMPLE_JPG_FILE" ]' \
            "The test sample jpg file exists. Add suitable test file if this test fails!"

assert_true '( "$AUTONAMEOW_RUNNER" --automagic --dry-run -- "$SAMPLE_JPG_FILE" 2>&1 ) >/dev/null' \
            "[TC011][TC001] autonameow should return zero when started with \"--automagic\", \"--dry-run\" and a valid file"

assert_true '( "$AUTONAMEOW_RUNNER" --automagic --dry-run --verbose -- "$SAMPLE_JPG_FILE" 2>&1 ) >/dev/null' \
            "[TC011][TC001] autonameow should return zero when started with \"--automagic\", \"--dry-run\", \"--verbose\" and a valid file"

assert_true '( "$AUTONAMEOW_RUNNER" --automagic --dry-run --debug -- "$SAMPLE_JPG_FILE" 2>&1 ) >/dev/null' \
            "[TC011][TC001] autonameow should return zero when started with \"--automagic\", \"--dry-run\", \"--debug\" and a valid file"

SAMPLE_JPG_FILE_EXPECTED='2010-01-31T161251 a cat lying on a rug.jpg'
# NOTE(jonas): Fix encoding issues! This PASSES on MacOS:
assert_true '( "$AUTONAMEOW_RUNNER" --automagic --dry-run --verbose -- "$SAMPLE_JPG_FILE" 2>/dev/null ) | col -b | grep -q -- "2010-01-31T161251 a cat lying on a rug.jpg"' \
            "Automagic mode output should include \"${SAMPLE_JPG_FILE_EXPECTED}\" given the file \""$(basename -- "${SAMPLE_JPG_FILE}")"\" (expect PASSED on MacOS)"

# NOTE(jonas): Fix encoding issues! This FAILS on MacOS:
assert_true '( "$AUTONAMEOW_RUNNER" --automagic --dry-run --verbose -- "$SAMPLE_JPG_FILE" 2>/dev/null ) | col -b | grep -q -- "2010-01-31T161251 a cat lying on a rug.jpg"' \
            "Automagic mode output should include \"${SAMPLE_JPG_FILE_EXPECTED}\" given the file \""$(basename -- "${SAMPLE_JPG_FILE}")"\" (expect FAILED os MacOS)"


_temp_dir="$(mktemp -d)"
_expected_name="${_temp_dir}/2010-01-31T161251 a cat lying on a rug.jpg"
assert_true 'cp -n -- "$SAMPLE_JPG_FILE" ${_temp_dir}/smulan.jpg 2>&1 >/dev/null' \
            "rename_sample_jpg_file Test setup should succeed"

assert_true '( "$AUTONAMEOW_RUNNER" --automagic -- "${_temp_dir}/smulan.jpg" 2>&1 ) >/dev/null && [ -e "$_expected_name" ]' \
            "rename_sample_jpg_file [TC010][TC011] \""$(basename -- "${SAMPLE_JPG_FILE}")"\" should be renamed to \""$(basename -- "${_expected_name}")"\""

assert_true '[ -f "${_temp_dir}/smulan.jpg" ] && rm -- "${_temp_dir}/smulan.jpg" ; [ -f "$_expected_name" ] && rm -- "$_expected_name" || true' \
            "rename_sample_jpg_file Test teardown should succeed"


assert_true '( "$AUTONAMEOW_RUNNER" --version 2>&1 ) >/dev/null' \
            "autonameow should return zero when started with \"--version\""

assert_true '( "$AUTONAMEOW_RUNNER" --version --verbose 2>&1 ) >/dev/null' \
            "autonameow should return zero when started with \"--version\" and \"--verbose\""

assert_true '( "$AUTONAMEOW_RUNNER" --version --debug 2>&1 ) >/dev/null' \
            "autonameow should return zero when started with \"--version\" and \"--debug\""

assert_true '( "$AUTONAMEOW_RUNNER" --version --quiet 2>&1 ) >/dev/null' \
            "autonameow should return zero when started with \"--version\" and \"--quiet\""


SAMPLE_PDF_FILE="$( ( cd "$SELF_DIR" && realpath -e "../test_files/gmail.pdf" ) )"
assert_true '[ -e "$SAMPLE_PDF_FILE" ]' \
            "The test sample pdf file exists. Add suitable test file if this test fails!"

set +o pipefail
assert_true '( "$AUTONAMEOW_RUNNER" --automagic --dry-run --verbose -- "$SAMPLE_PDF_FILE" 2>&1 | grep -q -- "Using file rule: \"test_files Gmail print-to-pdf\"" ) >/dev/null' \
            "[TC014] autonameow should choose file rule \"test_files Gmail print-to-pdf\" given the file \""$(basename -- "${SAMPLE_PDF_FILE}")"\""

assert_false '( "$AUTONAMEOW_RUNNER" --automagic --dry-run --verbose -- "$SAMPLE_JPG_FILE" 2>&1 | grep -q -- "Using file rule: \"test_files Gmail print-to-pdf\"" ) >/dev/null' \
             "[TC014] autonameow should NOT choose file rule \"test_files Gmail print-to-pdf\" given the file \""$(basename -- "${SAMPLE_JPG_FILE}")"\""

assert_true '( "$AUTONAMEOW_RUNNER" --automagic --dry-run --verbose -- "$SAMPLE_JPG_FILE" 2>&1 | grep -q -- "Using file rule: \"test_files smulan.jpg\"" ) >/dev/null' \
            "[TC014] autonameow should choose file rule \"test_files smulan.jpg\" given the file \""$(basename -- "${SAMPLE_JPG_FILE}")"\""

assert_false '( "$AUTONAMEOW_RUNNER" --automagic --dry-run --verbose -- "$SAMPLE_PDF_FILE" 2>&1 | grep -q -- "Using file rule: \"test_files smulan.jpg\"" ) >/dev/null' \
             "[TC014] autonameow should NOT choose file rule \"test_files smulan.jpg\" given the file \""$(basename -- "${SAMPLE_PDF_FILE}")"\""
set -o pipefail

assert_true '( "$AUTONAMEOW_RUNNER" --list-datetime --verbose -- "$SAMPLE_PDF_FILE" 2>&1 ) >/dev/null' \
            "Expect exit code 0 when started with \"--list-datetime\" given the file \""$(basename -- "${SAMPLE_PDF_FILE}")"\""

assert_true '( "$AUTONAMEOW_RUNNER" --list-datetime --verbose -- "$SAMPLE_PDF_FILE" 2>/dev/null ) | col -b | grep -q -- "2016-01-11 12:41:32" 2>&1 >/dev/null' \
            "Output should contain expected date when started with \"--list-datetime\" given the file \""$(basename -- "${SAMPLE_PDF_FILE}")"\""

assert_true '( "$AUTONAMEOW_RUNNER" --list-all -- "$SAMPLE_PDF_FILE" 2>&1 ) >/dev/null' \
            "Expect exit code 0 when started with \"--list-all\" given the file \""$(basename -- "${SAMPLE_PDF_FILE}")"\""

assert_true '( "$AUTONAMEOW_RUNNER" --list-all --dry-run --verbose -- "$SAMPLE_PDF_FILE" 2>/dev/null | col -b | grep -q -- "2016-01-11 12:41:32" 2>&1 ) >/dev/null' \
            "Output should include expected date when started with \"--list-all\" given the file \""$(basename -- "${SAMPLE_PDF_FILE}")"\""

assert_true '( "$AUTONAMEOW_RUNNER" --list-title -- "$SAMPLE_PDF_FILE" 2>&1 ) >/dev/null' \
            "Expect exit code 0 when started with \"--list-title\" given the file \""$(basename -- "${SAMPLE_PDF_FILE}")"\""

# NOTE(jonas): Fix encoding issues! This FAILS on MacOS:
SAMPLE_PDF_FILE_EXPECTED='2016-01-11T124132 gmail.pdf'
assert_true '( "$AUTONAMEOW_RUNNER" --automagic --dry-run -- "$SAMPLE_PDF_FILE" 2>&1 ) | col -b | grep -q -- "${SAMPLE_PDF_FILE_EXPECTED}"' \
            "Automagic mode output should include \"${SAMPLE_PDF_FILE_EXPECTED}\" given the file \""$(basename -- "${SAMPLE_PDF_FILE}")"\" (expect FAILED os MacOS)"

# NOTE(jonas): Fix encoding issues! This PASSES on MacOS:
SAMPLE_PDF_FILE_EXPECTED_MACOS='2016-01-11T124132 gmail.pdf'
assert_true '( "$AUTONAMEOW_RUNNER" --automagic --dry-run -- "$SAMPLE_PDF_FILE" 2>&1 ) | col -b | grep -q -- "${SAMPLE_PDF_FILE_EXPECTED_MACOS}"' \
            "Automagic mode output should include \"${SAMPLE_PDF_FILE_EXPECTED_MACOS}\" given the file \""$(basename -- "${SAMPLE_PDF_FILE}")"\" (expect PASSED on MacOS)"


EMPTY_CONFIG='/tmp/autonameow_empty_config.yaml'
assert_true 'touch "$EMPTY_CONFIG" 2>&1 >/dev/null' \
            "detect_empty_config Test setup should succeed"

assert_false '( "$AUTONAMEOW_RUNNER" --config-path "$EMPTY_CONFIG" 2>&1 ) >/dev/null' \
             "detect_empty_config Specifying a empty configuration file with \"--config-path\" should be handled properly"

assert_true '[ -f "$EMPTY_CONFIG" ] && rm -- "$EMPTY_CONFIG" 2>&1 >/dev/null' \
            "detect_empty_config Test teardown should succeed"

assert_false '( "$AUTONAMEOW_RUNNER" --config-path /tmp/does_not_exist_surely.mjao 2>&1 ) >/dev/null' \
             "Specifying an invalid path with \"--config-path\" should be handled properly"


BAD_CONFIG_FILE="$( ( cd "$SELF_DIR" && realpath -e "../test_files/bad_config.yaml" ) )"
assert_true '[ -e "$BAD_CONFIG_FILE" ]' \
            "A known bad configuration file exists. Add suitable test file if this test fails!"

assert_false '( "$AUTONAMEOW_RUNNER" --config-path "$BAD_CONFIG_FILE" 2>&1 ) >/dev/null' \
             "Attempting to load a invalid configuration file with \"--config-path\" should be handled properly"


assert_true '( "$AUTONAMEOW_RUNNER" --dump-options --verbose 2>&1 ) >/dev/null' \
            "autonameow should return zero when started with \"--dump-options\" and \"--verbose\""


NONASCII_CONFIG_FILE="$( ( cd "$SELF_DIR" && realpath -e "../test_files/autonam€öw.yaml" ) )"
assert_true '[ -e "$NONASCII_CONFIG_FILE" ]' \
            "A non-ASCII configuration file exists. Add suitable test file if this test fails!"

assert_true '( "$AUTONAMEOW_RUNNER" --config-path "$NONASCII_CONFIG_FILE" 2>&1 ) >/dev/null' \
             "Attempting to load a non-ASCII configuration file with \"--config-path\" should be handled properly"

assert_true '( "$AUTONAMEOW_RUNNER" --verbose --config-path "$NONASCII_CONFIG_FILE" 2>&1 ) >/dev/null' \
             "Expect exit code 0 for non-ASCII configuration file and \"--verbose\""

assert_true '( "$AUTONAMEOW_RUNNER" --debug --config-path "$NONASCII_CONFIG_FILE" 2>&1 ) >/dev/null' \
             "Expect exit code 0 for non-ASCII configuration file and \"--debug\""

assert_true '( "$AUTONAMEOW_RUNNER" --quiet --config-path "$NONASCII_CONFIG_FILE" 2>&1 ) >/dev/null' \
             "Expect exit code 0 for non-ASCII configuration file and \"--quiet\""

assert_true '( "$AUTONAMEOW_RUNNER" --dump-options --config-path "$NONASCII_CONFIG_FILE" 2>&1 ) >/dev/null' \
             "Expect exit code 0 for non-ASCII configuration file and \"--dump-options\""

assert_true '( "$AUTONAMEOW_RUNNER" --dump-options --verbose --config-path "$NONASCII_CONFIG_FILE" 2>&1 ) >/dev/null' \
             "Expect exit code 0 for non-ASCII configuration file and \"--dump-options\", \"--verbose\""

assert_true '( "$AUTONAMEOW_RUNNER" --dump-options --debug --config-path "$NONASCII_CONFIG_FILE" 2>&1 ) >/dev/null' \
             "Expect exit code 0 for non-ASCII configuration file and \"--dump-options\", \"--debug\""

assert_true '( "$AUTONAMEOW_RUNNER" --dump-options --quiet --config-path "$NONASCII_CONFIG_FILE" 2>&1 ) >/dev/null' \
             "Expect exit code 0 for non-ASCII configuration file and \"--dump-options\", \"--quiet\""


TEST_FILES_SUBDIR="$( ( cd "$SELF_DIR" && realpath -e "../test_files/subdir" ) )"
assert_true '[ -d "$TEST_FILES_SUBDIR" ]' \
            "The \"test_files/subdir\" directory exists. Add suitable test files if this test fails!"

assert_true '( "$AUTONAMEOW_RUNNER" --recurse --dry-run -- "$TEST_FILES_SUBDIR" 2>&1 ) >/dev/null' \
            "Expect exit code 0 when running \"--recurse --dry-run -- "$TEST_FILES_SUBDIR"\""

assert_true '( "$AUTONAMEOW_RUNNER" --verbose --recurse --dry-run -- "$TEST_FILES_SUBDIR" 2>&1 ) | col -b | grep -q ".*Got 8 files to process.*"' \
            "Expect output to contain \"Got 8 files to process\" when running \"--verbose --recurse --dry-run -- "$TEST_FILES_SUBDIR"\""


BAD_CONFIG_FILE_NO_FILE_RULES="$( ( cd "$SELF_DIR" && realpath -e "../test_files/bad_config_no_file_rules.yaml" ) )"
assert_true '[ -e "$BAD_CONFIG_FILE_NO_FILE_RULES" ]' \
            "A test configuration file without file rules exists. Add suitable test file if this test fails!"

assert_false '( "$AUTONAMEOW_RUNNER" --config-path "$BAD_CONFIG_FILE_NO_FILE_RULES" 2>&1 ) >/dev/null' \
             "Attempting to load a configuration file without any file rules should be handled properly"



# Calculate total execution time.
time_end="$(current_unix_time)"
total_time="$((($time_end - $time_start) / 1000000))"

calculate_statistics
logmsg "Completed the Command-Line Interface test suite tests in ${total_time} ms"
