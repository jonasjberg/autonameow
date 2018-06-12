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


check_testfiles_directory()
{
    assert_bulk_test "$(abspath_testfile "$1")" d r x
}

check_testfiles_file()
{
    assert_bulk_test "$(abspath_testfile "$1")" f r
}

check_testfiles_symlink()
{
    # NOTE(jonas): Can't test for -L because abspath_testfile resolves links..
    assert_bulk_test "$(abspath_testfile "$1")" e r
}



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

assert_bulk_test "$AUTONAMEOW_ROOT_DIR" n d r w x


# ______________________________________________________________________________
#
# Check script for setting environment variables, used by all tests.

_setup_environment_path="${AUTONAMEOW_ROOT_DIR}/tests/setup_environment.sh"
assert_bulk_test "$_setup_environment_path" n f r x


# ______________________________________________________________________________
#
# Check environment variables used by specific types of tests.

assert_bulk_test "$AUTONAMEOW_INTEGRATION_STATS" n e f

assert_bulk_test "$AUTONAMEOW_INTEGRATION_LOG" n e

assert_false '[ -d "$AUTONAMEOW_INTEGRATION_LOG" ]' \
             'Environment variable "AUTONAMEOW_INTEGRATION_LOG" should not be a directory'

assert_bulk_test "$AUTONAMEOW_INTEGRATION_TIMESTAMP" n
assert_false '[ -z "$AUTONAMEOW_INTEGRATION_TIMESTAMP" ]' \
             'Environment variable "AUTONAMEOW_INTEGRATION_TIMESTAMP" should not be unset'


# ______________________________________________________________________________
#
# Check test dependencies

assert_has_command 'grep'
assert_has_command 'mktemp'
assert_has_command 'realpath'

assert_has_command 'sed'
assert_true 'man sed | grep -- "^ \+.*-i\b"' \
            'System sed supports the "-i" option, required by some integration tests'

assert_has_command 'time'
assert_has_command 'aspell'  # devscripts/check-spelling.sh


# ______________________________________________________________________________
#
# Basic checks of the test runner scripts.

_integration_runner_path="${AUTONAMEOW_ROOT_DIR}/tests/run_integration_tests.sh"
assert_bulk_test "$_integration_runner_path" n e r x

assert_true '"$_integration_runner_path" -h' \
            "Expect exit code 0 when running \"${_integration_runner_path} -h\""


_unit_runner_path="${AUTONAMEOW_ROOT_DIR}/tests/run_unit_tests.sh"
assert_bulk_test "$_unit_runner_path" n e r x

assert_true '"$_unit_runner_path" -h' \
            "Expect exit code 0 when running \"${_unit_runner_path} -h\""


_regression_runner_path="${AUTONAMEOW_ROOT_DIR}/tests/run_regression_tests.sh"
assert_bulk_test "$_regression_runner_path" n e r x

assert_true '"$_regression_runner_path" -h' \
            "Expect exit code 0 when running \"${_regression_runner_path} -h\""


# ______________________________________________________________________________
#
# Check developer scripts and utilities in 'devscripts'.

_devscripts_path="${AUTONAMEOW_ROOT_DIR}/devscripts"
assert_bulk_test "$_devscripts_path" n e d r w x

_todo_helper_script_path="${_devscripts_path}/todo_id.py"
assert_bulk_test "$_todo_helper_script_path" n e f r x

assert_true '"${_todo_helper_script_path}"' \
            'TODO-list utility script returns exit code 0 when started without arguments'

assert_true '"${_todo_helper_script_path}" --help' \
            'TODO-list utility script returns exit code 0 when started with argument "--help"'

_whitespace_check_script_path="${_devscripts_path}/check_whitespace.sh"
assert_bulk_test "$_whitespace_check_script_path" n e f r x

_check_spelling_script_path="${_devscripts_path}/check-spelling.sh"
assert_bulk_test "$_check_spelling_script_path" n e f r x

_check_spelling_script_wordlist_path="${_devscripts_path}/check-spelling-wordlist.txt"
assert_bulk_test "$_check_spelling_script_wordlist_path" n e f r


# ______________________________________________________________________________
#
# Shared bash script (integration test) functionality.

_abspath_testfile_empty="$(abspath_testfile "empty")"
assert_bulk_test "$_abspath_testfile_empty" n e f

_abspath_testfile_subdir="$(abspath_testfile "subdir")"
assert_bulk_test "$_abspath_testfile_subdir" n e d

assert_bash_function 'calculate_execution_time'

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


_temporary_file='___temporary_file___'
[ -f "$_temporary_file" ] || touch "$_temporary_file"
assert_true '[ -f "${_temporary_file}" ]' \
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

assert_true '[ -f "${_temporary_file}" ] && rm "$_temporary_file"' \
            'Reference dummy temporary file was deleted'


# ______________________________________________________________________________
#
# Verify sample test files used by other tests.

