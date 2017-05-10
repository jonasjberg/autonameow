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


# TODO: This should not be a dummy file ..
dummy_markdown_report="${AUTONAMEOW_TESTRESULTS_DIR}/dummy_test_report_summary.md"
report_append_printf()
{
    printf "$*" | tee -a "$dummy_markdown_report"
}

report_append()
{
    tee -a "$dummy_markdown_report"
}

if [ "$count_fail" -eq "0" ]
then
    report_append_printf '\n\n'

    if [ -f "${AUTONAMEOW_TESTRESULTS_DIR}/.integrationlog.toreport" ]
    then
        # Read file contents; the path to the most recent integration test log.
        _int_log_path="$( < "${AUTONAMEOW_TESTRESULTS_DIR}/.integrationlog.toreport" )"
        if [ ! -f "$_int_log_path" ]
        then
            echo "Not a file: \"${_int_log_path}\". Aborting .." 1>&2
            exit 1
        fi

        # TODO: This is still incomplete and does not work as intended.
        report_append_printf '### Integration Test Report\n'
        report_append_printf "Read from file: \`${_int_log_path}\`\n"
        report_append_printf '\n\nSTART Testing HTML to markdown conversion with pandoc .. \n'
        pandoc -f html -t markdown "$_int_log_path" | report_append
        report_append_printf '\n\nDONE Testing .. \n'
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

        # TODO: This is still incomplete and does not work as intended.
        report_append_printf '### Unit Test Report\n'
        report_append_printf "Read from file: \`${_unit_log_path}\`\n"
        report_append_printf '\n\nSTART Testing HTML to markdown conversion with pandoc .. \n'
        pandoc -f html -t markdown "$_unit_log_path" | report_append
        report_append_printf '\n\nDONE Testing .. \n'
    fi
    # report_append_printf ''
    # report_append_printf '===============\n'
    # report_append_printf 'Line under header\n'
    # report_append_printf '\n\n'
fi

