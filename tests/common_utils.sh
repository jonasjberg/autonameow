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

# Get the full absolute path to this file.
# Also handles case where the script being sourced.
_self_dir_relative="${BASH_SOURCE[${#BASH_SOURCE[@]} - 1]}"
SELF_DIR="$(dirname -- "$(realpath -e -- "$_self_dir_relative")")"


C_RED="$(tput setaf 1)"
C_GREEN="$(tput setaf 2)"
C_RESET="$(tput sgr0)"


# Get absolute path to the autonameow source root.
AUTONAMEOW_ROOT_DIR="$( ( cd "$SELF_DIR" && realpath -e -- ".." ) )"
if [ ! -d "$AUTONAMEOW_ROOT_DIR" ]
then
    echo "Not a directory: \"${AUTONAMEOW_ROOT_DIR}\" .. Aborting" >&2
    exit 1
else
    export AUTONAMEOW_ROOT_DIR
fi

# Get absolute path to the test results directory and make sure it is valid.
AUTONAMEOW_TESTRESULTS_DIR="$( ( cd "$AUTONAMEOW_ROOT_DIR" && realpath -e -- "./docs/test_results/" ) )"
if [ ! -d "$AUTONAMEOW_TESTRESULTS_DIR" ]
then
    echo "Not a directory: \"${AUTONAMEOW_TESTRESULTS_DIR}\" .. Aborting" >&2
    exit 1
else
    export AUTONAMEOW_TESTRESULTS_DIR
fi

# Get absolute path to the project wiki source root.
#
# NOTE: Hardcoded path! "AUTONAMEOW_WIKI_ROOT_DIR" must be changed
#       to the correct path to the wiki repository on your system.
#
AUTONAMEOW_WIKI_ROOT_DIR="${HOME}/Dropbox/LNU/1DV430_IndividuelltProjekt/src/js224eh-project.wiki.git"
if [ ! -d "$AUTONAMEOW_WIKI_ROOT_DIR" ]
then
    cat >&2 <<EOF

Not a directory: "${AUTONAMEOW_WIKI_ROOT_DIR}" ..

  NOTE: You must set the variable "AUTONAMEOW_WIKI_ROOT_DIR" in
        "common_utils.sh" to the full path of the autonameow wiki
        repository root on this system.
EOF

    exit 1
else
    export AUTONAMEOW_WIKI_ROOT_DIR
fi

# Get the absolute path to a file in the "$SRCROOT/test_files" directory.
# Expects the first and only argument to be the basename of the desired file.
abspath_testfile()
{
    ( cd "$SELF_DIR" && realpath -e "../test_files/${1}" )
}

# Takes the basename of a logfile as the first and only argument.
# Any dates matching 'YYYY-MM-DDTHHMMSS' are returned as 'YYYY-MM-DD HH:MM:SS'.
get_timestamp_from_basename()
{
    local ts="$(grep -Eo -- "20[0-9]{2}-[0-9]{2}-[0-9]{2}T[0-9]{6}" <<< "$1")"
    sed 's/\([0-9]\{4\}\)-\([0-9]\{2\}\)-\([0-9]\{2\}\)T\([0-9]\{2\}\)\([0-9]\{2\}\)\([0-9]\{2\}\)/\1-\2-\3 \4:\5:\6/' <<< "$ts"
}

# Runs a "task" (evaluates an expression) and prints messages.
#
# 1. First argument controls message printing and supression of expression
#    output. Everything but 'true' results in passing all output.
# 2. Second argument is a message that describes the task being performed.
#    Message formatting is controlled by the first argument. If 'quiet' is
#    'true', a single line is printed for each task. Otherwise, the same
#    line is printed before running the tasks and then again after.
# 3. Third argument is an arbitrary expression to evalute.
#    If the expression evaluates to 0 the task is considered to have succeeded,
#    any other return code is considered a failure.
run_task()
{
    local _opt_quiet="$1"
    local _msg="$2"
    local _cmd="$3"

    # Print tasks is starting message.
    local FMT
    [ "$_opt_quiet" = 'true' ] && local FMT='%s ..' || local FMT='%s ..\n'
    printf "$FMT" "$_msg"

    # Run task and check exit status.
    if [ "$_opt_quiet" != 'true' ]
    then
        eval "${_cmd}"
    else
        eval "${_cmd}" 2>&1 >/dev/null
    fi
    local _retcode="$?"
    if [ "$_retcode" -ne '0' ]
    then
        count_fail="$((count_fail + 1))"
    fi

    # Print task has ended message.
    [ "$_opt_quiet" = 'true' ] || printf "${_msg} .."
    if [ "$_retcode" -eq '0' ]
    then
        printf " ${C_GREEN}[FINISHED]${C_RESET}\n"
    else
        printf " ${C_RED}[FAILED]${C_RESET}\n"
    fi
}

# Returns the current time as a UNIX timestamp.
current_unix_time()
{
    # The 'date' command differs between versions; the GNU coreutils version
    # uses '+%N' to print nanoseconds, which is missing in the BSD version
    # shipped with MacOS.  Circumvent hackily by inlining Python call ..
    #
    # NOTE: This should probably only be done once for performance.
    #       Lets just assume we're mostly interested in relative measurements.

    case "$OSTYPE" in
        darwin*) python -c 'import time ; t="%.9f"%time.time() ; print t.replace(".","")';;
         linux*) date "+%s%N" ;;
           msys) date "+%s%N" ;; # NOTE: Not a target OS!
              *) { echo 'ERROR: Unsupported Operating System!' 1>&2 ; exit 1 ; } ;;
    esac
}

# Calculates the execution time by taking the difference of two unix
# timestamps.  The expected arguments are start and end times.
# Returns the time delta in milliseconds.
calculate_execution_time()
{
    local _time_start="$1"
    local _time_end="$2"
    echo "$(((${_time_end} - ${_time_start}) / 1000000))"
}
