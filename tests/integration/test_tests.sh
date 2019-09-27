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
source "${AUTONAMEOW_ROOT_DIRPATH}/tests/integration/utils.sh"


_check_samplefiles_directory()
{
    aw_utils.assert_bulk_test "$(aw_utils.samplefile_abspath "$1")" d r x
}

_check_samplefiles_file()
{
    aw_utils.assert_bulk_test "$(aw_utils.samplefile_abspath "$1")" f r
}

_check_samplefiles_symlink()
{
    # NOTE(jonas): Can't test for -L because aw_utils.samplefile_abspath resolves links..
    aw_utils.assert_bulk_test "$(aw_utils.samplefile_abspath "$1")" e r
}



# Test Cases
# ____________________________________________________________________________

# Store current time for later calculation of total execution time.
time_start="$(aw_utils.current_unix_time)"

TESTSUITE_NAME='Test Suite'
aw_utils.log_msg "Running the $TESTSUITE_NAME test suite .."



aw_utils.assert_true  '[ "0" -eq "0" ]' 'Expect success .. (true positive)'
#aw_utils.assert_true  '[ "1" -eq "0" ]' 'Expect failure .. (false negative)'
aw_utils.assert_false '[ "1" -eq "0" ]' 'Expect success .. (true positive)'
#aw_utils.assert_false '[ "1" -ne "0" ]' 'Expect failure .. (false negative)'


# ______________________________________________________________________________
#
# Check shared environment variables, used by all tests.

aw_utils.assert_bulk_test "$AUTONAMEOW_ROOT_DIRPATH" n d r w x


# ______________________________________________________________________________
#
# Check script for setting environment variables, used by all tests.

_setup_environment_path="${AUTONAMEOW_ROOT_DIRPATH}/tests/setup_environment.sh"
aw_utils.assert_bulk_test "$_setup_environment_path" n f r x


# ______________________________________________________________________________
#
# Check environment variables used by specific types of tests.

aw_utils.assert_bulk_test "$AUTONAMEOW_INTEGRATION_STATS" n e f

aw_utils.assert_bulk_test "$AUTONAMEOW_INTEGRATION_LOG" n e

aw_utils.assert_false '[ -d "$AUTONAMEOW_INTEGRATION_LOG" ]' \
             'Environment variable "AUTONAMEOW_INTEGRATION_LOG" should not be a directory'

aw_utils.assert_bulk_test "$AUTONAMEOW_INTEGRATION_TIMESTAMP" n
aw_utils.assert_false '[ -z "$AUTONAMEOW_INTEGRATION_TIMESTAMP" ]' \
             'Environment variable "AUTONAMEOW_INTEGRATION_TIMESTAMP" should not be unset'


# ______________________________________________________________________________
#
# Check test dependencies

aw_utils.assert_has_command 'grep'
aw_utils.assert_has_command 'mktemp'
aw_utils.assert_has_command 'realpath'

aw_utils.assert_has_command 'sed'
aw_utils.assert_true 'man sed | grep -- "^ \+.*-i\b"' \
            'System sed supports the "-i" option, required by some integration tests'

aw_utils.assert_has_command 'time'
aw_utils.assert_has_command 'aspell'  # devscripts/check_spelling.sh


# ______________________________________________________________________________
#
# Basic checks of the test runner scripts.

_integration_runner_path="${AUTONAMEOW_ROOT_DIRPATH}/tests/run_integration_tests.sh"
aw_utils.assert_bulk_test "$_integration_runner_path" n e r x

aw_utils.assert_true '"$_integration_runner_path" -h' \
            "Expect exit code 0 when running \"${_integration_runner_path} -h\""


_unit_runner_path="${AUTONAMEOW_ROOT_DIRPATH}/tests/run_unit_tests.sh"
aw_utils.assert_bulk_test "$_unit_runner_path" n e r x

aw_utils.assert_true '"$_unit_runner_path" -h' \
            "Expect exit code 0 when running \"${_unit_runner_path} -h\""


_regression_runner_path="${AUTONAMEOW_ROOT_DIRPATH}/tests/run_regression_tests.sh"
aw_utils.assert_bulk_test "$_regression_runner_path" n e r x

