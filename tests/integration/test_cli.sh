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

if [ -z "${AUTONAMEOW_ROOT_DIR:-}" ]
then
    cat >&2 <<EOF

[ERROR] Integration test suites can no longer be run stand-alone.
        Please use use the designated integration test runner.

EOF
    exit 1
fi

# Resets test suite counter variables.
source "$AUTONAMEOW_ROOT_DIR/tests/integration/utils.sh"



# Test Cases
# ____________________________________________________________________________

# Store current time for later calculation of total execution time.
time_start="$(current_unix_time)"

TESTSUITE_NAME='Command-Line Interface'
logmsg "Running the ${TESTSUITE_NAME} test suite .."



assert_true 'command -v python3' \
            'Python v3.x is available on the system'

ACTIVE_CONFIG="$(abspath_testfile "configs/default.yaml")"
bulk_assert_test "$ACTIVE_CONFIG" n e f r

bulk_assert_test "$AUTONAMEOW_RUNNER" n e r x

assert_true '"$AUTONAMEOW_RUNNER"' \
            'The autonameow launcher script can be started with no arguments'

assert_true '"$AUTONAMEOW_RUNNER" 2>&1 | grep -- "--help"' \
            '[TC005] autonameow should print how to get help when started with no arguments'

assert_true '"$AUTONAMEOW_RUNNER" --help -- 2>&1 | head -n 1 | grep -- "Usage"' \
            '[TC005] autonameow should display usage information when started with "--help"'

assert_true '"$AUTONAMEOW_RUNNER" --help -- 2>&1 | grep -- "dry-run"' \
            '[TC001] autonameow should provide a "--dry-run" option'

assert_true '"$AUTONAMEOW_RUNNER" --help -- 2>&1 | grep -- "--interactive"' \
            '[TC013] autonameow should provide a "--interactive" option'

assert_true '"$AUTONAMEOW_RUNNER" --interactive -- ' \
            '[TC013] autonameow should return 0 when started with "--interactive" without specifying files'

assert_true '"$AUTONAMEOW_RUNNER" --interactive --verbose -- ' \
            '[TC013] autonameow should return 0 when started with "--interactive" and "--verbose" without specifying files'

assert_true '"$AUTONAMEOW_RUNNER" --interactive --debug -- ' \
            '[TC013] autonameow should return 0 when started with "--interactive" and "--debug" without specifying files'

assert_true '"$AUTONAMEOW_RUNNER" --automagic -- ' \
            'autonameow should return 0 when started with "--automagic" without specifying files'

assert_true '"$AUTONAMEOW_RUNNER" --automagic --verbose -- ' \
            'autonameow should return 0 when started with "--automagic" and "--verbose" without specifying files'

assert_true '"$AUTONAMEOW_RUNNER" --automagic --debug -- ' \
            'autonameow should return 0 when started with "--automagic" and "--debug" without specifying files'

assert_false '"$AUTONAMEOW_RUNNER" --verbose --debug -- ' \
             'Starting with mutually exclusive options "--verbose" and "--debug" should generate an error'

assert_false '"$AUTONAMEOW_RUNNER" --verbose --quiet -- ' \
             'Starting with mutually exclusive options "--verbose" and "--quiet" should generate an error'

assert_false '"$AUTONAMEOW_RUNNER" --debug --quiet -- ' \
             'Starting with mutually exclusive options "--debug" and "--quiet" should generate an error'

assert_false '"$AUTONAMEOW_RUNNER" --verbose 2>&1 | grep -- " :root:"' \
             'Output should not contain " :root:" when starting with "--verbose"'

assert_false '"$AUTONAMEOW_RUNNER" --verbose 2>&1 | grep -- ":root:"' \
             'Output should not contain ":root:" when starting with "--verbose"'

assert_false '"$AUTONAMEOW_RUNNER" --debug 2>&1 | grep -- " :root:"' \
             'Output should not contain " :root:" when starting with "--debug"'

assert_false '"$AUTONAMEOW_RUNNER" --debug 2>&1 | grep -- ":root:"' \
             'Output should not contain ":root:" when starting with "--debug"'


SAMPLE_EMPTY_FILE="$(abspath_testfile "empty")"
bulk_assert_test "$SAMPLE_EMPTY_FILE" e f r

