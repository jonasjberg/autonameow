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

TESTSUITE_NAME='Command-Line Interface'
aw_utils.log_msg "Running the $TESTSUITE_NAME test suite .."



aw_utils.assert_true 'aw_utils.command_exists python3' \
            'Python v3.x is available on the system'

ACTIVE_CONFIG="$(aw_utils.samplefile_abspath "configs/default.yaml")"
aw_utils.assert_bulk_test "$ACTIVE_CONFIG" n e f r

aw_utils.assert_bulk_test "$AUTONAMEOW_RUNNER" n e r x

aw_utils.assert_true '"$AUTONAMEOW_RUNNER"' \
            'The autonameow launcher script can be started with no arguments'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" 2>&1 | grep -- "--help"' \
            '[TC005] autonameow should print how to get help when started with no arguments'


aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --help -- 2>&1 | head -n 1 | grep -- "Usage"' \
            '[TC005] autonameow should display usage information when started with "--help"'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --help -- 2>&1 | grep -- "dry-run"' \
            '[TC001] autonameow should provide a "--dry-run" option'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --help -- 2>&1 | grep -- "--interactive"' \
            '[TC013] autonameow should provide a "--interactive" option'


# ______________________________________________________________________________
#
# Check exit codes for trivival use-cases.

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --interactive -- ' \
            '[TC013] autonameow should return 0 when started with "--interactive" without specifying files'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --interactive --verbose -- ' \
            '[TC013] autonameow should return 0 when started with "--interactive" and "--verbose" without specifying files'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --interactive --debug -- ' \
            '[TC013] autonameow should return 0 when started with "--interactive" and "--debug" without specifying files'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --automagic -- ' \
            'autonameow should return 0 when started with "--automagic" without specifying files'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --automagic --verbose -- ' \
            'autonameow should return 0 when started with "--automagic" and "--verbose" without specifying files'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --automagic --debug -- ' \
            'autonameow should return 0 when started with "--automagic" and "--debug" without specifying files'

aw_utils.assert_false '"$AUTONAMEOW_RUNNER" --verbose --debug -- ' \
             'Starting with mutually exclusive options "--verbose" and "--debug" should generate an error'

aw_utils.assert_false '"$AUTONAMEOW_RUNNER" --verbose --quiet -- ' \
             'Starting with mutually exclusive options "--verbose" and "--quiet" should generate an error'

aw_utils.assert_false '"$AUTONAMEOW_RUNNER" --debug --quiet -- ' \
             'Starting with mutually exclusive options "--debug" and "--quiet" should generate an error'


SAMPLE_EMPTY_FILE="$(aw_utils.samplefile_abspath "empty")"
aw_utils.assert_bulk_test "$SAMPLE_EMPTY_FILE" e f r

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --batch --automagic --dry-run -- "$SAMPLE_EMPTY_FILE"' \
            'Expect exit status 0 when started with "--automagic", "--dry-run" and an empty file'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --automagic --dry-run --verbose -- "$SAMPLE_EMPTY_FILE"' \
            'Expect exit status 0 when started with "--automagic", "--dry-run", "--verbose" and an empty file'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --automagic --dry-run --debug -- "$SAMPLE_EMPTY_FILE"' \
            'Expect exit status 0 when started with "--automagic", "--dry-run", "--debug" and an empty file'


aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --version' \
            'autonameow should return 0 when started with "--version"'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --version --verbose' \
            'autonameow should return 0 when started with "--version" and "--verbose"'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --version --debug' \
            'autonameow should return 0 when started with "--version" and "--debug"'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --version --quiet' \
            'autonameow should return 0 when started with "--version" and "--quiet"'


# ______________________________________________________________________________
#
# Check that the log format is not garbled due to multiple logger roots (?)

aw_utils.assert_false '"$AUTONAMEOW_RUNNER" --verbose 2>&1 | grep -- " :root:"' \
             'Output should not contain " :root:" when starting with "--verbose"'

aw_utils.assert_false '"$AUTONAMEOW_RUNNER" --verbose 2>&1 | grep -- ":root:"' \
             'Output should not contain ":root:" when starting with "--verbose"'

aw_utils.assert_false '"$AUTONAMEOW_RUNNER" --debug 2>&1 | grep -- " :root:"' \
             'Output should not contain " :root:" when starting with "--debug"'

