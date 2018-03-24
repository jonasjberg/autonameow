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
source "$AUTONAMEOW_ROOT_DIR/tests/integration/utils.sh"



# Test Cases
# ____________________________________________________________________________

# Store current time for later calculation of total execution time.
time_start="$(current_unix_time)"

TESTSUITE_NAME='Stand-alone Extraction'
logmsg "Running the ${TESTSUITE_NAME} test suite .."



EXTRACT_RUNNER="${AUTONAMEOW_ROOT_DIR}/bin/meowxtract.sh"
assert_bulk_test "$EXTRACT_RUNNER" n e f r x

assert_true '"$EXTRACT_RUNNER"' \
            'The autonameow launcher script can be started with no arguments'

assert_true '"$EXTRACT_RUNNER" 2>&1 | grep -- "--help"' \
            'Stand-alone extraction should print how to get help when started with no arguments'

assert_true '"$EXTRACT_RUNNER" --help -- 2>&1 | head -n 1 | grep -i -- "Usage"' \
            'Stand-alone extraction should display usage information when started with "--help"'

assert_true '"$EXTRACT_RUNNER"' \
            'Stand-alone extraction should return 0 when started without specifying files'

assert_true '"$EXTRACT_RUNNER" --verbose' \
            'Stand-alone extraction should return 0 when started with "--verbose" without specifying files'

assert_true '"$EXTRACT_RUNNER" --debug' \
            'Stand-alone extraction should return 0 when started with "--debug" without specifying files'

assert_false '"$EXTRACT_RUNNER" --verbose --debug' \
             'Mutually exclusive options "--verbose" and "--debug" should generate an error'


# ______________________________________________________________________________
#
# Check that the log format is not garbled due to multiple logger roots (?)

assert_false '"$EXTRACT_RUNNER" 2>&1 | grep -- " :root:"' \
             'Output should not contain " :root:"'

assert_false '"$EXTRACT_RUNNER" 2>&1 | grep -- ":root:"' \
             'Output should not contain ":root:"'

assert_false '"$EXTRACT_RUNNER" --verbose 2>&1 | grep -- " :root:"' \
             'Output should not contain " :root:" when starting with "--verbose"'

assert_false '"$EXTRACT_RUNNER" --verbose 2>&1 | grep -- ":root:"' \
             'Output should not contain ":root:" when starting with "--verbose"'

assert_false '"$EXTRACT_RUNNER" --debug 2>&1 | grep -- " :root:"' \
             'Output should not contain " :root:" when starting with "--debug"'

assert_false '"$EXTRACT_RUNNER" --debug 2>&1 | grep -- ":root:"' \
             'Output should not contain ":root:" when starting with "--debug"'


# Test file to extract from.
SAMPLE_PDF_FILE="$(abspath_testfile "gmail.pdf")"
assert_bulk_test "$SAMPLE_PDF_FILE" e r

sample_pdf_file_basename="$(basename -- "${SAMPLE_PDF_FILE}")"


# ______________________________________________________________________________
#
# Smoke-test metadata extraction.

assert_true '"$EXTRACT_RUNNER" --metadata -- "$SAMPLE_PDF_FILE"' \
            "Expect exit code 0 when started with \"--metadata\" given the file \"${sample_pdf_file_basename}\""

assert_true '"$EXTRACT_RUNNER" --metadata --verbose -- "$SAMPLE_PDF_FILE"' \
            "Expect exit code 0 when started with \"--metadata --verbose\" given the file \"${sample_pdf_file_basename}\""

assert_true '"$EXTRACT_RUNNER" --metadata --debug -- "$SAMPLE_PDF_FILE"' \
            "Expect exit code 0 when started with \"--metadata --debug\" given the file \"${sample_pdf_file_basename}\""

# Metadata extraction with statistics.

assert_true '"$EXTRACT_RUNNER" --metadata --stats -- "$SAMPLE_PDF_FILE"' \
            "Expect exit code 0 when started with \"--metadata\" given the file \"${sample_pdf_file_basename}\""