aw_utils.assert_true '"$_regression_runner_path" -h' \
            "Expect exit code 0 when running \"${_regression_runner_path} -h\""


# ______________________________________________________________________________
#
# Check developer scripts and utilities in 'devscripts'.

_devscripts_path="${AUTONAMEOW_ROOT_DIRPATH}/devscripts"
aw_utils.assert_bulk_test "$_devscripts_path" n e d r w x

_todo_helper_script_path="${_devscripts_path}/todo_id.py"
aw_utils.assert_bulk_test "$_todo_helper_script_path" n e f r x

aw_utils.assert_true '"$_todo_helper_script_path"' \
            'TODO-list utility script returns exit code 0 when started without arguments'

aw_utils.assert_true '"$_todo_helper_script_path" --help' \
            'TODO-list utility script returns exit code 0 when started with argument "--help"'

_whitespace_check_script_path="${_devscripts_path}/check_whitespace.sh"
aw_utils.assert_bulk_test "$_whitespace_check_script_path" n e f r x

_check_spelling_script_path="${_devscripts_path}/check_spelling.sh"
aw_utils.assert_bulk_test "$_check_spelling_script_path" n e f r x

_check_spelling_script_wordlist_path="${_devscripts_path}/check_spelling_wordlist.txt"
aw_utils.assert_bulk_test "$_check_spelling_script_wordlist_path" n e f r


# ______________________________________________________________________________
#
# Verify utility functionality used by the integration tests.

_samplefile_empty="$(aw_utils.samplefile_abspath 'empty')"
aw_utils.assert_bulk_test "$_samplefile_empty" n e f

_samplefile_subdir="$(aw_utils.samplefile_abspath 'subdir')"
aw_utils.assert_bulk_test "$_samplefile_subdir" n e d

aw_utils.assert_true '[ "$(aw_utils.calculate_execution_time 1501987087187088013 1501987087942286968)" -eq "755" ]' \
            'aw_utils.calculate_execution_time returns expected (755ms)'

aw_utils.assert_true '[ "$(aw_utils.calculate_execution_time 1501987193168368101 1501987208094155073)" -eq "14925" ]' \
            'aw_utils.calculate_execution_time returns expected (14925ms)'

aw_utils.assert_bulk_test "$AUTONAMEOW_ROOT_DIRPATH"
aw_utils.assert_bulk_test "$AUTONAMEOW_ROOT_DIRPATH" e
aw_utils.assert_bulk_test "$AUTONAMEOW_ROOT_DIRPATH" d
aw_utils.assert_bulk_test "$AUTONAMEOW_ROOT_DIRPATH" r
aw_utils.assert_bulk_test "$AUTONAMEOW_ROOT_DIRPATH" w
aw_utils.assert_bulk_test "$AUTONAMEOW_ROOT_DIRPATH" x
aw_utils.assert_bulk_test "$AUTONAMEOW_ROOT_DIRPATH" e d
aw_utils.assert_bulk_test "$AUTONAMEOW_ROOT_DIRPATH" e d r
aw_utils.assert_bulk_test "$AUTONAMEOW_ROOT_DIRPATH" e d r w
aw_utils.assert_bulk_test "$AUTONAMEOW_ROOT_DIRPATH" e d r x
aw_utils.assert_bulk_test "$AUTONAMEOW_ROOT_DIRPATH" e r
aw_utils.assert_bulk_test "$AUTONAMEOW_ROOT_DIRPATH" e r w
aw_utils.assert_bulk_test "$AUTONAMEOW_ROOT_DIRPATH" e r x
aw_utils.assert_bulk_test "$AUTONAMEOW_ROOT_DIRPATH" e w
aw_utils.assert_bulk_test "$AUTONAMEOW_ROOT_DIRPATH" e w x
aw_utils.assert_bulk_test "$AUTONAMEOW_ROOT_DIRPATH" e x


_temporary_file='___temporary_file___'
[ -f "$_temporary_file" ] || touch "$_temporary_file"
aw_utils.assert_true '[ -f "$_temporary_file" ]' \
            'Reference dummy temporary was created'