aw_utils.assert_false '"$AUTONAMEOW_RUNNER" --debug 2>&1 | grep -- ":root:"' \
             'Output should not contain ":root:" when starting with "--debug"'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" -v | grep -- "^Started at 20.*"' \
            'When started with "-v" the output should match "^Started at 20.*"'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" -v | grep -Eo -- "^Started at [0-9]{4}-[01][0-9]-[0-3][0-9] [0-2][0-9]:[0-5][0-9]:[0-5][0-9] by .*"' \
            'When started with "-v" the output should match a more specific pattern "^Started at ISO_DATE_AND_TIME by .*"'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" -v | grep -- "^Finished at 20.*"' \
            'When started with "-v" the output should match "^Finished at 20.*"'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" -v | grep -Eo -- "^Finished at [0-9]{4}-[01][0-9]-[0-3][0-9] [0-2][0-9]:[0-5][0-9]:[0-5][0-9] after .* seconds with exit code [0-9]+$"' \
            'When started with "-v" the output should match a more specific pattern "^Finished at ISO_DATE_AND_TIME after .* seconds with exit code NUMBER"'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" -v 2>&1 | grep -- ".*Using configuration: .*"' \
            'When started with "-v" the output should match ".*Using configuration.*"'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" -v 2>&1 | grep -- ".*No input files specified.*"' \
            'When started with "-v" the output should match ".*No input files specified.*"'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" -v 2>&1 | grep -- ".*No input files specified.*"' \
            'When started without options the output should match ".*No input files specified.*"'


SAMPLE_PDF_FILE="$(aw_utils.samplefile_abspath "gmail.pdf")"
aw_utils.assert_bulk_test "$SAMPLE_PDF_FILE" e f r

sample_pdf_file_basename="$(basename -- "$SAMPLE_PDF_FILE")"
aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --config-path "$ACTIVE_CONFIG" --dry-run --list-all -- "$SAMPLE_PDF_FILE"' \
            "Expect exit code 0 when started with \"--dry-run --list-all\" given the file \"${sample_pdf_file_basename}\""

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --config-path "$ACTIVE_CONFIG" --list-all --dry-run --verbose -- "$SAMPLE_PDF_FILE" 2>/dev/null | grep -- "2016-01-11 12:41:32"' \
            "Output should include expected date when started with \"--list-all\" given the file \"${sample_pdf_file_basename}\""

aw_utils.assert_false '"$AUTONAMEOW_RUNNER" --list-all --dry-run --verbose -- "$SAMPLE_PDF_FILE" 2>&1 | grep -- " !!binary "' \
             "Output should not contain \" !!binary \" when running with \"--list-all\" given the file \"${sample_pdf_file_basename}\""

# aw_utils.assert_false '"$AUTONAMEOW_RUNNER" --dump-config 2>&1 | grep -- " \!\!python/object:"' \
#              '[TD0148] Output should not contain " !!python/object:" when running with "--dump-config"'


# ______________________________________________________________________________
#
# Tests the recursive option.

SAMPLE_SUBDIR="$(aw_utils.samplefile_abspath "subdir")"
aw_utils.assert_bulk_test "$SAMPLE_SUBDIR" d r w x

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --batch --recurse --dry-run -- "$SAMPLE_SUBDIR"' \
            "Expect exit code 0 when running \"--batch --recurse --dry-run -- \"${SAMPLE_SUBDIR}\"\""

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --batch --verbose --recurse --dry-run -- "$SAMPLE_SUBDIR" 2>&1 | grep -- ".*Got 8 files to process.*"' \
            "Expect output to contain \"Got 8 files to process\" when running \"--batch --verbose --recurse --dry-run -- ${SAMPLE_SUBDIR}\""


# ______________________________________________________________________________
# Tests with the same input paths used more than once.

