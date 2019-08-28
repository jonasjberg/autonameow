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

# Executes 'vulture' to find unused code.

set -o nounset


if ! command -v vulture &>/dev/null
then
    cat >&2 <<EOF

[ERROR] The executable "vulture" is not available on this system.
        Please install "vulture" before running this script.


EOF
    exit 1
fi


# Get absolute path to the autonameow source root.
if [ -z "${AUTONAMEOW_ROOT_DIR:-}" ]
then
    self_dirpath="$(realpath --canonicalize-existing -- "$(dirname -- "$0")")"
    AUTONAMEOW_ROOT_DIR="$(realpath --canonicalize-existing -- "${self_dirpath}/..")"
fi

if [ ! -d "$AUTONAMEOW_ROOT_DIR" ]
then
    printf '[ERROR] Not a directory: "%s"\n' "$AUTONAMEOW_ROOT_DIR" >&2
    printf '        Unable to set "AUTONAMEOW_ROOT_DIR". Aborting.\n' >&2
    exit 1
fi


(
    cd "$AUTONAMEOW_ROOT_DIR" || exit 1
    vulture --min-confidence=90 --exclude=autonameow/thirdparty autonameow
)
