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

# grep wrapper for searching the entire project for TODOs.

set -o nounset


SELF_BASENAME="$(basename -- "$0")"

# Get absolute path to the autonameow source root.
if [ -z "${AUTONAMEOW_ROOT_DIR:-}" ]
then
    self_dirpath="$(realpath -e -- "$(dirname -- "$0")")"
    AUTONAMEOW_ROOT_DIR="$(realpath -e -- "${self_dirpath}/..")"
fi

if [ ! -d "$AUTONAMEOW_ROOT_DIR" ]
then
    printf '[ERROR] Not a directory: "%s"\n' "$AUTONAMEOW_ROOT_DIR"   >&2
    printf '        Unable to set "AUTONAMEOW_ROOT_DIR". Aborting.\n' >&2
    exit 1
fi


if [ "$#" -ne "1" ]
then
    cat <<EOF

USAGE:  $SELF_BASENAME [PATTERN]
        Where [PATTERN] is inserted in "TODO: .*[PATTERN].*",
        which is passed to grep along with other options.

EOF
    exit 0
fi


# -H  Always print filename headers with output lines.
grep --color=auto \
     --exclude-dir={.git,.idea,.cache,docs,license,notes,samplefiles,thirdparty} \
     --include={*.py,*.sh} \
     --ignore-case \
     --recursive \
     --line-number \
     --binary-file=without-match \
     -H \
     -- "TODO: .*${1}.*" "$AUTONAMEOW_ROOT_DIR" 2>/dev/null | sort
