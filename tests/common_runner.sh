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



count_fail=0

printf "Running integration test runner .."
if ${SELF_DIR}/integration_runner.sh 2>&1 >/dev/null
then
    printf " [FINISHED]\n"
else
    printf " [FAILED]\n"
    count_fail="$((count_fail + 1))"
fi

printf "Running unit test runner .."
if ${SELF_DIR}/unit_runner.sh 2>&1 >/dev/null
then
    printf " [FINISHED]\n"
else
    printf " [FAILED]\n"
    count_fail="$((count_fail + 1))"
fi


wiki_report_results="${AUTONAMEOW_WIKI_ROOT_DIR}/Test-Results.md"
report_append()
{
    printf "$*" >> "$wiki_report_results"
}

if [ "$count_fail" -eq "0" ]
then
    # Insert heading with todays date if not already present.
    _date="$(date "+%Y-%m-%d")"
    if ! grep -q "^### ${_date}$" "$wiki_report_results"
    then
        report_append "\n### ${_date}\n\n"
    fi

    # Root path used in the links that are added to the report.
    REMOTE_TEST_RESULTS="https://github.com/1dv430/js224eh-project/blob/master/docs/test_results"

    if [ -f "${AUTONAMEOW_TESTRESULTS_DIR}/.integrationlog.toreport" ]
    then
        # Read file contents; the path to the most recent integration test log.
        _int_log_path="$( < "${AUTONAMEOW_TESTRESULTS_DIR}/.integrationlog.toreport" )"
        if [ ! -f "$_int_log_path" ]
        then
            echo "Not a file: \"${_int_log_path}\". Aborting .." 1>&2
            exit 1
        fi

        _int_log_basename="$(basename -- "${_int_log_path}")"
        _int_log_timestamp="$(get_timestamp_from_basename "${_int_log_basename}")"
        _int_log_link="${REMOTE_TEST_RESULTS}/${_int_log_basename}"
        report_append "* [${_int_log_timestamp}] [Integration Test Report](${_int_log_link})\n"
    fi

    if [ -f "${AUTONAMEOW_TESTRESULTS_DIR}/.unittestlog.toreport" ]
    then
        # Read file contents; the path to the most recent unit test log.
        _unit_log_path="$( < "${AUTONAMEOW_TESTRESULTS_DIR}/.unittestlog.toreport" )"
        if [ ! -f "$_unit_log_path" ]
        then
            echo "Not a file: \"${_unit_log_path}\". Aborting .." 1>&2
            exit 1
        fi

        _unit_log_basename="$(basename -- "${_unit_log_path}")"
        _unit_log_timestamp="$(get_timestamp_from_basename "${_unit_log_basename}")"
        _unit_log_link="${REMOTE_TEST_RESULTS}/${_unit_log_basename}"
        report_append "* [${_unit_log_timestamp}] [Unit Test Report](${_unit_log_link})\n"
    fi
fi

