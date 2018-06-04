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

# Runs static analysis on bash scripts using 'shellcheck'.

set -o nounset -o pipefail

if ! command -v shellcheck >/dev/null 2>&1
then
    cat >&2 <<EOF

[ERROR] The executable "shellcheck" is not available on this system.
        Please install "shellcheck" before running this script.


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



# Checks to ignore for the integration test "suite" scripts:
#
# SC2016: Expressions don't expand in single quotes, use double quotes for that.
#
find "${AUTONAMEOW_ROOT_DIR}/tests/integration" -type f -name '*.sh' -print0 \
    | sort -z | xargs -0 shellcheck -s bash -e 'SC2016' --


# Find all other shell scripts.
find "${AUTONAMEOW_ROOT_DIR}/tests" "${AUTONAMEOW_ROOT_DIR}/bin" "${AUTONAMEOW_ROOT_DIR}/devscripts" \
    -type f -name '*.sh' -not -path '*/tests/integration/*' -print0 \
    | sort -z | xargs -0 shellcheck -s bash --


