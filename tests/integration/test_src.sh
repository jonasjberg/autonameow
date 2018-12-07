#!/usr/bin/env bash

#   Copyright(c) 2016-2018 Jonas Sjöberg <autonameow@jonasjberg.com>
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


check_git_ls_files_does_not_match()
{
    local -r _pattern="$1"
    assert_false 'cd "$AUTONAMEOW_ROOT_DIR" && git ls-files | grep --fixed-strings -- "$_pattern"' \
                 "git repository does not contain files matching \"${_pattern}\""
}



# Test Cases
# ____________________________________________________________________________

# Store current time for later calculation of total execution time.
time_start="$(current_unix_time)"

TESTSUITE_NAME='Source Code'
logmsg "Running the ${TESTSUITE_NAME} test suite .."



# ______________________________________________________________________________
#
# Make sure that certain files have not been added to version control.

check_git_ls_files_does_not_match '.cache'
check_git_ls_files_does_not_match '.DS_Store'
check_git_ls_files_does_not_match '.hypothesis'
check_git_ls_files_does_not_match '.idea'
check_git_ls_files_does_not_match '.orig'
check_git_ls_files_does_not_match '.pyc'
check_git_ls_files_does_not_match 'junk/'
check_git_ls_files_does_not_match 'local/'
check_git_ls_files_does_not_match '__pycache__'
check_git_ls_files_does_not_match 'docs/test_results'
check_git_ls_files_does_not_match '.regressionrunner_captured_runtimes'
check_git_ls_files_does_not_match '.regressionrunner_history'
check_git_ls_files_does_not_match '.regressionrunner_lastrun'


# ______________________________________________________________________________
#
# Make sure that data files are available.

assert_bulk_test "${AUTONAMEOW_ROOT_DIR}/autonameow/util/mimemagic.mappings" e f r
assert_bulk_test "${AUTONAMEOW_ROOT_DIR}/autonameow/util/mimemagic.preferred" e f r

assert_bulk_test "${AUTONAMEOW_ROOT_DIR}/autonameow/analyzers/probable_extension_lookup" e f r

assert_bulk_test "${AUTONAMEOW_ROOT_DIR}/autonameow/extractors/filesystem/crossplatform_fieldmeta.yaml" e f r
assert_bulk_test "${AUTONAMEOW_ROOT_DIR}/autonameow/extractors/filesystem/filetags_fieldmeta.yaml" e f r
assert_bulk_test "${AUTONAMEOW_ROOT_DIR}/autonameow/extractors/filesystem/guessit_fieldmeta.yaml" e f r
assert_bulk_test "${AUTONAMEOW_ROOT_DIR}/autonameow/extractors/metadata/extractor_exiftool_fieldmeta.yaml" e f r
assert_bulk_test "${AUTONAMEOW_ROOT_DIR}/autonameow/extractors/metadata/extractor_jpeginfo_fieldmeta.yaml" e f r
assert_bulk_test "${AUTONAMEOW_ROOT_DIR}/autonameow/extractors/metadata/extractor_pandoc_fieldmeta.yaml" e f r
assert_bulk_test "${AUTONAMEOW_ROOT_DIR}/autonameow/extractors/metadata/extractor_pandoc_template.plain" e f r

assert_bulk_test "${AUTONAMEOW_ROOT_DIR}/autonameow/core/metadata/canonical_creatortool.yaml" e f r
assert_bulk_test "${AUTONAMEOW_ROOT_DIR}/autonameow/core/metadata/canonical_language.yaml" e f r
assert_bulk_test "${AUTONAMEOW_ROOT_DIR}/autonameow/core/metadata/canonical_publisher.yaml" e f r


# ______________________________________________________________________________
#
# Check TODO-list identifiers with stand-alone TODO-list utility script.

_todo_helper_script_path="${AUTONAMEOW_ROOT_DIR}/devscripts/todo_id.py"

assert_true '"${_todo_helper_script_path}"' \
            'TODO-list utility script checks pass ("todo_id.py --check" returns 0)'


# ______________________________________________________________________________
#
# Check text file style violations, whitespace, line separators, etc.

text_files=(
    $(git ls-files | xargs file --mime-type -- | grep 'text/' | cut -d':' -f1 | grep -v -- 'tests.*\.yaml$\|.md$\|test_results\|local\|junk\|test_files\|notes\|thirdparty\|write_sample_textfiles.py\|test_extractors_text_rtf.py')
)
_check_committed_textfiles_exist_and_readable()
{
    for tf in "${text_files[@]}"
    do
        [ -r "$tf" ] || return 1
    done
    return 0
}
assert_true '_check_committed_textfiles_exist_and_readable' \
            'All committed files with MIME-type matching "text/*" exist and are readable'


python_source_files=(
    $(git ls-files | grep '\.py$' | grep -v -- 'junk\|local\|notes\|test_files\|thirdparty')
)
_check_python_source_files_exist_and_readable()
{
    for tf in "${python_source_files[@]}"
    do
        [ -r "$tf" ] || return 1
    done
    return 0
}
assert_true '_check_python_source_files_exist_and_readable' \
            'All committed Python source files (some excluded, see test for details) exist and are readable'


_check_python_source_files_do_not_use_grouped_imports()
{
    for tf in "${python_source_files[@]}"
    do
        grep -qE 'from [a-zA-Z0-9_\.]+ import \($' -- "$tf" && return 1
    done
    return 0
}
assert_true '_check_python_source_files_do_not_use_grouped_imports' \
            'None of the committed Python source files (some excluded, see test for details) use grouped import statements'


_whitespace_check_script_path="${AUTONAMEOW_ROOT_DIR}/devscripts/check_whitespace.sh"
assert_bulk_test "$_whitespace_check_script_path" e x

assert_true '$_whitespace_check_script_path' \
            'Whitespace conformance script checks pass ("check_whitespace.sh" returns 0)'


# ______________________________________________________________________________
#
# Check spelling with external script.

_check_spelling_script_path="${AUTONAMEOW_ROOT_DIR}/devscripts/check-spelling.sh"
assert_bulk_test "$_check_spelling_script_path" e x

assert_true '$_check_spelling_script_path' \
            'Spell-checker script checks pass ("check-spelling.sh" returns 0)'




# Calculate total execution time.
time_end="$(current_unix_time)"
total_time="$(calculate_execution_time "$time_start" "$time_end")"

log_test_suite_results_summary "$TESTSUITE_NAME" "$total_time"
update_global_test_results
