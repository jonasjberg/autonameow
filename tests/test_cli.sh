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
logmsg "Running the Command-Line Interface test suite .."



AUTONAMEOW_RUNNER="$( ( cd "$SELF_DIR" && realpath -e "../run.sh" ) )"
assert_true '[ -e "$AUTONAMEOW_RUNNER" ]' \
            "The autonameow launcher script should exist"

assert_true '[ -x "$AUTONAMEOW_RUNNER" ]' \
            "The autonameow launcher script has executable permission"

assert_true '"$AUTONAMEOW_RUNNER"' \
            "The autonameow launcher script can be started with no arguments"



calculate_statistics
logmsg "Completed the Command-Line Interface test suite tests in ${SECONDS} seconds"