aw_utils.assert_bulk_test "$_temporary_file"
aw_utils.assert_bulk_test "$_temporary_file" e
aw_utils.assert_bulk_test "$_temporary_file" f
aw_utils.assert_bulk_test "$_temporary_file" r
aw_utils.assert_bulk_test "$_temporary_file" w
aw_utils.assert_bulk_test "$_temporary_file" e f
aw_utils.assert_bulk_test "$_temporary_file" e f r
aw_utils.assert_bulk_test "$_temporary_file" e f r w
aw_utils.assert_bulk_test "$_temporary_file" e r
aw_utils.assert_bulk_test "$_temporary_file" e r w
aw_utils.assert_bulk_test "$_temporary_file" e w
aw_utils.assert_bulk_test "$_temporary_file" e w
aw_utils.assert_bulk_test "$_temporary_file" e
aw_utils.assert_bulk_test "$_temporary_file" f
aw_utils.assert_bulk_test "$_temporary_file" f r
aw_utils.assert_bulk_test "$_temporary_file" f r w
aw_utils.assert_bulk_test "$_temporary_file" f w

aw_utils.assert_true '[ -f "$_temporary_file" ] && rm "$_temporary_file"' \
            'Reference dummy temporary file was deleted'


# ______________________________________________________________________________
#
# Verify sample data used by all testing code; integration, regression and unit.

