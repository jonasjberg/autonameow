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

# _______________________________________________________________________
# Very simple and likely broken search of unused functions and methods.
# First finds all 'def DEF_NAME' in Python source files. These files are
# then searched again for anything matching; "DEF_NAME("  or  "=DEF_NAME"
# which is counted as one "usage" of 'DEF_NAME'.
#
# This script does not yield very good results but can help with finding
# methods or functions that are only used by their tests.
# PyCharm and "vulture" probably also have some kind of functionality to
# ignore usage by test code, but I haven't found it yet..
#
# NOTE: Make sure working directory is "AUTONAMEOW_ROOT_DIRPATH/autonameow"

set -o noclobber -o pipefail
SEARCHDIR="${AUTONAMEOW_ROOT_DIRPATH:-.}"
set -o nounset

# Number of usages less or equal to this are included in the results.
MIN_USAGE_COUNT=1


grep_own_python() { grep -hrE --exclude-dir={devscripts,thirdparty,tests} --include "*.py" "$@" "$SEARCHDIR" ; }


grep_own_python -o '^def [a-zA-Z0-9_]+' | cut -f2 -d' ' | while read -r def_name
do
    declare -i def_name_call_count
    def_name_call_count="$(grep_own_python "(${def_name}\(|=${def_name})" | grep -v "def ${def_name}" | wc -l)"

    if [ "$def_name_call_count" -le "$MIN_USAGE_COUNT" ]
    then
        printf '%s  %s\n' "$def_name_call_count" "$def_name"
    fi
done | sort -r
