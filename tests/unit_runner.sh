#!/usr/bin/env bash

#   Copyright(c) 2016-2017 Jonas Sjöberg
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

SELF="$(basename "$0")"
SELF_DIR="$(realpath -e "$(dirname "$0")")"

# Make sure required executables are available.
if ! command -v "pytest" >/dev/null 2>&1
then
    echo "This script requires \"pytest\" to run. Exiting .." 1>&2
    exit 1
fi


# Get absolute path to log file directory and make sure it is valid.
_LOGFILE_DIR="$( ( cd "$SELF_DIR" && realpath -e -- "../docs/test_results/" ) )"
if [ ! -d "$_LOGFILE_DIR" ]
then
    echo "Not a directory: \"${_LOGFILE_DIR}\" .. Aborting" >&2
    exit 1
fi



_timestamp="$(date "+%Y-%m-%dT%H%M%S")"

_unittest_log="${_LOGFILE_DIR}/unit_${_timestamp}.html"
if [ -e "$_unittest_log" ]
then
    echo "File exists: \"${_unittest_log}\" .. Aborting" >&2
    exit 1
fi


AUTONAMEOW_ROOT_DIR="$( ( cd "$SELF_DIR" && realpath -e -- ".." ) )"
if [ ! -d "$AUTONAMEOW_ROOT_DIR" ]
then
    echo "Unable to get autonameow root directory. Exiting .." 1>&2
    exit 1
fi

# Run tests and generate HTML report
( cd "$AUTONAMEOW_ROOT_DIR" && PYTHONPATH=autonameow:tests pytest --html="${_unittest_log}" )


if [ -s "$_unittest_log" ]
then
    echo "Wrote unit test HTML log file: \"${_unittest_log}\""
    exit 0
fi

