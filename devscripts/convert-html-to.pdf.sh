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

# Converts all HTML test reports to PDF.

set -o noclobber -o nounset -o pipefail

SELF="$(basename "$0")"

# Get the full absolute path to this file.
# Also handles case where the script being sourced.
_self_dir_relative="${BASH_SOURCE[${#BASH_SOURCE[@]} - 1]}"
SELF_DIRPATH="$(dirname -- "$(realpath -e -- "$_self_dir_relative")")"


# Get absolute path to the test results directory and make sure it is valid.
AUTONAMEOW_TESTRESULTS_DIR="$( ( cd "$SELF_DIRPATH" && realpath -e -- "../docs/test_results/" ) )"

if [ ! -d "$AUTONAMEOW_TESTRESULTS_DIR" ]
then
    echo "Not a directory: \"${AUTONAMEOW_TESTRESULTS_DIR}\" .. Aborting" >&2
    exit 1
else
    export AUTONAMEOW_TESTRESULTS_DIR
fi



if ! command -v "wkhtmltopdf" >/dev/null 2>&1
then
    cat >&2 <<EOF

  The executable "wkhtmltopdf" is not available on this system.
       Please install "wkhtmltopdf" before running this script.

EOF
    exit 1
fi



(
    cd "$AUTONAMEOW_TESTRESULTS_DIR"
    for html_file in integration_log_*.html unittest_log_*.html
    do
        [ -f "${html_file}" ] || continue

        dest_file="${html_file%.*}.pdf"
        [ -e "$dest_file" ] && continue

        wkhtmltopdf "$html_file" "${dest_file}"
    done
)
