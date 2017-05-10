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

if ! source "${SELF_DIR}/common_utils.sh"
then
    echo "Shared test utility library is missing. Aborting .." 1>&2
    exit 1
fi


# Make sure required executables are available.
if ! command -v "pytest" >/dev/null 2>&1
then
    echo "This script requires \"pytest\" to run. Exiting .." 1>&2
    exit 1
else
    # Workaround for pytest crashing when writing something other than stdout ..
    _pytesthelp="$(pytest --help 2>&1)"
    if ! grep -q -- '--html' <<< "$_pytesthelp"
    then
        echo "This script requires \"pytest-html\" to generate HTML reports." 1>&2
        echo "Install using pip by executing:  pip3 install pytest-html"
        exit 1
    fi
fi


_timestamp="$(date "+%Y-%m-%dT%H%M%S")"
_unittest_log="${AUTONAMEOW_TESTRESULTS_DIR}/unittest_log_${_timestamp}.html"
if [ -e "$_unittest_log" ]
then
    echo "File exists: \"${_unittest_log}\" .. Aborting" >&2
    exit 1
fi


# Run tests and generate HTML report
( cd "$AUTONAMEOW_ROOT_DIR" && PYTHONPATH=autonameow:tests pytest --html="${_unittest_log}" )

if [ -s "$_unittest_log" ]
then
    echo "Wrote unit test HTML log file: \"${_unittest_log}\""

    # Write log file name to temporary file, used by other scripts.
    set +o noclobber
    echo "${_unittest_log}" > "${AUTONAMEOW_TESTRESULTS_DIR}/.unittestlog.toreport"
    set -o noclobber

    exit 0
fi




# if ! command -v "aha" >/dev/null 2>&1
# then
#     logmsg "The executable \"aha\" is not available on this system"
#     # logmsg "Skipping converting raw logfiles to HTML .."
#     # exit 1
# fi


# _unittest_rawlog="${AUTONAMEOW_TESTRESULTS_DIR}/unit_stdout_${_timestamp}.raw"
# if [ -e "$_unittest_rawlog" ]
# then
#     echo "File exists: \"${_unittest_rawlog}\" .. Aborting" >&2
#     exit 1
# fi


# ( cd "$AUTONAMEOW_ROOT_DIR" && PYTHONPATH=autonameow:tests pytest --verbose --color=yes 2>&1 >> "$_unittest_rawlog")

# if [ -s "$_unittest_rawlog" ]
# then
#     _unittest_rawlog_html="${_unittest_rawlog}.html"
#
#     if aha --title "autonameow Unit Test Log ${_timestamp}" \
#         < "$_unittest_rawlog" > "$_unittest_rawlog_html"
#     then
#         if [ -s "$_unittest_rawlog_html" ]
#         then
#             logmsg "Wrote HTML log file: \"${_unittest_rawlog_html}\""
#         fi
#     else
#         logmsg 'FAILED to write HTML log file!'
#     fi
# fi