assert_true '"$EXTRACT_RUNNER" --metadata --stats --verbose -- "$SAMPLE_PDF_FILE"' \
            "Expect exit code 0 when started with \"--metadata --stats --verbose\" given the file \"${sample_pdf_file_basename}\""

assert_true '"$EXTRACT_RUNNER" --metadata --stats --debug -- "$SAMPLE_PDF_FILE"' \
            "Expect exit code 0 when started with \"--metadata --stats --debug\" given the file \"${sample_pdf_file_basename}\""


# ______________________________________________________________________________
#
# Smoke-test text extraction.

assert_true '"$EXTRACT_RUNNER" --text -- "$SAMPLE_PDF_FILE"' \
            "Expect exit code 0 when started with \"--text\" given the file \"${sample_pdf_file_basename}\""

assert_true '"$EXTRACT_RUNNER" --text --verbose -- "$SAMPLE_PDF_FILE"' \
            "Expect exit code 0 when started with \"--text --verbose\" given the file \"${sample_pdf_file_basename}\""

assert_true '"$EXTRACT_RUNNER" --text --debug -- "$SAMPLE_PDF_FILE"' \
            "Expect exit code 0 when started with \"--text --debug\" given the file \"${sample_pdf_file_basename}\""

# Text extraction with statistics.

assert_true '"$EXTRACT_RUNNER" --text --stats -- "$SAMPLE_PDF_FILE"' \
            "Expect exit code 0 when started with \"--text --stats\" given the file \"${sample_pdf_file_basename}\""

assert_true '"$EXTRACT_RUNNER" --text --stats --verbose -- "$SAMPLE_PDF_FILE"' \
            "Expect exit code 0 when started with \"--text --stats --verbose\" given the file \"${sample_pdf_file_basename}\""

assert_true '"$EXTRACT_RUNNER" --text --stats --debug -- "$SAMPLE_PDF_FILE"' \
            "Expect exit code 0 when started with \"--text --stats --debug\" given the file \"${sample_pdf_file_basename}\""


# ______________________________________________________________________________
#
# Smoke-test combined metadata and text extraction.

assert_true '"$EXTRACT_RUNNER" --metadata --text -- "$SAMPLE_PDF_FILE"' \
            "Expect exit code 0 when started with \"--metadata --text\" given the file \"${sample_pdf_file_basename}\""

assert_true '"$EXTRACT_RUNNER" --metadata --text --verbose -- "$SAMPLE_PDF_FILE"' \
            "Expect exit code 0 when started with \"--metadata --text --verbose\" given the file \"${sample_pdf_file_basename}\""

assert_true '"$EXTRACT_RUNNER" --metadata --text --debug -- "$SAMPLE_PDF_FILE"' \
            "Expect exit code 0 when started with \"--metadata --text --debug\" given the file \"${sample_pdf_file_basename}\""

# Metadata and text extraction with statistics.

assert_true '"$EXTRACT_RUNNER" --metadata --text --stats -- "$SAMPLE_PDF_FILE"' \
            "Expect exit code 0 when started with \"--metadata --text --stats\" given the file \"${sample_pdf_file_basename}\""

assert_true '"$EXTRACT_RUNNER" --metadata --text --stats --verbose -- "$SAMPLE_PDF_FILE"' \
            "Expect exit code 0 when started with \"--metadata --text --stats --verbose\" given the file \"${sample_pdf_file_basename}\""

assert_true '"$EXTRACT_RUNNER" --metadata --text --stats --debug -- "$SAMPLE_PDF_FILE"' \
            "Expect exit code 0 when started with \"--metadata --text --stats --debug\" given the file \"${sample_pdf_file_basename}\""


# ______________________________________________________________________________
#
# Verify output of metadata extraction. Focus on values that are changed by coercers.