assert_true '"$AUTONAMEOW_RUNNER" --batch --automagic --dry-run -- "$SAMPLE_EMPTY_FILE"' \
            'Expect exit status 0 when started with "--automagic", "--dry-run" and an empty file'

assert_true '"$AUTONAMEOW_RUNNER" --automagic --dry-run --verbose -- "$SAMPLE_EMPTY_FILE"' \
            'Expect exit status 0 when started with "--automagic", "--dry-run", "--verbose" and an empty file'

assert_true '"$AUTONAMEOW_RUNNER" --automagic --dry-run --debug -- "$SAMPLE_EMPTY_FILE"' \
            'Expect exit status 0 when started with "--automagic", "--dry-run", "--debug" and an empty file'


assert_true '"$AUTONAMEOW_RUNNER" --version' \
            'autonameow should return 0 when started with "--version"'

assert_true '"$AUTONAMEOW_RUNNER" --version --verbose' \
            'autonameow should return 0 when started with "--version" and "--verbose"'

assert_true '"$AUTONAMEOW_RUNNER" --version --debug' \
            'autonameow should return 0 when started with "--version" and "--debug"'

assert_true '"$AUTONAMEOW_RUNNER" --version --quiet' \
            'autonameow should return 0 when started with "--version" and "--quiet"'


SAMPLE_PDF_FILE="$(abspath_testfile "gmail.pdf")"
bulk_assert_test "$SAMPLE_PDF_FILE" e f r

sample_pdf_file_basename="$(basename -- "${SAMPLE_PDF_FILE}")"
assert_true '"$AUTONAMEOW_RUNNER" --config-path "$ACTIVE_CONFIG" --dry-run --list-all -- "$SAMPLE_PDF_FILE"' \
            "Expect exit code 0 when started with \"--dry-run --list-all\" given the file \"${sample_pdf_file_basename}\""

assert_true '"$AUTONAMEOW_RUNNER" --config-path "$ACTIVE_CONFIG" --list-all --dry-run --verbose -- "$SAMPLE_PDF_FILE" 2>/dev/null | grep -- "2016-01-11 12:41:32"' \
            "Output should include expected date when started with \"--list-all\" given the file \"${sample_pdf_file_basename}\""

assert_false '"$AUTONAMEOW_RUNNER" --list-all --dry-run --verbose -- "$SAMPLE_PDF_FILE" 2>&1 | grep -- " !!binary "' \
             "Output should not contain \" !!binary \" when running with \"--list-all\" given the file \"${sample_pdf_file_basename}\""

assert_false '"$AUTONAMEOW_RUNNER" --dump-config 2>&1 | grep -- " \!\!python/object:"' \
             'Output should not contain " !!python/object:" when running with "--dump-config"'


TEST_FILES_SUBDIR="$(abspath_testfile "subdir")"
bulk_assert_test "$TEST_FILES_SUBDIR" d r w x

assert_true '"$AUTONAMEOW_RUNNER" --batch --recurse --dry-run -- "$TEST_FILES_SUBDIR"' \
            "Expect exit code 0 when running \"--batch --recurse --dry-run -- \"${TEST_FILES_SUBDIR}\"\""

assert_true '"$AUTONAMEOW_RUNNER" --batch --verbose --recurse --dry-run -- "$TEST_FILES_SUBDIR" 2>&1 | grep -- ".*Got 8 files to process.*"' \
            "Expect output to contain \"Got 8 files to process\" when running \"--batch --verbose --recurse --dry-run -- ${TEST_FILES_SUBDIR}\""


# ______________________________________________________________________________
# Tests with the same input paths used more than once.

sample_empty_file_basename="$(basename -- "${SAMPLE_EMPTY_FILE}")"
sample_pdf_file_basename="$(basename -- "${SAMPLE_PDF_FILE}")"

assert_true '"$AUTONAMEOW_RUNNER" --dry-run --automagic -- "$SAMPLE_EMPTY_FILE"' \
            "Expect exit code 0 for \"--dry-run --automagic -- \"${sample_empty_file_basename}\"\""

assert_true '"$AUTONAMEOW_RUNNER" --dry-run --automagic -- "$SAMPLE_EMPTY_FILE" "$SAMPLE_EMPTY_FILE"' \
            "Expect exit code 0 for \"--dry-run --automagic -- \"${sample_empty_file_basename}\" \"${sample_empty_file_basename}\"\""

