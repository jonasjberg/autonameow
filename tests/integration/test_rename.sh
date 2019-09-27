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
source "$AUTONAMEOW_ROOT_DIRPATH/tests/integration/utils.sh"



# A sample file is copied to a temporary directory, autonameow is then started
# with the "--automagic" option, which should rename the temporary file.
# After running the program, the temporary directory should contain the
# expected base name.  Finally, the used files are deleted.
# Arguments:
# 1. A name for this group of tests.
# 2. Basename of a file in the "$SRCROOT/tests/samplefiles" directory to be
#    copied to a temporary directory. Only this copy can be modified during
#    the test.
# 3. The expected basename of the file after having been renamed.
test_automagic_rename()
{
    local -r _test_name="RENAME ${1}"
    local -r _sample_file="$(aw_utils.abspath_testfile "${2}")"
    local -r _expected_basename="$3"
    local _sample_file_basename
    local _temp_dir
    local _expected_name
    local _temp_file

    aw_utils.assert_bulk_test "$_sample_file" e f r

    _sample_file_basename="$(basename -- "${_sample_file}")"
    _temp_dir="$(mktemp -d -t aw_test_integration_rename.XXXXXX)"
    _expected_name="${_temp_dir}/${_expected_basename}"
    _temp_file="${_temp_dir}/${_sample_file_basename}"

    aw_utils.assert_true 'cp -n -- "${_sample_file}" "${_temp_file}"' \
                "(${_test_name}) Test setup should succeed in copying the sample file to a temporary directory"

    aw_utils.assert_true '[ -f "${_temp_file}" ]' \
                "(${_test_name}) A copy of the sample file must exit in the temporary directory"

    aw_utils.assert_true '[ -f "$_temp_file" ] && "$AUTONAMEOW_RUNNER" --batch --config-path "$ACTIVE_CONFIG" --automagic -- "${_temp_file}" && [ -e "$_expected_name" ]' \
                "(${_test_name}) Should be renamed to \"${_expected_basename}\""

    aw_utils.assert_true '[ -f "${_temp_file}" ] && rm -- "${_temp_file}" ; [ -f "$_expected_name" ] && rm -- "$_expected_name" || true' \
                "(${_test_name}) Test teardown should succeed in deleting temporary files"
}

# Tests autonameow using command-line options "--automagic --dry-run".
# The program output is searched for the expected file name.
# The given sample file should NOT be renamed.
# Arguments:
# 1. A name for this group of tests.
# 2. Basename of a file in the "$SRCROOT/tests/samplefiles" directory.
# 3. The expected basename of the file after having been renamed.
test_automagic_dryrun()
{
    local -r _test_name="DRY-RUN ${1}"
    local -r _sample_file="$(aw_utils.abspath_testfile "${2}")"
    local -r _expected_basename="$3"

    aw_utils.assert_bulk_test "$_sample_file" e f r

    aw_utils.assert_true '[ -f "$_sample_file" ] && "$AUTONAMEOW_RUNNER" --batch --config-path "$ACTIVE_CONFIG" --automagic --dry-run -- "${_sample_file}"' \
                "(${_test_name}) returns exit code 0 when started with \"--automagic --dry-run\""

    aw_utils.assert_true '[ -f "$_sample_file" ] && "$AUTONAMEOW_RUNNER" --batch --config-path "$ACTIVE_CONFIG" --automagic --dry-run --verbose -- "${_sample_file}"' \
                "(${_test_name}) returns exit code 0 when started with \"--automagic --dry-run --verbose\""

    aw_utils.assert_true '[ -f "$_sample_file" ] && "$AUTONAMEOW_RUNNER" --batch --config-path "$ACTIVE_CONFIG" --automagic --dry-run --debug -- "${_sample_file}"' \
                "(${_test_name}) returns exit code 0 when started with \"--automagic --dry-run --debug\""

    aw_utils.assert_true '[ -f "$_sample_file" ] && "$AUTONAMEOW_RUNNER" --batch --config-path "$ACTIVE_CONFIG" --automagic --dry-run -- "${_sample_file}" | grep -- "${_expected_basename}"' \
                "(${_test_name}) output should include \"${_expected_basename}\" when started with \"--dry-run\""

    aw_utils.assert_true '[ -f "$_sample_file" ] && "$AUTONAMEOW_RUNNER" --batch --config-path "$ACTIVE_CONFIG" --automagic --dry-run --verbose -- "${_sample_file}" 2>/dev/null | grep -- "${_expected_basename}"' \
                "(${_test_name}) output should include \"${_expected_basename}\" when started with \"--dry-run --verbose\""

    aw_utils.assert_true '[ -f "${_sample_file}" ]' \
                "(${_test_name}) The sample file should still exist, I.E. not have been renamed."
}


