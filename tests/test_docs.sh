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


SELF="$(basename "$0")"
SELF_DIR="$(dirname "$0")"

source "${SELF_DIR}/utils.sh"



# Test Cases
# ____________________________________________________________________________


logmsg "Started \"${SELF}\""
logmsg "Running the Documentation test suite .."



FORMATS_DOC="$( ( cd "$SELF_DIR" && realpath -e "../docs/formats.md" ) )"
assert_true '[ -f "$FORMATS_DOC" ]' \
            "Data formats docs \""$(basename -- "$FORMATS_DOC")"\" should exist"

assert_true '[ "$(cat "$FORMATS_DOC" | wc -l)" -gt "50" ]' \
            "Data formats docs contains at least 50 lines"

assert_false 'grep -q "\(TODO\|FIXME\|XXX\).*" "$FORMATS_DOC"' \
             "Data formats docs does not contain TODOs"



calculate_statistics
logmsg "Completed the Documentation test suite tests in ${SECONDS} seconds"

