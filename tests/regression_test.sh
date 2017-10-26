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

# Source 'regression_utils.sh', which in turn sources 'common_utils.sh'.
if ! source "${SELF_DIR}/regression_utils.sh"
then
    echo "Regression test utility library is missing. Aborting .." 1>&2
    exit 1
fi





# validate_regression_test_dir()
# {
#     local _dir="$(
#     if [ ! -d "$regdir" ]
#     then
#         logmsg "Not a directory: \"${regdir}\" .. SKIPPING"
#         continue
#     fi
# 
# }

get_regressiontest_args()
{
    local _dir="$1"
    if [ ! -f "${_dir}/args" ]
    then
        logmsg "2
    fi

}

run_regressiontest()
{
    local _dir="$1"

    _args="${_dir}/${REGTEST_BASENAME_ARGS}"
    if [ ! -f "$_args" ]
    then
        failtest
    fi
}
