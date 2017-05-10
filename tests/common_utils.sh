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



# Get absolute path to the autonameow source root.
AUTONAMEOW_ROOT_DIR="$( ( cd "$SELF_DIR" && realpath -e -- ".." ) )"
if [ ! -d "$AUTONAMEOW_ROOT_DIR" ]
then
    echo "Not a directory: \"${AUTONAMEOW_ROOT_DIR}\" .. Aborting" >&2
    exit 1
else
    export AUTONAMEOW_ROOT_DIR
fi

# Get absolute path to the test results directory and make sure it is valid.
AUTONAMEOW_TESTRESULTS_DIR="$( ( cd "$AUTONAMEOW_ROOT_DIR" && realpath -e -- "./docs/test_results/" ) )"
if [ ! -d "$AUTONAMEOW_TESTRESULTS_DIR" ]
then
    echo "Not a directory: \"${AUTONAMEOW_TESTRESULTS_DIR}\" .. Aborting" >&2
    exit 1
else
    export AUTONAMEOW_TESTRESULTS_DIR
fi

# Get absolute path to the project wiki source root.
#
# NOTE: Hardcoded path! "AUTONAMEOW_WIKI_ROOT_DIR" must be changed
#       to the correct path to the wiki repository on your system.
#
AUTONAMEOW_WIKI_ROOT_DIR="${HOME}/Dropbox/LNU/1DV430_IndividuelltProjekt/src/js224eh-project.wiki.git"
if [ ! -d "$AUTONAMEOW_WIKI_ROOT_DIR" ]
then
    cat >&2 <<EOF

Not a directory: "${AUTONAMEOW_WIKI_ROOT_DIR}" ..

  NOTE: You must set the variable "AUTONAMEOW_WIKI_ROOT_DIR" in
        "common_utils.sh" to the full path of the autonameow wiki
        repository root on this system.
EOF

    exit 1
else
    export AUTONAMEOW_WIKI_ROOT_DIR
fi