_check_samplefiles_file      '2007-04-23_12-comments.png'
_check_samplefiles_file      '2017-09-12T224820 filetags-style name -- tag2 a tag1.txt'
_check_samplefiles_file      '2017-11-20T020738 filetags-style name -- tag1.txt'
_check_samplefiles_file      '4123.epub'
_check_samplefiles_file      '4123.pdf'
_check_samplefiles_file      'Charles+Darwin+-+On+the+Origin+of+Species%2C+6th+Edition.mobi'
_check_samplefiles_file      'Charles+Darwin+-+On+the+Origin+of+Species%2C+6th+Edition.pdf'
_check_samplefiles_file      'Critique_of_Pure_Reason.djvu'
_check_samplefiles_file      'Critique_of_Pure_Reason.djvu_expected.txt'
_check_samplefiles_file      'UTF-8-demo.txt'
_check_samplefiles_file      'empty'
_check_samplefiles_symlink   'empty.symlink'
_check_samplefiles_file      'gmail.pdf'
_check_samplefiles_file      'magic_bmp.bmp'
_check_samplefiles_file      'magic_gif.gif'
_check_samplefiles_file      'magic_jpg.jpg'
_check_samplefiles_file      'magic_mp4.mp4'
_check_samplefiles_file      'magic_pdf.pdf'
_check_samplefiles_file      'magic_png.png'
_check_samplefiles_file      'magic_txt'
_check_samplefiles_file      'magic_txt.md'
_check_samplefiles_file      'magic_txt.txt'
_check_samplefiles_file      'ObjectCalisthenics.rtf'
_check_samplefiles_file      'ObjectCalisthenics.rtf_expected.txt'
_check_samplefiles_file      'pg38145-images.epub'
_check_samplefiles_file      'pg38145-images.epub_expected.txt'
_check_samplefiles_file      'sample.md'
_check_samplefiles_file      'sample.md_expected.txt'
_check_samplefiles_file      'sample.rtf'
_check_samplefiles_file      'sample.rtf_expected.txt'
_check_samplefiles_file      'saved-webpage.html'
_check_samplefiles_file      'saved-webpage.mhtml'
_check_samplefiles_file      'Screen Shot 2018-06-25 at 21.43.07.png'
_check_samplefiles_file      'simple-lexical-analysis'
_check_samplefiles_file      'simplest_pdf.md.pdf'
_check_samplefiles_file      'simplest_pdf.md.pdf_expected.txt'
_check_samplefiles_file      'simplest_pdf.md.pdf.txt'
_check_samplefiles_file      'smulan.jpg'
_check_samplefiles_file      'text_alnum_ascii.txt'
_check_samplefiles_file      'text_alnum_cp1252.txt'
_check_samplefiles_file      'text_alnum_cp437.txt'
_check_samplefiles_file      'text_alnum_cp858.txt'
_check_samplefiles_file      'text_alnum_iso-8859-1.txt'
_check_samplefiles_file      'text_alnum_macroman.txt'
_check_samplefiles_file      'text_alnum_utf-16.txt'
_check_samplefiles_file      'text_alnum_utf-8.txt'
_check_samplefiles_file      'text_git_euc-jp.txt'
_check_samplefiles_file      'text_git_iso-2022-jp.txt'
_check_samplefiles_file      'text_git_iso88591.txt'
_check_samplefiles_file      'text_git_utf-8_1.txt'
_check_samplefiles_file      'text_git_utf-8_2.txt'
_check_samplefiles_file      'text_git_utf16.txt'
_check_samplefiles_file      'text_sample_ascii.txt'
_check_samplefiles_file      'text_sample_cp1252.txt'
_check_samplefiles_file      'text_sample_cp437.txt'
_check_samplefiles_file      'text_sample_cp858.txt'
_check_samplefiles_file      'text_sample_iso-8859-1.txt'
_check_samplefiles_file      'text_sample_macroman.txt'
_check_samplefiles_file      'text_sample_utf-16.txt'
_check_samplefiles_file      'text_sample_utf-8.txt'
_check_samplefiles_directory 'configs'
_check_samplefiles_file      'configs/autonam€öw.yaml'
_check_samplefiles_file      'configs/bad_0001.yaml'
_check_samplefiles_file      'configs/bad_0002.yaml'
_check_samplefiles_file      'configs/bad_0003.yaml'
_check_samplefiles_file      'configs/bad_0004.yaml'
_check_samplefiles_file      'configs/bad_0005.yaml'
_check_samplefiles_file      'configs/bad_0006.yaml'
_check_samplefiles_file      'configs/bad_0007.yaml'
_check_samplefiles_file      'configs/bad_0008.yaml'
_check_samplefiles_file      'configs/bad_0009.yaml'
_check_samplefiles_file      'configs/bad_corrupt_gif.yaml'
_check_samplefiles_file      'configs/bad_empty_but_sections.yaml'
_check_samplefiles_file      'configs/bad_empty_but_version.yaml'
_check_samplefiles_file      'configs/bad_no_file_rules.yaml'
_check_samplefiles_file      'configs/default.yaml'
_check_samplefiles_file      'configs/integration_default_templated.yaml'
_check_samplefiles_file      'configs/integration_test_config_1.yaml'
_check_samplefiles_file      'configs/integration_test_config_UTF-8-demo.yaml'
_check_samplefiles_file      'configs/integration_test_config_add-ext_1.yaml'
_check_samplefiles_file      'configs/integration_test_config_add-ext_2.yaml'
_check_samplefiles_file      'configs/integration_test_config_filetags.yaml'
_check_samplefiles_directory 'subdir'
_check_samplefiles_file      'subdir/file_1'
_check_samplefiles_file      'subdir/file_2'
_check_samplefiles_file      'subdir/file_3'
_check_samplefiles_directory 'subdir/subsubdir_A'
_check_samplefiles_file      'subdir/subsubdir_A/file_A1'
_check_samplefiles_file      'subdir/subsubdir_A/file_A2'
_check_samplefiles_directory 'subdir/subsubdir_B'
_check_samplefiles_file      'subdir/subsubdir_B/file_A3'
_check_samplefiles_file      'subdir/subsubdir_B/file_B1'
_check_samplefiles_file      'subdir/subsubdir_B/file_B2'

aw_utils.assert_bulk_test "${AUTONAMEOW_ROOT_DIRPATH}/tests/unit/test_core_metadata_canonicalize_creatortool.yaml" e f r
aw_utils.assert_bulk_test "${AUTONAMEOW_ROOT_DIRPATH}/tests/unit/test_core_metadata_canonicalize_language.yaml" e f r
aw_utils.assert_bulk_test "${AUTONAMEOW_ROOT_DIRPATH}/tests/unit/test_core_metadata_canonicalize_publisher.yaml" e f r




# Calculate total execution time.
time_end="$(aw_utils.current_unix_time)"
total_time="$(aw_utils.calculate_execution_time "$time_start" "$time_end")"

aw_utils.log_test_suite_results_summary "$TESTSUITE_NAME" "$total_time"
aw_utils.update_global_test_results
