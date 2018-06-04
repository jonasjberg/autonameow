#!/usr/bin/env bash

#   Copyright(c) 2016-2018 Jonas Sjöberg
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

# Generate statistics on the project source code using "cloc".

set -o nounset

IGNORE_DIRS='test_files,thirdparty,license,docs,notes,.idea,.cache'


if ! command -v cloc >/dev/null 2>&1
then
    cat >&2 <<EOF

[ERROR] The executable "cloc" is not available on this system.
        Please install "cloc" before running this script.


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
    echo "[ERROR] Not a directory: \"${AUTONAMEOW_ROOT_DIR}\" .. Aborting" >&2
    exit 1
fi


(
    cd "$AUTONAMEOW_ROOT_DIR" && \
    cloc --exclude-dir="$IGNORE_DIRS" .
)