# Test Cases
# ____________________________________________________________________________

# Store current time for later calculation of total execution time.
time_start="$(aw_utils.current_unix_time)"

TESTSUITE_NAME='Rename Files'
aw_utils.log_msg "Running the ${TESTSUITE_NAME} test suite .."



aw_utils.assert_true 'aw_utils.command_exists python3' \
            'Python v3.x is available on the system'

aw_utils.assert_bulk_test "$AUTONAMEOW_RUNNER" n e r x

ACTIVE_CONFIG="$(aw_utils.abspath_testfile "configs/integration_test_config_1.yaml")"
aw_utils.assert_bulk_test "$ACTIVE_CONFIG" n e r


SAMPLE_PDF_FILE='gmail.pdf'
SAMPLE_PDF_FILE_EXPECTED='2016-01-11T124132 gmail.pdf'
test_automagic_rename 'samplefiles Gmail print-to-pdf' "$SAMPLE_PDF_FILE" "$SAMPLE_PDF_FILE_EXPECTED"
test_automagic_dryrun 'samplefiles Gmail print-to-pdf' "$SAMPLE_PDF_FILE" "$SAMPLE_PDF_FILE_EXPECTED"


SAMPLE_SIMPLESTPDF_FILE='simplest_pdf.md.pdf'
SAMPLE_SIMPLESTPDF_FILE_EXPECTED='simplest_pdf.md.pdf'
test_automagic_rename 'samplefiles simplest_pdf.md.pdf' "$SAMPLE_SIMPLESTPDF_FILE" "$SAMPLE_SIMPLESTPDF_FILE_EXPECTED"
test_automagic_dryrun 'samplefiles simplest_pdf.md.pdf' "$SAMPLE_SIMPLESTPDF_FILE" "$SAMPLE_SIMPLESTPDF_FILE_EXPECTED"


# ==============================================================================
ACTIVE_CONFIG="$(aw_utils.abspath_testfile "configs/integration_test_config_filetags.yaml")"
aw_utils.assert_bulk_test "$ACTIVE_CONFIG" n e r

SAMPLE_FILETAGS_FILE='2017-09-12T224820 filetags-style name -- tag2 a tag1.txt'
SAMPLE_FILETAGS_FILE_EXPECTED='2017-09-12T224820 filetags-style name -- a tag1 tag2.txt'
test_automagic_rename 'samplefiles Filetags cleanup' "$SAMPLE_FILETAGS_FILE" "$SAMPLE_FILETAGS_FILE_EXPECTED"
test_automagic_dryrun 'samplefiles Filetags cleanup' "$SAMPLE_FILETAGS_FILE" "$SAMPLE_FILETAGS_FILE_EXPECTED"


# ==============================================================================
ACTIVE_CONFIG="$(aw_utils.abspath_testfile "configs/integration_test_config_add-ext_1.yaml")"
aw_utils.assert_bulk_test "$ACTIVE_CONFIG" n e r

SAMPLE_EMPTY_FILE='empty'
SAMPLE_EMPTY_FILE_EXPECTED='empty'
test_automagic_rename 'Fix incorrect extensions Method 1 samplefiles/empty' "$SAMPLE_EMPTY_FILE" "$SAMPLE_EMPTY_FILE_EXPECTED"
test_automagic_dryrun 'Fix incorrect extensions Method 1 samplefiles/empty' "$SAMPLE_EMPTY_FILE" "$SAMPLE_EMPTY_FILE_EXPECTED"


