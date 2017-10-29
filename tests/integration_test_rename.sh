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
TESTSUITE_NAME='Rename Files'

# Source 'integration_utils.sh', which in turn sources 'common_utils.sh'.
if ! source "${SELF_DIR}/integration_utils.sh"
then
    echo "Integration test utility library is missing. Aborting .." 1>&2
    exit 1
fi


# A sample file is copied to a temporary directory, autonameow is then started
# with the "--automagic" option, which should rename the temporary file.
# After running the program, the temporary directory should contain the
# expected base name.  Finally, the used files are deleted.
# Arguments:
# 1. A name for this group of tests.
# 2. Full path to the sample file to be copied to a temporary directory.
# 3. The expected basename of the file after having been renamed.
test_automagic_rename()
{
    local _test_name="RENAME ${1}"
    local _sample_file="$2"
    local _expected_basename="$3"

    local _sample_file_basename="$(basename -- "${_sample_file}")"
    local _temp_dir="$(mktemp -d)"
    local _expected_name="${_temp_dir}/${_expected_basename}"
    local _temp_file="${_temp_dir}/${_sample_file_basename}"

    assert_true 'cp -n -- "${_sample_file}" "${_temp_file}"' \
                "(${_test_name}) Test setup should succeed in copying the sample file to a temporary directory"

    assert_true '[ -f "${_temp_file}" ]' \
                "(${_test_name}) A copy of the sample file must exit in the temporary directory"

    if ! [ -f "${_temp_file}" ]
    then
        assert_true '[ "1" -eq "0" ]' \
        "(${_test_name}) Test setup FAILED. Unable to continue. Skipping remaining tests .."
        return -1
    fi

    assert_true '"$AUTONAMEOW_RUNNER" --batch --config-path "$ACTIVE_CONFIG" --automagic -- "${_temp_file}" && [ -e "$_expected_name" ]' \
                "(${_test_name}) Should be renamed to \"${_expected_basename}\""

    assert_true '[ -f "${_temp_file}" ] && rm -- "${_temp_file}" ; [ -f "$_expected_name" ] && rm -- "$_expected_name" || true' \
                "(${_test_name}) Test teardown should succeed in deleting temporary files"
}

# Tests autonameow using command-line options "--automagic --dry-run".
# The program output is searched for the expected file name.
# The given sample file should NOT be renamed.
# Arguments:
# 1. A name for this group of tests.
# 2. Full path to the sample file to be copied to a temporary directory.
# 3. The expected basename of the file after having been renamed.
test_automagic_dryrun()
{
    local _test_name="DRY-RUN ${1}"
    local _sample_file="$2"
    local _expected_basename="$3"

    if ! [ -f "${_sample_file}" ]
    then
        assert_true '[ "1" -eq "0" ]' \
        "(${_test_name}) Test setup FAILED. Unable to continue. Skipping remaining tests .."
        return -1
    fi

    assert_true '"$AUTONAMEOW_RUNNER" --batch --config-path "$ACTIVE_CONFIG" --automagic --dry-run -- "${_sample_file}"' \
                "(${_test_name}) Expect exit code 0 when started with \"--automagic --dry-run\""

    assert_true '"$AUTONAMEOW_RUNNER" --batch --config-path "$ACTIVE_CONFIG" --automagic --dry-run --verbose -- "${_sample_file}"' \
                "(${_test_name}) Expect exit code 0 when started with \"--automagic --dry-run --verbose\""

    assert_true '"$AUTONAMEOW_RUNNER" --batch --config-path "$ACTIVE_CONFIG" --automagic --dry-run --debug -- "${_sample_file}"' \
                "(${_test_name}) Expect exit code 0 when started with \"--automagic --dry-run --debug\""

    assert_true '"$AUTONAMEOW_RUNNER" --batch --config-path "$ACTIVE_CONFIG" --automagic --dry-run -- "${_sample_file}" | grep -- "${_expected_basename}"' \
                "(${_test_name}) Expect output to include \"${_expected_basename}\" when started with \"--dry-run\""

    assert_true '"$AUTONAMEOW_RUNNER" --batch --config-path "$ACTIVE_CONFIG" --automagic --dry-run --verbose -- "${_sample_file}" 2>/dev/null | grep -- "${_expected_basename}"' \
                "(${_test_name}) Expect output to include \"${_expected_basename}\" when started with \"--dry-run --verbose\""

    assert_true '[ -f "${_sample_file}" ]' \
                "(${_test_name}) The sample file should not be renamed."
}