sample_empty_file_basename="$(basename -- "$SAMPLE_EMPTY_FILE")"
sample_pdf_file_basename="$(basename -- "$SAMPLE_PDF_FILE")"

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --dry-run --automagic -- "$SAMPLE_EMPTY_FILE"' \
            "Expect exit code 0 for \"--dry-run --automagic -- \"${sample_empty_file_basename}\"\""

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --dry-run --automagic -- "$SAMPLE_EMPTY_FILE" "$SAMPLE_EMPTY_FILE"' \
            "Expect exit code 0 for \"--dry-run --automagic -- \"${sample_empty_file_basename}\" \"${sample_empty_file_basename}\"\""

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --dry-run --automagic -- "$SAMPLE_EMPTY_FILE" "$SAMPLE_EMPTY_FILE" "$SAMPLE_EMPTY_FILE"' \
            "Expect exit code 0 for \"--dry-run --automagic -- \"${sample_empty_file_basename}\" \"${sample_empty_file_basename}\" \"${sample_empty_file_basename}\"\""

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --dry-run --automagic -- "$SAMPLE_PDF_FILE"' \
            "Expect exit code 0 for \"--dry-run --automagic -- \"${sample_pdf_file_basename}\"\""

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --dry-run --automagic -- "$SAMPLE_PDF_FILE" "$SAMPLE_PDF_FILE"' \
            "Expect exit code 0 for \"--dry-run --automagic -- \"${sample_pdf_file_basename}\" \"${sample_pdf_file_basename}\"\""

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --dry-run --automagic -- "$SAMPLE_PDF_FILE" "$SAMPLE_PDF_FILE" "$SAMPLE_PDF_FILE"' \
            "Expect exit code 0 for \"--dry-run --automagic -- \"${sample_pdf_file_basename}\" \"${sample_pdf_file_basename}\" \"${sample_pdf_file_basename}\"\""

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --dry-run --automagic -- "$SAMPLE_EMPTY_FILE" "$SAMPLE_PDF_FILE"' \
            "Expect exit code 0 for \"--dry-run --automagic -- \"${sample_empty_file_basename}\" \"${sample_pdf_file_basename}\"\""

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --dry-run --automagic -- "$SAMPLE_EMPTY_FILE" "$SAMPLE_PDF_FILE" "$SAMPLE_EMPTY_FILE"' \
            "Expect exit code 0 for \"--dry-run --automagic -- \"${sample_empty_file_basename}\" \"${sample_pdf_file_basename}\" \"${sample_empty_file_basename}\"\""

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --dry-run --automagic -- "$SAMPLE_EMPTY_FILE" "$SAMPLE_PDF_FILE" "$SAMPLE_EMPTY_FILE" "$SAMPLE_PDF_FILE"' \
            "Expect exit code 0 for \"--dry-run --automagic -- \"${sample_empty_file_basename}\" \"${sample_pdf_file_basename}\" \"${sample_empty_file_basename}\" \"${sample_pdf_file_basename}\"\""

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --dry-run --automagic -- "$SAMPLE_PDF_FILE" "$SAMPLE_EMPTY_FILE"' \
            "Expect exit code 0 for \"--dry-run --automagic -- \"${sample_pdf_file_basename}\" \"${sample_empty_file_basename}\"\""

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --dry-run --automagic -- "$SAMPLE_PDF_FILE" "$SAMPLE_EMPTY_FILE" "$SAMPLE_PDF_FILE"' \
            "Expect exit code 0 for \"--dry-run --automagic -- \"${sample_pdf_file_basename}\" \"${sample_empty_file_basename}\" \"${sample_pdf_file_basename}\"\""

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --dry-run --automagic -- "$SAMPLE_PDF_FILE" "$SAMPLE_EMPTY_FILE" "$SAMPLE_PDF_FILE" "$SAMPLE_EMPTY_FILE"' \
            "Expect exit code 0 for \"--dry-run --automagic -- \"${sample_pdf_file_basename}\" \"${sample_empty_file_basename}\" \"${sample_pdf_file_basename}\" \"${sample_empty_file_basename}\"\""


# ______________________________________________________________________________
#
# Check the '--dump-meowuris' option.

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --help 2>&1 | grep -- "--dump-meowuris"' \
            'Help text includes the "--dump-meowuris" option'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --dump-meowuris' \
            'Expect exit code 0 for "--dump-meowuris"'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --dump-meowuris --debug' \
            'Expect exit code 0 for "--dump-meowuris --debug"'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --dump-meowuris --verbose' \
            'Expect exit code 0 for "--dump-meowuris --verbose"'


# ______________________________________________________________________________
#
# Check the '--dump-config' option.

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --dump-config' \
            'Expect exit code 0 for "--dump-config"'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --dump-config --debug' \
            'Expect exit code 0 for "--dump-config --debug"'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --dump-config --verbose' \
            'Expect exit code 0 for "--dump-config --verbose"'


# ______________________________________________________________________________
#
# Check the '--postprocess-only' option.

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --help 2>&1 | grep -- "--postprocess-only"' \
            'Help text includes the "--postprocess-only" option'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --postprocess-only' \
            'Expect exit code 0 for "--postprocess-only"'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --postprocess-only --debug' \
            'Expect exit code 0 for "--postprocess-only --debug"'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --postprocess-only --verbose' \
            'Expect exit code 0 for "--postprocess-only --verbose"'




# Calculate total execution time.
time_end="$(aw_utils.current_unix_time)"
total_time="$(aw_utils.calculate_execution_time "$time_start" "$time_end")"

aw_utils.log_test_suite_results_summary "$TESTSUITE_NAME" "$total_time"
aw_utils.update_global_test_results