SAMPLE_NOEXT_FILE='simple-lexical-analysis'
SAMPLE_NOEXT_FILE_EXPECTED='simple-lexical-analysis.png'
test_automagic_rename 'Fix incorrect extensions Method 1 samplefiles/simple-lexical-analysis' "$SAMPLE_NOEXT_FILE" "$SAMPLE_NOEXT_FILE_EXPECTED"
test_automagic_dryrun 'Fix incorrect extensions Method 1 samplefiles/simple-lexical-analysis' "$SAMPLE_NOEXT_FILE" "$SAMPLE_NOEXT_FILE_EXPECTED"


# ==============================================================================
ACTIVE_CONFIG="$(aw_utils.abspath_testfile "configs/integration_test_config_add-ext_2.yaml")"
aw_utils.assert_bulk_test "$ACTIVE_CONFIG" n e r

test_automagic_rename 'Fix incorrect extensions Method 2 samplefiles/empty' "$SAMPLE_EMPTY_FILE" "$SAMPLE_EMPTY_FILE_EXPECTED"
test_automagic_dryrun 'Fix incorrect extensions Method 2 samplefiles/empty' "$SAMPLE_EMPTY_FILE" "$SAMPLE_EMPTY_FILE_EXPECTED"


SAMPLE_MAGICTXTMD_FILE='magic_txt.md'
SAMPLE_MAGICTXTMD_FILE_EXPECTED='magic_txt.md'
test_automagic_rename 'Fix incorrect extensions Method 2 samplefiles/magic_txt.md' "$SAMPLE_MAGICTXTMD_FILE" "$SAMPLE_MAGICTXTMD_FILE_EXPECTED"
test_automagic_dryrun 'Fix incorrect extensions Method 2 samplefiles/magic_txt.md' "$SAMPLE_MAGICTXTMD_FILE" "$SAMPLE_MAGICTXTMD_FILE_EXPECTED"


# ==============================================================================
ACTIVE_CONFIG="$(aw_utils.abspath_testfile "configs/default.yaml")"
aw_utils.assert_bulk_test "$ACTIVE_CONFIG" n e r


assert_unable_to_find_new_name()
{
    local -r _test_name="Expect unable to find new name for \"${1}\""
    local -r _sample_file="$(aw_utils.abspath_testfile "${1}")"

    aw_utils.assert_bulk_test "$_sample_file" e f r

    aw_utils.assert_true '[ -f "$_sample_file" ] && "$AUTONAMEOW_RUNNER" --batch --config-path "$ACTIVE_CONFIG" --automagic --dry-run -- "${_sample_file}"' \
                "(${_test_name}) returns exit code 0 when started with \"--batch --automagic --dry-run\""

    aw_utils.assert_true '[ -f "$_sample_file" ] && "$AUTONAMEOW_RUNNER" --batch --config-path "$ACTIVE_CONFIG" --automagic --dry-run --verbose -- "${_sample_file}"' \
                "(${_test_name}) returns exit code 0 when started with \"--batch --automagic --dry-run --verbose\""

    aw_utils.assert_true '[ -f "$_sample_file" ] && "$AUTONAMEOW_RUNNER" --batch --config-path "$ACTIVE_CONFIG" --automagic --dry-run --debug -- "${_sample_file}"' \
                "(${_test_name}) returns exit code 0 when started with \"--batch --automagic --dry-run --debug\""

    aw_utils.assert_true '[ -f "$_sample_file" ] && "$AUTONAMEOW_RUNNER" --batch --config-path "$ACTIVE_CONFIG" --automagic --dry-run --quiet -- "${_sample_file}"' \
                "(${_test_name}) returns exit code 0 when started with \"--batch --automagic --dry-run --quiet\""

    aw_utils.assert_true '[ -f "${_sample_file}" ]' \
                "(${_test_name}) The sample file should still exist, I.E. not have been renamed."
}