assert_true '"$EXTRACT_RUNNER" --metadata -- "$SAMPLE_PDF_FILE" | grep -- "extractor.metadata.exiftool.File:MIMEType\ \+application/pdf"' \
            "Expect metadata extracted from \"${sample_pdf_file_basename}\" to contain expected exiftool.File:MIMEType"

assert_true '"$EXTRACT_RUNNER" --metadata -- "$SAMPLE_PDF_FILE" | grep -- "extractor.metadata.exiftool.File:FileType\ \+PDF"' \
            "Expect metadata extracted from \"${sample_pdf_file_basename}\" to contain expected exiftool.File:FileType"

assert_true '"$EXTRACT_RUNNER" --metadata -- "$SAMPLE_PDF_FILE" | grep -- "extractor.metadata.exiftool.File:FileName\ .*gmail.pdf"' \
            "Expect metadata extracted from \"${sample_pdf_file_basename}\" to contain expected exiftool.File:FileName"

assert_true '"$EXTRACT_RUNNER" --metadata -- "$SAMPLE_PDF_FILE" | grep -- "extractor.metadata.exiftool.PDF:CreateDate\ \+2016-01-11 12:41:32+00:00"' \
            "Expect metadata extracted from \"${sample_pdf_file_basename}\" to contain expected exiftool.PDF:CreateDate"

assert_true '"$EXTRACT_RUNNER" --metadata -- "$SAMPLE_PDF_FILE" | grep -- "extractor.metadata.exiftool.PDF:ModifyDate\ \+2016-01-11 12:41:32+00:00"' \
            "Expect metadata extracted from \"${sample_pdf_file_basename}\" to contain expected exiftool.PDF:ModifyDate"


# ______________________________________________________________________________
#
# Verify output of text extraction.

assert_true '"$EXTRACT_RUNNER" --text -- "$SAMPLE_PDF_FILE" | grep -- "Fri, Jan 8, 2016 at 3:50 PM"' \
            "Expect text extracted from \"${sample_pdf_file_basename}\" to contain \"Fri, Jan 8, 2016 at 3:50 PM\""


# Test file to extract from.
SAMPLE_RTF_FILE="$(abspath_testfile "sample.rtf")"
assert_bulk_test "$SAMPLE_RTF_FILE" e r

sample_rtf_file_basename="$(basename -- "${SAMPLE_RTF_FILE}")"

assert_true '"$EXTRACT_RUNNER" --text -- "$SAMPLE_RTF_FILE" | grep -- "baz last line"' \
            "Expect text extracted from \"${sample_rtf_file_basename}\" to contain \"baz last line\""

SAMPLE_MD_FILE="$(abspath_testfile "sample.md")"
assert_bulk_test "$SAMPLE_MD_FILE" e r

sample_md_file_basename="$(basename -- "${SAMPLE_MD_FILE}")"

# From the MarkdownTextExtractor
assert_true '"$EXTRACT_RUNNER" --text -- "$SAMPLE_MD_FILE" | grep -- "ON MEOW"' \
            "Expect text extracted from \"${sample_md_file_basename}\" to contain \"ON MEOW\""

assert_true '"$EXTRACT_RUNNER" --text -- "$SAMPLE_MD_FILE" | grep -- "-   meow list"' \
            "Expect text extracted from \"${sample_md_file_basename}\" to contain \"-   meow list\""

# From the PlainTextExtractor
assert_true '"$EXTRACT_RUNNER" --text -- "$SAMPLE_MD_FILE" | grep -- "On Meow"' \
            "Expect text extracted from \"${sample_md_file_basename}\" to contain \"On Meow\""

assert_true '"$EXTRACT_RUNNER" --text -- "$SAMPLE_MD_FILE" | grep -- "* meow list"' \
            "Expect text extracted from \"${sample_md_file_basename}\" to contain \"* meow list\""




# Calculate total execution time.
time_end="$(current_unix_time)"
total_time="$(calculate_execution_time "$time_start" "$time_end")"

log_test_suite_results_summary "$TESTSUITE_NAME" "$total_time"
update_global_test_results
