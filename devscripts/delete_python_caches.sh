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

# Delete all '*.pyc' files and '__pycache__' directories.
# Requires user to confirm before files are deleted. Use '--force' to skip.

set -o nounset


if [ -z "${AUTONAMEOW_ROOT_DIRPATH:-}" ]
then
    # Try to get the absolute path to the autonameow source root ..
    self_dirpath="$(realpath -e -- "$(dirname -- "$0")")"
    AUTONAMEOW_ROOT_DIRPATH="$(realpath -e -- "${self_dirpath}/..")"
    unset self_dirpath
fi

if [ ! -d "$AUTONAMEOW_ROOT_DIRPATH" ]
then
    printf '[ERROR] Not a directory: "%s"\n' "$AUTONAMEOW_ROOT_DIRPATH"   >&2
    printf '        Unable to set "AUTONAMEOW_ROOT_DIRPATH". Aborting.\n' >&2
    exit 1
fi


# User must confirm before deleting files unless started with '--force'.
require_user_confirmation='true'
[ "$#" -eq "1" ] && [ "$1" == '--force' ] && require_user_confirmation='false'

if [ "$require_user_confirmation" == 'true' ]
then
    cat >&2 <<EOF

  CAUTION:  Do NOT run this script haphazaradly! ABORT NOW!

  This script DELETES files and directories RECURSIVELY!
  Starting from path: "${AUTONAMEOW_ROOT_DIRPATH}"

  Files matching "*.pyc" and directories named "__pycache__" will be DELETED!

EOF

    read -rsp $'  Press ANY key to continue or ctrl-c to abort\n' -n 1 key
fi


find "$AUTONAMEOW_ROOT_DIRPATH" -xdev -type f -name "*.pyc" -delete
find "$AUTONAMEOW_ROOT_DIRPATH" -xdev -type d -name '__pycache__' -delete

