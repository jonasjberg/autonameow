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

# Runs static analysis on python sources using 'pylint'.

set -o nounset -o pipefail

if ! command -v pylint >/dev/null 2>&1
then
    cat >&2 <<EOF

[ERROR] The executable "pylint" is not available on this system.
        Please install "pylint" before running this script.


EOF
    exit 1
fi



# Get absolute path to the autonameow source root.
if [ -z "${AUTONAMEOW_ROOT_DIR:-}" ]
then
    self_dirpath="$(realpath -e "$(dirname "$0")")"
    AUTONAMEOW_ROOT_DIR="$( ( cd "$self_dirpath" && realpath -e -- ".." ) )"
fi

if [ ! -d "$AUTONAMEOW_ROOT_DIR" ]
then
    printf '[ERROR] Not a directory: "%s" .. Aborting\n' "$AUTONAMEOW_ROOT_DIR" >&2
    exit 1
fi



(
    # Export variable for use in 'init-hook' call in the 'pylintrc' file.
    export AUTONAMEOW_SYSPATH="${AUTONAMEOW_ROOT_DIR}/autonameow"

    cd "$AUTONAMEOW_ROOT_DIR" && PYTHONPATH=autonameow:tests \
    pylint --rcfile='./devscripts/pylintrc' autonameow bin
)