# Test Cases
# ____________________________________________________________________________

# Store current time for later calculation of total execution time.
time_start="$(current_unix_time)"

logmsg "Started \"${SELF}\""
logmsg "Running the "$TESTSUITE_NAME" test suite .."



assert_true 'command -v python3' \
            "Python v3.x is available on the system"

AUTONAMEOW_RUNNER="$( ( cd "$SELF_DIR" && realpath -e "../bin/run.sh" ) )"
assert_false '[ -z "$AUTONAMEOW_RUNNER" ]' \
             'Variable "AUTONAMEOW_RUNNER" should not be unset'

assert_true '[ -e "$AUTONAMEOW_RUNNER" ]' \
            "The autonameow launcher script \""$(basename -- "$AUTONAMEOW_RUNNER")"\" exists"

assert_true '[ -x "$AUTONAMEOW_RUNNER" ]' \
            "The autonameow launcher script has executable permission"

ACTIVE_CONFIG="$(abspath_testfile "configs/integration_test_config_1.yaml")"
assert_false '[ -z "$ACTIVE_CONFIG" ]' \
             'Variable "ACTIVE_CONFIG" should not be unset'

assert_true '[ -e "$ACTIVE_CONFIG" ]' \
            "The config file \""$(basename -- "$ACTIVE_CONFIG")"\" exists"


SAMPLE_JPG_FILE="$(abspath_testfile "smulan.jpg")"
SAMPLE_JPG_FILE_EXPECTED='2010-01-31T161251 a cat lying on a rug.jpg'
assert_true '[ -e "$SAMPLE_JPG_FILE" ]' \
            "Sample file \"${SAMPLE_JPG_FILE}\" exists. Substitute a suitable sample file if this test fails!"

test_automagic_rename 'test_files smulan.jpg' "$SAMPLE_JPG_FILE" "$SAMPLE_JPG_FILE_EXPECTED"
test_automagic_dryrun 'test_files smulan.jpg' "$SAMPLE_JPG_FILE" "$SAMPLE_JPG_FILE_EXPECTED"


SAMPLE_PDF_FILE="$(abspath_testfile "gmail.pdf")"
SAMPLE_PDF_FILE_EXPECTED='2016-01-11T124132 gmail.pdf'
assert_true '[ -e "$SAMPLE_PDF_FILE" ]' \
            "Sample file \"${SAMPLE_PDF_FILE}\" exists. Substitute a suitable sample file if this test fails!"

test_automagic_rename 'test_files Gmail print-to-pdf' "$SAMPLE_PDF_FILE" "$SAMPLE_PDF_FILE_EXPECTED"
test_automagic_dryrun 'test_files Gmail print-to-pdf' "$SAMPLE_PDF_FILE" "$SAMPLE_PDF_FILE_EXPECTED"


SAMPLE_SIMPLESTPDF_FILE="$(abspath_testfile "simplest_pdf.md.pdf")"
SAMPLE_SIMPLESTPDF_FILE_EXPECTED='simplest_pdf.md.pdf'
assert_true '[ -e "$SAMPLE_SIMPLESTPDF_FILE" ]' \
            "Sample file \"${SAMPLE_SIMPLESTPDF_FILE}\" exists. Substitute a suitable sample file if this test fails!"

test_automagic_rename 'test_files simplest_pdf.md.pdf' "$SAMPLE_SIMPLESTPDF_FILE" "$SAMPLE_SIMPLESTPDF_FILE_EXPECTED"
test_automagic_dryrun 'test_files simplest_pdf.md.pdf' "$SAMPLE_SIMPLESTPDF_FILE" "$SAMPLE_SIMPLESTPDF_FILE_EXPECTED"


# ==============================================================================
ACTIVE_CONFIG="$(abspath_testfile "configs/integration_test_config_filetags.yaml")"
assert_false '[ -z "$ACTIVE_CONFIG" ]' \
             'Variable "ACTIVE_CONFIG" should not be unset'

assert_true '[ -e "$ACTIVE_CONFIG" ]' \
            "The config file \""$(basename -- "$ACTIVE_CONFIG")"\" exists"

SAMPLE_FILETAGS_FILE="$(abspath_testfile "2017-09-12T224820 filetags-style name -- tag2 a tag1.txt")"
SAMPLE_FILETAGS_FILE_EXPECTED='2017-09-12T224820 filetags-style name -- a tag1 tag2.txt'
assert_true '[ -e "$SAMPLE_FILETAGS_FILE" ]' \
            "Sample file \"${SAMPLE_FILETAGS_FILE}\" exists. Substitute a suitable sample file if this test fails!"

