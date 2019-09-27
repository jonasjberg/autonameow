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


check_git_ls_files_does_not_match()
{
    local -r _pattern="$1"
    aw_utils.assert_false 'cd "$AUTONAMEOW_ROOT_DIRPATH" && git ls-files | grep --fixed-strings -- "$_pattern"' \
                 "git repository does not contain files matching \"${_pattern}\""
}



# Test Cases
# ____________________________________________________________________________

# Store current time for later calculation of total execution time.
time_start="$(aw_utils.current_unix_time)"

TESTSUITE_NAME='Source Code'
aw_utils.log_msg "Running the $TESTSUITE_NAME test suite .."



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

aw_utils.assert_bulk_test "${AUTONAMEOW_ROOT_DIRPATH}/autonameow/util/mimemagic.mappings" e f r
aw_utils.assert_bulk_test "${AUTONAMEOW_ROOT_DIRPATH}/autonameow/util/mimemagic.preferred" e f r

aw_utils.assert_bulk_test "${AUTONAMEOW_ROOT_DIRPATH}/autonameow/analyzers/probable_extension_lookup" e f r

declare -a _FIELDMETA_YAML_FILES=(
    "${AUTONAMEOW_ROOT_DIRPATH}/autonameow/extractors/metadata/extractor_crossplatform_fieldmeta.yaml"
    "${AUTONAMEOW_ROOT_DIRPATH}/autonameow/extractors/metadata/extractor_exiftool_fieldmeta.yaml"
    "${AUTONAMEOW_ROOT_DIRPATH}/autonameow/extractors/metadata/extractor_filetags_fieldmeta.yaml"
    "${AUTONAMEOW_ROOT_DIRPATH}/autonameow/extractors/metadata/extractor_guessit_fieldmeta.yaml"
    "${AUTONAMEOW_ROOT_DIRPATH}/autonameow/extractors/metadata/extractor_jpeginfo_fieldmeta.yaml"
    "${AUTONAMEOW_ROOT_DIRPATH}/autonameow/extractors/metadata/extractor_pandoc_fieldmeta.yaml"
    "${AUTONAMEOW_ROOT_DIRPATH}/autonameow/extractors/metadata/extractor_pandoc_template.plain"
)
for fieldmeta_file in "${_FIELDMETA_YAML_FILES[@]}"
do
    aw_utils.assert_bulk_test "$fieldmeta_file" e f r
done

aw_utils.assert_bulk_test "${AUTONAMEOW_ROOT_DIRPATH}/autonameow/core/truths/data/creatortool.yaml" e f r
aw_utils.assert_bulk_test "${AUTONAMEOW_ROOT_DIRPATH}/autonameow/core/truths/data/language.yaml" e f r
aw_utils.assert_bulk_test "${AUTONAMEOW_ROOT_DIRPATH}/autonameow/core/truths/data/publisher.yaml" e f r


# ______________________________________________________________________________
#
# Check field meta file contents. The 'generic_field' values are case-sensitive.

for fieldmeta_file in "${_FIELDMETA_YAML_FILES[@]}"
do
    _fieldmeta_basename="$(basename -- "$fieldmeta_file")"

    aw_utils.assert_false 'grep -qE -- "generic_field: [A-Z]+" "$fieldmeta_file"' \
                 "Fieldmeta YAML-file \"${_fieldmeta_basename}\" does not capitalize any \"generic_field\" value"

    if grep -q -- 'generic_field' "$fieldmeta_file"
    then
        _expr='grep -qE -- "generic_field: [a-z_]+( +?#.*)?$" "$fieldmeta_file"'
    else
        # File does not contain any "generic_field" entry but is included
        # like this (shame.. shame..) to keep the number of tests constant.
        _expr='true'
    fi
    aw_utils.assert_true "$_expr" \
                "Fieldmeta YAML-file \"${_fieldmeta_basename}\" uses only ASCII letters and underlines in any and all \"generic_field\" values"

    aw_utils.assert_false 'grep -qE -- "weight: [0-9]+$" "$fieldmeta_file"' \
                 "Fieldmeta YAML-file \"${_fieldmeta_basename}\" uses floats for all \"weight\" values (1.0 rather than 1)"
done


# ______________________________________________________________________________
#
# Check TODO-list identifiers with stand-alone TODO-list utility script.

_todo_helper_script_path="${AUTONAMEOW_ROOT_DIRPATH}/devscripts/todo_id.py"

aw_utils.assert_true '"$_todo_helper_script_path"' \
            'TODO-list utility script checks pass ("todo_id.py --check" returns 0)'


# ______________________________________________________________________________
#
# Check text file style violations, whitespace, line separators, etc.

text_files=(
    $(git ls-files | xargs file --mime-type -- | grep 'text/' | cut -d':' -f1 | grep -v -- 'tests.*\.yaml$\|.md$\|test_results\|local\|junk\|samplefiles\|notes\|thirdparty\|write_sample_textfiles.py\|test_extractors_text_rtf.py')
)
_check_committed_textfiles_exist_and_readable()
{
    for tf in "${text_files[@]}"
    do
        [ -r "$tf" ] || return 1
    done
    return 0
}
aw_utils.assert_true '_check_committed_textfiles_exist_and_readable' \
            'All committed files with MIME-type matching "text/*" exist and are readable'


python_source_files=(
    $(git ls-files '*.py' | grep -v -- 'junk\|local\|notes\|samplefiles\|thirdparty\|vendor')
)
_check_python_source_files_exist_and_readable()
{
    for tf in "${python_source_files[@]}"
    do
        [ -r "$tf" ] || return 1
    done
    return 0
}
aw_utils.assert_true '_check_python_source_files_exist_and_readable' \
            'All committed Python source files (some excluded, see test for details) exist and are readable'


_check_python_source_files_do_not_use_grouped_imports()
{
    for tf in "${python_source_files[@]}"
    do
        grep -qE 'from [a-zA-Z0-9_\.]+ import \($' -- "$tf" && return 1
    done
    return 0
}
aw_utils.assert_true '_check_python_source_files_do_not_use_grouped_imports' \
            'None of the committed Python source files (some excluded, see test for details) use grouped import statements'


_whitespace_check_script_path="${AUTONAMEOW_ROOT_DIRPATH}/devscripts/check_whitespace.sh"
aw_utils.assert_bulk_test "$_whitespace_check_script_path" e x

aw_utils.assert_true '$_whitespace_check_script_path' \
            'Whitespace conformance script checks pass ("check_whitespace.sh" returns 0)'


# ______________________________________________________________________________
#
# Check spelling with external script.

_check_spelling_script_path="${AUTONAMEOW_ROOT_DIRPATH}/devscripts/check_spelling.sh"
aw_utils.assert_bulk_test "$_check_spelling_script_path" e x

aw_utils.assert_true '$_check_spelling_script_path' \
            'Spell-checker script checks pass ("check_spelling.sh" returns 0)'




# Calculate total execution time.
time_end="$(aw_utils.current_unix_time)"
total_time="$(aw_utils.calculate_execution_time "$time_start" "$time_end")"

aw_utils.log_test_suite_results_summary "$TESTSUITE_NAME" "$total_time"
aw_utils.update_global_test_results
