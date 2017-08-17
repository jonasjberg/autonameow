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
TESTSUITE_NAME='Documentation'

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
logmsg "Running the "$TESTSUITE_NAME" test suite .."


DOC_PATH="$( ( cd "$AUTONAMEOW_ROOT_DIR" && realpath -e "./docs/" ) )"
assert_true '[ -d "$DOC_PATH" ]' \
            "Documentation directory \""$(basename -- "$DOC_PATH")"\" should exist"

FORMATS_DOC="${DOC_PATH}/formats.md"
assert_true '[ -f "$FORMATS_DOC" ]' \
            "Data formats docs \""$(basename -- "$FORMATS_DOC")"\" should exist"

assert_true '[ "$(cat "$FORMATS_DOC" | wc -l)" -gt "50" ]' \
            "[TC006][TC008] Data formats docs contains at least 50 lines"

assert_false 'grep -q "\(TODO\|FIXME\|XXX\).*" "$FORMATS_DOC"' \
             "[TC006][TC008] Data formats docs does not contain TODOs"

_srcroot_readme="${AUTONAMEOW_ROOT_DIR}/README.md"
assert_true '[ -f "$_srcroot_readme" ]' \
            'The root source directory should contain a "README.md"'

assert_false 'grep_todos "$_srcroot_readme"' \
             "Main README.md does not contain TODOs"

_wiki_report_results="${AUTONAMEOW_WIKI_ROOT_DIR}/Test-Results.md"
assert_true '[ -f "$_wiki_report_results" ]' \
            'The project Wiki should contain "Test-Results.md"'

assert_false 'grep_todos "$FORMATS_DOC"' \
             "[TC012] Data formats docs does not contain TODOs"



_tracked_files="$( (cd "$AUTONAMEOW_TESTRESULTS_DIR" && git ls-files | grep -- '.*\.pdf$') )"
_untracked_files="$( (cd "$AUTONAMEOW_TESTRESULTS_DIR" && git ls-files --others --exclude-standard) )"
_count_tracked="$(wc -l <<< "$_tracked_files")"
_count_untracked="$(wc -l <<< "$_untracked_files")"

count_file_in_document()
{
    [ -z "${1:-}" ] && { echo "0" ; return ; }

    local _file
    while IFS='\n' read -r _file
    do
        grep -- "${_file}" "${_wiki_report_results}"
    done <<< "$1" | wc -l
}

_count_tracked_in_doc="$(count_file_in_document "${_tracked_files}")"
_count_untracked_in_doc="$(count_file_in_document "${_untracked_files}")"

assert_false '[ -z "${_count_tracked}" ]' \
             'Varible for number of tracked files should not be unset'

assert_false '[ -z "${_count_untracked}" ]' \
             'Varible for number of untracked files should not be unset'

assert_true '[ "${_count_tracked}" -eq "${_count_tracked_in_doc}" ]' \
            'All tracked logs should be included in the wiki "Test Results" page'

assert_true '[ "${_count_untracked_in_doc}" -eq "0" ]' \
            'The wiki "Test Results" page should not contain untracked files'



# Calculate total execution time.
time_end="$(current_unix_time)"
total_time="$(calculate_execution_time "$time_start" "$time_end")"

log_test_suite_results_summary "$TESTSUITE_NAME" "$total_time"
