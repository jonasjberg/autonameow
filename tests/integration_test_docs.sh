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
logmsg "Running the Documentation test suite .."


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



# Calculate total execution time.
time_end="$(current_unix_time)"
total_time="$((($time_end - $time_start) / 1000000))"

calculate_statistics
logmsg "Completed the Documentation test suite tests in ${total_time} ms"