assert_true '"$AUTONAMEOW_RUNNER" --dry-run --automagic -- "$SAMPLE_EMPTY_FILE" "$SAMPLE_EMPTY_FILE" "$SAMPLE_EMPTY_FILE"' \
            "Expect exit code 0 for \"--dry-run --automagic -- \"${sample_empty_file_basename}\" \"${sample_empty_file_basename}\" \"${sample_empty_file_basename}\"\""

assert_true '"$AUTONAMEOW_RUNNER" --dry-run --automagic -- "$SAMPLE_PDF_FILE"' \
            "Expect exit code 0 for \"--dry-run --automagic -- \"${sample_pdf_file_basename}\"\""

assert_true '"$AUTONAMEOW_RUNNER" --dry-run --automagic -- "$SAMPLE_PDF_FILE" "$SAMPLE_PDF_FILE"' \
            "Expect exit code 0 for \"--dry-run --automagic -- \"${sample_pdf_file_basename}\" \"${sample_pdf_file_basename}\"\""

assert_true '"$AUTONAMEOW_RUNNER" --dry-run --automagic -- "$SAMPLE_PDF_FILE" "$SAMPLE_PDF_FILE" "$SAMPLE_PDF_FILE"' \
            "Expect exit code 0 for \"--dry-run --automagic -- \"${sample_pdf_file_basename}\" \"${sample_pdf_file_basename}\" \"${sample_pdf_file_basename}\"\""

assert_true '"$AUTONAMEOW_RUNNER" --dry-run --automagic -- "$SAMPLE_EMPTY_FILE" "$SAMPLE_PDF_FILE"' \
            "Expect exit code 0 for \"--dry-run --automagic -- \"${sample_empty_file_basename}\" \"${sample_pdf_file_basename}\"\""

assert_true '"$AUTONAMEOW_RUNNER" --dry-run --automagic -- "$SAMPLE_EMPTY_FILE" "$SAMPLE_PDF_FILE" "$SAMPLE_EMPTY_FILE"' \
            "Expect exit code 0 for \"--dry-run --automagic -- \"${sample_empty_file_basename}\" \"${sample_pdf_file_basename}\" \"${sample_empty_file_basename}\"\""

assert_true '"$AUTONAMEOW_RUNNER" --dry-run --automagic -- "$SAMPLE_EMPTY_FILE" "$SAMPLE_PDF_FILE" "$SAMPLE_EMPTY_FILE" "$SAMPLE_PDF_FILE"' \
            "Expect exit code 0 for \"--dry-run --automagic -- \"${sample_empty_file_basename}\" \"${sample_pdf_file_basename}\" \"${sample_empty_file_basename}\" \"${sample_pdf_file_basename}\"\""

assert_true '"$AUTONAMEOW_RUNNER" --dry-run --automagic -- "$SAMPLE_PDF_FILE" "$SAMPLE_EMPTY_FILE"' \
            "Expect exit code 0 for \"--dry-run --automagic -- \"${sample_pdf_file_basename}\" \"${sample_empty_file_basename}\"\""

assert_true '"$AUTONAMEOW_RUNNER" --dry-run --automagic -- "$SAMPLE_PDF_FILE" "$SAMPLE_EMPTY_FILE" "$SAMPLE_PDF_FILE"' \
            "Expect exit code 0 for \"--dry-run --automagic -- \"${sample_pdf_file_basename}\" \"${sample_empty_file_basename}\" \"${sample_pdf_file_basename}\"\""

assert_true '"$AUTONAMEOW_RUNNER" --dry-run --automagic -- "$SAMPLE_PDF_FILE" "$SAMPLE_EMPTY_FILE" "$SAMPLE_PDF_FILE" "$SAMPLE_EMPTY_FILE"' \
            "Expect exit code 0 for \"--dry-run --automagic -- \"${sample_pdf_file_basename}\" \"${sample_empty_file_basename}\" \"${sample_pdf_file_basename}\" \"${sample_empty_file_basename}\"\""



# Calculate total execution time.
time_end="$(current_unix_time)"
total_time="$(calculate_execution_time "$time_start" "$time_end")"

log_test_suite_results_summary "$TESTSUITE_NAME" "$total_time"
update_global_test_results
