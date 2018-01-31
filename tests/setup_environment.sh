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

set -o nounset


# Get the full absolute path to this file.
# Also handles case where the script being sourced.
_self_dir_relative="${BASH_SOURCE[${#BASH_SOURCE[@]} - 1]}"
self_path="$(dirname -- "$(realpath -e -- "$_self_dir_relative")")"


error_msg_exit()
{
    printf '[ERROR] %s: "%s"\n' "$1" "$2" >&2
    exit 1
}


# Absolute path to the autonameow source root.
AUTONAMEOW_ROOT_DIR="$( ( cd "$self_path" && realpath -e -- ".." ) )"
if [ ! -d "$AUTONAMEOW_ROOT_DIR" ]
then
    error_msg_exit 'Not a directory' "$AUTONAMEOW_ROOT_DIR"
fi
export AUTONAMEOW_ROOT_DIR

# Absolute path to the main executable for running autonameow.
AUTONAMEOW_RUNNER="${AUTONAMEOW_ROOT_DIR}/bin/autonameow.sh"
if [ ! -f "$AUTONAMEOW_RUNNER" ]
then
    error_msg_exit 'Not a file' "$AUTONAMEOW_RUNNER"
fi
export AUTONAMEOW_RUNNER

# Absolute path to the "test_files" directory.
AUTONAMEOW_TESTFILES_DIR="${AUTONAMEOW_ROOT_DIR}/test_files"
if [ ! -d "$AUTONAMEOW_TESTFILES_DIR" ]
then
    error_msg_exit 'Not a directory' "$AUTONAMEOW_TESTFILES_DIR"
fi
export AUTONAMEOW_TESTFILES_DIR

# Create the test results directory if missing and export the absolute path.
AUTONAMEOW_TESTRESULTS_DIR="${AUTONAMEOW_ROOT_DIR}/docs/test_results/"
[ ! -d "$AUTONAMEOW_TESTRESULTS_DIR" ] && mkdir -p "$AUTONAMEOW_TESTRESULTS_DIR"
if [ ! -d "$AUTONAMEOW_TESTRESULTS_DIR" ]
then
    error_msg_exit 'Not a directory' "$AUTONAMEOW_TESTRESULTS_DIR"
fi
export AUTONAMEOW_TESTRESULTS_DIR
