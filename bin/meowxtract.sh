#!/usr/bin/env bash

# 'meowxtract.sh' -- Stand-alone autonameow Content Extraction
# ============================================================
# Copyright(c) 2016-2018 Jonas Sjöberg
# https://github.com/jonasjberg
# http://www.jonasjberg.com
# University mail: js224eh[a]student.lnu.se
# _____________________________________________________________________________
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
# _____________________________________________________________________________

set -o nounset -o pipefail

# Make sure that Python 3 is available.
if ! command -v python3 >/dev/null 2>&1
then
    cat >&2 <<EOF

[ERROR] This program requires Python v3.x to run.
        Please install python3 and make sure it is executable.

EOF
    exit 1
fi


# Check if running on a supported/target operating system.
case $OSTYPE in
    darwin*) ;;
     linux*) ;;
          *) cat >&2 <<EOF

[WARNING] Running on unsupported operating system "$OSTYPE"
          autonameow has NOT been thoroughly tested on this OS!

EOF
;;
esac


# NOTE: The version of readlink shipped with MacOS does not have the '-f'
#       option. Description from the "readlink (GNU coreutils) 8.25" manpage:
#
#       -f, --canonicalize
#       canonicalize by following every symlink in every component of
#       the given name recursively; all but the last component must exist
#
if readlink --version 2>/dev/null | grep -q 'GNU coreutils'
then
    # Using GNU coreutils version of readlink.
    self_abspath="$(dirname "$(realpath -e -- "$0")")"
    AUTONAMEOW_PATH="$( ( cd "$self_abspath" && realpath -e -- ".." ) )"
else
    # Not using GNU coreutils readlink or readlink is not available.
    self_abspath="$(python -c "import os; print(os.path.realpath(os.path.join(\"$0\", os.pardir)))")"
    AUTONAMEOW_PATH="$(dirname -- "${self_abspath}")"
fi


# Make sure that the resulting path is accessible.
if ! (cd "$AUTONAMEOW_PATH") 2>/dev/null
then
    printf '[ERROR] Unable to cd to AUTONAMEOW_PATH: "%s"\n' "$AUTONAMEOW_PATH" >&2
    exit 1
fi


# TODO: Avoid using launcher-scripts to setup "$PYTHONPATH" ..
# Execute stand-alone content extraction.
PYTHONPATH="${AUTONAMEOW_PATH}/autonameow" \
    python3 "${AUTONAMEOW_PATH}/autonameow/extractors/meowxtract.py" "$@"

