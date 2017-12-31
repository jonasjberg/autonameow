#!/usr/bin/env bash

# Copyright(c) 2016-2017 Jonas Sjöberg
# https://github.com/jonasjberg
# http://www.jonasjberg.com
# University mail: js224eh[a]student.lnu.se
# _____________________________________________________________________________
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
# _____________________________________________________________________________
#

set -o noclobber -o nounset -o pipefail


AUTONAMEOW_TESTRESULTS_DIR="/Users/jonas/Dropbox/LNU/1DV430_IndividuelltProjekt/src/js224eh-project.git/docs/test_results"
TEST_RESULTS_DOCUMENT="/Users/jonas/Dropbox/LNU/1DV430_IndividuelltProjekt/src/js224eh-project.wiki.git/Test-Results.md"

if [ ! -d "$AUTONAMEOW_TESTRESULTS_DIR" ]
then
    cat >&2 <<EOF

[ERROR] Not a directory: "${AUTONAMEOW_TESTRESULTS_DIR}"
        Set "AUTONAMEOW_TESTRESULTS_DIR" before running this script.

EOF
    exit 1
fi

if [ ! -f "$TEST_RESULTS_DOCUMENT" ]
then
    cat >&2 <<EOF

[ERROR] Not a file: "${TEST_RESULTS_DOCUMENT}"
        Set "TEST_RESULTS_DOCUMENT" before running this script.

EOF
    exit 1
fi


tracked_files="$( (cd "$AUTONAMEOW_TESTRESULTS_DIR" && git ls-files) )"
untracked_files="$( (cd "$AUTONAMEOW_TESTRESULTS_DIR" && git ls-files --others --exclude-standard) )"

# Number of tracked files.
count_tracked="$(wc -l <<< "$tracked_files")"

# Number of untracked files.
count_untracked="$(wc -l <<< "$untracked_files")"

# Number of tracked files in the document.
count_file_in_document()
{
    while IFS=$'\n' read -r _file
    do
        grep -- "${_file}" "$TEST_RESULTS_DOCUMENT"
    done <<< "$1" | wc -l
}

print_stats_line()
{
    printf '%30.30s : %s\n' "$1" "$2"
}

count_tracked_in_doc="$(count_file_in_document "${tracked_files}")"
count_untracked_in_doc="$(count_file_in_document "${untracked_files}")"

printf '\n\n'
print_stats_line "Tracked logs" "$count_tracked"
print_stats_line "UNTracked logs" "$count_untracked"
print_stats_line "Tracked logs in wiki report" "${count_tracked_in_doc}"
print_stats_line "UNTracked logs in wiki report" "${count_untracked_in_doc}"
printf '\n\n'

if [ "${count_tracked}" -eq "${count_tracked_in_doc}" ]
then
    printf '[PASS] All tracked logs are present in the wiki report\n'
else
    printf '[FAIL] Number of tracked logs differs from number of logs in the wiki report!\n'
fi

if [ "${count_untracked_in_doc}" -eq "0" ]
then
    printf '[PASS] No untracked files in the report\n'
else
    printf '[FAIL] Report contains untracked files!\n'
fi
