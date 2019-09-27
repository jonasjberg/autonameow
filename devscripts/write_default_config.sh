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

set -o noclobber -o nounset -o pipefail


SELF_DIRPATH="$(realpath -e -- "$(dirname -- "$0")")"

# Get absolute path to the autonameow source root.
if [ -z "${AUTONAMEOW_ROOT_DIR:-}" ]
then
    AUTONAMEOW_ROOT_DIR="$(realpath -e -- "${SELF_DIRPATH}/..")"
fi

if [ ! -d "$AUTONAMEOW_ROOT_DIR" ]
then
    printf '[ERROR] Not a directory: "%s"\n' "$AUTONAMEOW_ROOT_DIR"   >&2
    printf '        Unable to set "AUTONAMEOW_ROOT_DIR". Aborting.\n' >&2
    exit 1
fi


dest_path="${AUTONAMEOW_ROOT_DIR}/tests/samplefiles/configs/default.yaml"
if [ -e "$dest_path" ]
then
    echo "Destination exists: \"${dest_path}\""

    _ts="$(date "+%Y-%m-%dT%H%M%S")"
    _move_dest="${AUTONAMEOW_ROOT_DIR}/notes/test_files_default_config_${_ts}.yaml"
    mv -nvi -- "$dest_path" "$_move_dest" || exit 1
fi


(
    cd "${AUTONAMEOW_ROOT_DIR}/autonameow" || exit 1
    PYTHONPATH=. python3 core/config/default_config.py --write-default "$dest_path"
)