test_automagic_rename 'test_files Filetags cleanup' "$SAMPLE_FILETAGS_FILE" "$SAMPLE_FILETAGS_FILE_EXPECTED"
test_automagic_dryrun 'test_files Filetags cleanup' "$SAMPLE_FILETAGS_FILE" "$SAMPLE_FILETAGS_FILE_EXPECTED"


# ==============================================================================
ACTIVE_CONFIG="$(abspath_testfile "configs/integration_test_config_add-ext_1.yaml")"
assert_false '[ -z "$ACTIVE_CONFIG" ]' \
             'Variable "ACTIVE_CONFIG" should not be unset'

assert_true '[ -e "$ACTIVE_CONFIG" ]' \
            "The config file \""$(basename -- "$ACTIVE_CONFIG")"\" exists"

SAMPLE_EMPTY_FILE="$(abspath_testfile "empty")"
SAMPLE_EMPTY_FILE_EXPECTED='empty'
assert_true '[ -e "$SAMPLE_EMPTY_FILE" ]' \
            "Sample file \"${SAMPLE_EMPTY_FILE}\" exists. Substitute a suitable sample file if this test fails!"

test_automagic_rename 'Fix incorrect extensions Method 1 test_files/empty' "$SAMPLE_EMPTY_FILE" "$SAMPLE_EMPTY_FILE_EXPECTED"
test_automagic_dryrun 'Fix incorrect extensions Method 1 test_files/empty' "$SAMPLE_EMPTY_FILE" "$SAMPLE_EMPTY_FILE_EXPECTED"


SAMPLE_NOEXT_FILE="$(abspath_testfile "simple-lexical-analysis")"
SAMPLE_NOEXT_FILE_EXPECTED='simple-lexical-analysis.png'
assert_true '[ -e "$SAMPLE_NOEXT_FILE" ]' \
            "Sample file \"${SAMPLE_NOEXT_FILE}\" exists. Substitute a suitable sample file if this test fails!"

test_automagic_rename 'Fix incorrect extensions Method 1 test_files/simple-lexical-analysis' "$SAMPLE_NOEXT_FILE" "$SAMPLE_NOEXT_FILE_EXPECTED"
test_automagic_dryrun 'Fix incorrect extensions Method 1 test_files/simple-lexical-analysis' "$SAMPLE_NOEXT_FILE" "$SAMPLE_NOEXT_FILE_EXPECTED"


# ==============================================================================
ACTIVE_CONFIG="$(abspath_testfile "configs/integration_test_config_add-ext_2.yaml")"
assert_false '[ -z "$ACTIVE_CONFIG" ]' \
             'Variable "ACTIVE_CONFIG" should not be unset'

assert_true '[ -e "$ACTIVE_CONFIG" ]' \
            "The config file \""$(basename -- "$ACTIVE_CONFIG")"\" exists"

test_automagic_rename 'Fix incorrect extensions Method 2 test_files/empty' "$SAMPLE_EMPTY_FILE" "$SAMPLE_EMPTY_FILE_EXPECTED"
test_automagic_dryrun 'Fix incorrect extensions Method 2 test_files/empty' "$SAMPLE_EMPTY_FILE" "$SAMPLE_EMPTY_FILE_EXPECTED"


SAMPLE_MAGICTXTMD_FILE="$(abspath_testfile "magic_txt.md")"
SAMPLE_MAGICTXTMD_FILE_EXPECTED='magic_txt.md'
assert_true '[ -e "$SAMPLE_NOEXT_FILE" ]' \
            "Sample file \"${SAMPLE_MAGICTXTMD_FILE}\" exists. Substitute a suitable sample file if this test fails!"

test_automagic_rename 'Fix incorrect extensions Method 2 test_files/magic_txt.md' "$SAMPLE_MAGICTXTMD_FILE" "$SAMPLE_MAGICTXTMD_FILE_EXPECTED"
test_automagic_dryrun 'Fix incorrect extensions Method 2 test_files/magic_txt.md' "$SAMPLE_MAGICTXTMD_FILE" "$SAMPLE_MAGICTXTMD_FILE_EXPECTED"



# Calculate total execution time.
time_end="$(current_unix_time)"
total_time="$(calculate_execution_time "$time_start" "$time_end")"

log_test_suite_results_summary "$TESTSUITE_NAME" "$total_time"
