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

set -o noclobber -o nounset -o pipefail


SELF_DIR="$(realpath -e "$(dirname "$0")")"

# Get absolute path to the autonameow source root.
AUTONAMEOW_ROOT_DIR="$( ( cd "$SELF_DIR" && realpath -e -- ".." ) )"
if [ ! -d "$AUTONAMEOW_ROOT_DIR" ]
then
    echo "Not a directory: \"${AUTONAMEOW_ROOT_DIR}\" .. Aborting" >&2
    exit 1
fi


dest_path="${AUTONAMEOW_ROOT_DIR}/test_files/configs/default.yaml"
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

