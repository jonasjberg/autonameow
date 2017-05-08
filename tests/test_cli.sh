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

source "${SELF_DIR}/utils.sh"



# Test Cases
# ____________________________________________________________________________


logmsg "Started \"${SELF}\""
logmsg "Running the Command-Line Interface test suite .."



AUTONAMEOW_RUNNER="$( ( cd "$SELF_DIR" && realpath -e "../run.sh" ) )"
assert_true '[ -e "$AUTONAMEOW_RUNNER" ]' \
            "The autonameow launcher script \""$(basename -- "$AUTONAMEOW_RUNNER")"\" exists"

assert_true '[ -x "$AUTONAMEOW_RUNNER" ]' \
            "The autonameow launcher script has executable permission"

assert_true '"$AUTONAMEOW_RUNNER" >/dev/null' \
            "The autonameow launcher script can be started with no arguments"

assert_true '"$AUTONAMEOW_RUNNER" | grep -q -- "--help"' \
            "[TC005] autonameow should print how to get help when started with no arguments"

assert_true '"$AUTONAMEOW_RUNNER" --help | head -n 1 | grep -q "usage"' \
            "[TC005] autonameow should display usage information when started with \"--help\""

assert_true '"$AUTONAMEOW_RUNNER" --help | grep -q "dry-run"' \
            "[TC001] autonameow should provide a \"--dry-run\" option"

assert_true '"$AUTONAMEOW_RUNNER" --interactive 2>/dev/null' \
            "[TC013] autonameow should provide a \"--interactive\" option"



calculate_statistics
logmsg "Completed the Command-Line Interface test suite tests in ${SECONDS} seconds"