check_testfiles_file      '2007-04-23_12-comments.png'
check_testfiles_file      '2017-09-12T224820 filetags-style name -- tag2 a tag1.txt'
check_testfiles_file      '2017-11-20T020738 filetags-style name -- tag1.txt'
check_testfiles_file      '4123.epub'
check_testfiles_file      '4123.pdf'
check_testfiles_file      'Charles+Darwin+-+On+the+Origin+of+Species%2C+6th+Edition.mobi'
check_testfiles_file      'Charles+Darwin+-+On+the+Origin+of+Species%2C+6th+Edition.pdf'
check_testfiles_file      'UTF-8-demo.txt'
check_testfiles_file      'empty'
check_testfiles_symlink   'empty.symlink'
check_testfiles_file      'gmail.pdf'
check_testfiles_file      'magic_bmp.bmp'
check_testfiles_file      'magic_gif.gif'
check_testfiles_file      'magic_jpg.jpg'
check_testfiles_file      'magic_mp4.mp4'
check_testfiles_file      'magic_pdf.pdf'
check_testfiles_file      'magic_png.png'
check_testfiles_file      'magic_txt'
check_testfiles_file      'magic_txt.md'
check_testfiles_file      'magic_txt.txt'
check_testfiles_file      'ObjectCalisthenics.rtf'
check_testfiles_file      'ObjectCalisthenics.rtf_expected.txt'
check_testfiles_file      'pg38145-images.epub'
check_testfiles_file      'pg38145-images.epub_expected.txt'
check_testfiles_file      'sample.md'
check_testfiles_file      'sample.md_expected.txt'
check_testfiles_file      'sample.rtf'
check_testfiles_file      'sample.rtf_expected.txt'
check_testfiles_file      'saved-webpage.html'
check_testfiles_file      'saved-webpage.mhtml'
check_testfiles_file      'simple-lexical-analysis'
check_testfiles_file      'simplest_pdf.md.pdf'
check_testfiles_file      'simplest_pdf.md.pdf_expected.txt'
check_testfiles_file      'simplest_pdf.md.pdf.txt'
check_testfiles_file      'smulan.jpg'
check_testfiles_file      'text_alnum_ascii.txt'
check_testfiles_file      'text_alnum_cp1252.txt'
check_testfiles_file      'text_alnum_cp437.txt'
check_testfiles_file      'text_alnum_cp858.txt'
check_testfiles_file      'text_alnum_iso-8859-1.txt'
check_testfiles_file      'text_alnum_macroman.txt'
check_testfiles_file      'text_alnum_utf-16.txt'
check_testfiles_file      'text_alnum_utf-8.txt'
check_testfiles_file      'text_git_euc-jp.txt'
check_testfiles_file      'text_git_iso-2022-jp.txt'
check_testfiles_file      'text_git_iso88591.txt'
check_testfiles_file      'text_git_utf-8_1.txt'
check_testfiles_file      'text_git_utf-8_2.txt'
check_testfiles_file      'text_git_utf16.txt'
check_testfiles_file      'text_sample_ascii.txt'
check_testfiles_file      'text_sample_cp1252.txt'
check_testfiles_file      'text_sample_cp437.txt'
check_testfiles_file      'text_sample_cp858.txt'
check_testfiles_file      'text_sample_iso-8859-1.txt'
check_testfiles_file      'text_sample_macroman.txt'
check_testfiles_file      'text_sample_utf-16.txt'
check_testfiles_file      'text_sample_utf-8.txt'
check_testfiles_directory 'configs'
check_testfiles_file      'configs/autonam€öw.yaml'
check_testfiles_file      'configs/bad_0001.yaml'
check_testfiles_file      'configs/bad_0002.yaml'
check_testfiles_file      'configs/bad_0003.yaml'
check_testfiles_file      'configs/bad_0004.yaml'
check_testfiles_file      'configs/bad_0005.yaml'
check_testfiles_file      'configs/bad_0006.yaml'
check_testfiles_file      'configs/bad_0007.yaml'
check_testfiles_file      'configs/bad_0008.yaml'
check_testfiles_file      'configs/bad_0009.yaml'
check_testfiles_file      'configs/bad_corrupt_gif.yaml'
check_testfiles_file      'configs/bad_empty_but_sections.yaml'
check_testfiles_file      'configs/bad_empty_but_version.yaml'
check_testfiles_file      'configs/bad_no_file_rules.yaml'
check_testfiles_file      'configs/default.yaml'
check_testfiles_file      'configs/integration_default_templated.yaml'
check_testfiles_file      'configs/integration_test_config_1.yaml'
check_testfiles_file      'configs/integration_test_config_UTF-8-demo.yaml'
check_testfiles_file      'configs/integration_test_config_add-ext_1.yaml'
check_testfiles_file      'configs/integration_test_config_add-ext_2.yaml'
check_testfiles_file      'configs/integration_test_config_filetags.yaml'
check_testfiles_directory 'subdir'
check_testfiles_file      'subdir/file_1'
check_testfiles_file      'subdir/file_2'
check_testfiles_file      'subdir/file_3'
check_testfiles_directory 'subdir/subsubdir_A'
check_testfiles_file      'subdir/subsubdir_A/file_A1'
check_testfiles_file      'subdir/subsubdir_A/file_A2'
check_testfiles_directory 'subdir/subsubdir_B'
check_testfiles_file      'subdir/subsubdir_B/file_A3'
check_testfiles_file      'subdir/subsubdir_B/file_B1'
check_testfiles_file      'subdir/subsubdir_B/file_B2'




# Calculate total execution time.
time_end="$(current_unix_time)"
total_time="$(calculate_execution_time "$time_start" "$time_end")"

log_test_suite_results_summary "$TESTSUITE_NAME" "$total_time"
update_global_test_results