assert_unable_to_find_new_name '2007-04-23_12-comments.png'
assert_unable_to_find_new_name '2017-09-12T224820 filetags-style name -- tag2 a tag1.txt'
assert_unable_to_find_new_name '2017-11-20T020738 filetags-style name -- tag1.txt'
assert_unable_to_find_new_name '4123.epub'
assert_unable_to_find_new_name '4123.pdf'
assert_unable_to_find_new_name 'Charles+Darwin+-+On+the+Origin+of+Species%2C+6th+Edition.mobi'
assert_unable_to_find_new_name 'Charles+Darwin+-+On+the+Origin+of+Species%2C+6th+Edition.pdf'
assert_unable_to_find_new_name 'UTF-8-demo.txt'
assert_unable_to_find_new_name 'empty'
assert_unable_to_find_new_name 'gmail.pdf'
assert_unable_to_find_new_name 'magic_bmp.bmp'
assert_unable_to_find_new_name 'magic_gif.gif'
assert_unable_to_find_new_name 'magic_jpg.jpg'
assert_unable_to_find_new_name 'magic_mp4.mp4'
assert_unable_to_find_new_name 'magic_pdf.pdf'
assert_unable_to_find_new_name 'magic_png.png'
assert_unable_to_find_new_name 'magic_txt'
assert_unable_to_find_new_name 'magic_txt.md'
assert_unable_to_find_new_name 'magic_txt.txt'
assert_unable_to_find_new_name 'ObjectCalisthenics.rtf'
assert_unable_to_find_new_name 'pg38145-images.epub'
assert_unable_to_find_new_name 'pg38145-images.epub_expected.txt'
assert_unable_to_find_new_name 'sample.md'
assert_unable_to_find_new_name 'sample.md_expected.txt'
assert_unable_to_find_new_name 'sample.rtf'
assert_unable_to_find_new_name 'sample.rtf_expected.txt'
assert_unable_to_find_new_name 'saved-webpage.html'
assert_unable_to_find_new_name 'saved-webpage.mhtml'
assert_unable_to_find_new_name 'simple-lexical-analysis'
assert_unable_to_find_new_name 'simplest_pdf.md.pdf'
assert_unable_to_find_new_name 'simplest_pdf.md.pdf_expected.txt'
assert_unable_to_find_new_name 'simplest_pdf.md.pdf.txt'
assert_unable_to_find_new_name 'smulan.jpg'
assert_unable_to_find_new_name 'text_alnum_ascii.txt'
assert_unable_to_find_new_name 'text_alnum_cp1252.txt'
assert_unable_to_find_new_name 'text_alnum_cp437.txt'
assert_unable_to_find_new_name 'text_alnum_cp858.txt'
assert_unable_to_find_new_name 'text_alnum_iso-8859-1.txt'
assert_unable_to_find_new_name 'text_alnum_macroman.txt'
assert_unable_to_find_new_name 'text_alnum_utf-16.txt'
assert_unable_to_find_new_name 'text_alnum_utf-8.txt'
assert_unable_to_find_new_name 'text_git_euc-jp.txt'
assert_unable_to_find_new_name 'text_git_iso-2022-jp.txt'
assert_unable_to_find_new_name 'text_git_iso88591.txt'
assert_unable_to_find_new_name 'text_git_utf-8_1.txt'
assert_unable_to_find_new_name 'text_git_utf-8_2.txt'
assert_unable_to_find_new_name 'text_git_utf16.txt'
assert_unable_to_find_new_name 'text_sample_ascii.txt'
assert_unable_to_find_new_name 'text_sample_cp1252.txt'
assert_unable_to_find_new_name 'text_sample_cp437.txt'
assert_unable_to_find_new_name 'text_sample_cp858.txt'
assert_unable_to_find_new_name 'text_sample_iso-8859-1.txt'
assert_unable_to_find_new_name 'text_sample_macroman.txt'
assert_unable_to_find_new_name 'text_sample_utf-16.txt'
assert_unable_to_find_new_name 'text_sample_utf-8.txt'




# Calculate total execution time.
time_end="$(aw_utils.current_unix_time)"
total_time="$(aw_utils.calculate_execution_time "$time_start" "$time_end")"

aw_utils.log_test_suite_results_summary "$TESTSUITE_NAME" "$total_time"
aw_utils.update_global_test_results
