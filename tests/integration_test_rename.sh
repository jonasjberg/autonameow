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
SELF_DIR="$(dirname "$0")"

# Source 'integration_utils.sh', which in turn sources 'common_utils.sh'.
if ! source "${SELF_DIR}/integration_utils.sh"
then
    echo "Integration test utility library is missing. Aborting .." 1>&2
    exit 1
fi



# Test Cases
# ____________________________________________________________________________

# Store current time for later calculation of total execution time.
time_start="$(current_unix_time)"

logmsg "Started \"${SELF}\""
logmsg "Running the Rename Files test suite .."



_temp_dir="$(mktemp -d)"
_expected_name="${_temp_dir}/2010-01-31T161251 a cat lying on a rug.jpg"
assert_true 'cp -n -- "$SAMPLE_JPG_FILE" ${_temp_dir}/smulan.jpg 2>&1 >/dev/null' \
            "rename_sample_jpg_file Test setup should succeed"

assert_true '( "$AUTONAMEOW_RUNNER" --automagic -- "${_temp_dir}/smulan.jpg" 2>&1 ) >/dev/null && [ -e "$_expected_name" ]' \
            "rename_sample_jpg_file [TC010][TC011] \""$(basename -- "${SAMPLE_JPG_FILE}")"\" should be renamed to \""$(basename -- "${_expected_name}")"\""

assert_true '[ -f "${_temp_dir}/smulan.jpg" ] && rm -- "${_temp_dir}/smulan.jpg" ; [ -f "$_expected_name" ] && rm -- "$_expected_name" || true' \
            "rename_sample_jpg_file Test teardown should succeed"



# Calculate total execution time.
time_end="$(current_unix_time)"
total_time="$((($time_end - $time_start) / 1000000))"

calculate_statistics
logmsg "Completed the Rename Files test suite tests in ${total_time} ms"
