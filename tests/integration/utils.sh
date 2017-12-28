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

C_RED="$(tput setaf 1)"
C_GREEN="$(tput setaf 2)"
C_RESET="$(tput sgr0)"
# C_RESET='\E[0m'

# Get the full absolute path to this file.
# Also handles case where the script being sourced.
_self_dir_relative="${BASH_SOURCE[${#BASH_SOURCE[@]} - 1]}"
SELF_DIR="$(dirname -- "$(realpath -e -- "$_self_dir_relative")")"
TEST_DIR="$(dirname -- "$SELF_DIR")"


# Initialize counter variables every time this script is sourced
# by each of the test suites. Used in 'log_test_suite_results_summary'.
tests_total=0
tests_passed=0
tests_failed=0


# Should be called once at the start of a test run. Creates a timestamped log
# file and exports the the log file path as 'AUTONAMEOW_INTEGRATION_LOG'.
initialize_logging()
{
    if [ ! -d "$AUTONAMEOW_TESTRESULTS_DIR" ]
    then
        echo "Not a directory: \"${AUTONAMEOW_TESTRESULTS_DIR}\" .. Aborting" >&2
        exit 1
    fi

    # Export variables to be used by all sourcing scripts during this test run.
    AUTONAMEOW_TEST_TIMESTAMP="$(date "+%Y-%m-%dT%H%M%S")"
    export AUTONAMEOW_TEST_TIMESTAMP

    AUTONAMEOW_INTEGRATION_LOG="${AUTONAMEOW_TESTRESULTS_DIR}/integration_log_${AUTONAMEOW_TEST_TIMESTAMP}.raw"
    export AUTONAMEOW_INTEGRATION_LOG

    logmsg "Logging to file: \"${AUTONAMEOW_INTEGRATION_LOG}\""
}

# Print message to stdout and append message to AUTONAMEOW_INTEGRATION_LOG.
# ANSI escape codes are allowed and included in the log file.

# Conditional piping inside the subshell allows executing only this file, in
# which case AUTONAMEOW_INTEGRATION_LOG will be undefined and the 'tee' call is
# skipped. In this case no log file is written do disk.
logmsg()
{
    local _timestamp="$(date "+%Y-%m-%d %H:%M:%S")"
    printf "%s %s\n" "$_timestamp" "$*" |
    ( [ ! -z "${AUTONAMEOW_INTEGRATION_LOG:-}" ] && tee -a "$AUTONAMEOW_INTEGRATION_LOG" || cat )
}

# Prints out a summary of test results for the currently sourcing script.
log_test_suite_results_summary()
{
    local _name="$1"
    local _execution_time="$2"
    local _highlight_red=''

    logmsg "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    if [ "$tests_failed" -eq "0" ]
    then
        logmsg "${C_GREEN}[ ALL TESTS PASSED ]${C_RESET}"
    else
        logmsg "${C_RED}[ SOME TESTS FAILED ]${C_RESET}"
        _highlight_red="${C_RED}"
    fi

    logmsg "$(printf "Test Suite Summary:  %d total, %d passed, ${_highlight_red}%d failed${C_RESET}" \
              "$tests_total" "$tests_passed" "$tests_failed")"
    logmsg "Completed the "$_name" test suite tests in ${_execution_time} ms"
    logmsg "======================================================================"
}

# Logs a test failure message and increments counters.
test_fail()
{
    logmsg "${C_RED}[FAILED]${C_RESET} " "$*"
    tests_failed="$((tests_failed + 1))"
    tests_total="$((tests_total + 1))"
}

# Logs a test success message and increments counters.
test_pass()
{
    logmsg "${C_GREEN}[PASSED]${C_RESET} " "$*"
    tests_passed="$((tests_passed + 1))"
    tests_total="$((tests_total + 1))"
}

# Evaluates an expression, given as the first argument.
# Calls 'test_fail' if the expression returns NON-zero.
# Calls 'test_pass' if the expression returns zero.
assert_true()
{
    ( eval "${1}" 2>&1 >/dev/null ) >/dev/null
    if [ "$?" -ne "0" ]
    then
        shift ; test_fail "$*"
    else
        shift ; test_pass "$*"
    fi
}

# Evaluates an expression, given as the first argument.
# Calls 'test_pass' if the expression returns NON-zero.
# Calls 'test_fail' if the expression returns zero.
assert_false()
{
    ( eval "${1}" 2>&1 >/dev/null ) >/dev/null
    if [ "$?" -ne "0" ]
    then
        shift ; test_pass "$*"
    else
        shift ; test_fail "$*"
    fi
}

# TODO: Finish this function ..
log_system_info()
{
    local _os_name="$(uname -s)"
    local _os_vers="$(uname -r)"
    local _cpu_info

    case "$OSTYPE" in
        darwin*)
            _cpu_info="$(sysctl -n machdep.cpu.brand_string)" ;;

        linux*|msys)
            if [ -e "/proc/cpuinfo" ]
            then
                _cpu_info="$(cat /proc/cpuinfo | grep -m1 'model name')"
                _cpu_info="${_cpu_info#*:}"
            fi ;;

        *)
            _cpu_info="undetermined" ;;
    esac

    echo "System info: Running ${_os_name} ${_os_vers} on ${_cpu_info}"
}

# Converts the integration test log file to HTML using executable 'aha' if
# available.  Executed at the end of a test run by 'integration_runner.sh'.
convert_raw_log_to_html()
{
    if ! command -v "aha" >/dev/null 2>&1
    then
        logmsg "The executable \"aha\" is not available on this system"
        logmsg "Skipping converting raw logfiles to HTML .."
        exit 1
    fi

    if [ -z "${AUTONAMEOW_INTEGRATION_LOG:-}" ] \
    || [ ! -f "$AUTONAMEOW_INTEGRATION_LOG" ]
    then
        echo "Logging has not been initialized. Aborting .." 1>&2
        return 1
    fi

    _html_integration_log="${AUTONAMEOW_INTEGRATION_LOG%.*}.html"
    _html_title="autonameow Integration Test Log ${AUTONAMEOW_TEST_TIMESTAMP}"

    if aha --title "$_html_title" \
        < "$AUTONAMEOW_INTEGRATION_LOG" | sed 's///g' > "$_html_integration_log"
    then
        if [ -s "$_html_integration_log" ]
        then
            logmsg "Wrote integration test log HTML file: \"${_html_integration_log}\""
            rm -- "$AUTONAMEOW_INTEGRATION_LOG"

            # Write log file name to temporary file, used by other scripts.
            set +o noclobber
            echo "${_html_integration_log}" > "${AUTONAMEOW_TESTRESULTS_DIR}/.integrationlog.toreport"
            set -o noclobber
        fi
    else
        logmsg 'FAILED to write HTML log file!'
    fi
}

# Searches the contents of a file for "TODOs" -- 'TODO', 'FIXME' or 'XXX'.
# The file should be given as the first argument.
# Returns ZERO if the file contains TODOs, otherwise non-zero.
grep_todos()
{
    grep -q "\(TODO\|FIXME\|XXX\).*" -- "$1"
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

# Get the absolute path to a file in the "$SRCROOT/test_files" directory.
# Expects the first and only argument to be the basename of the desired file.
abspath_testfile()
{
    ( cd "$AUTONAMEOW_ROOT_DIR" && realpath -e "test_files/${1}" )
}

# Takes the basename of a logfile as the first and only argument.
# Any dates matching 'YYYY-MM-DDTHHMMSS' are returned as 'YYYY-MM-DD HH:MM:SS'.
get_timestamp_from_basename()
{
    local ts="$(grep -Eo -- "20[0-9]{2}-[0-9]{2}-[0-9]{2}T[0-9]{6}" <<< "$1")"
    sed 's/\([0-9]\{4\}\)-\([0-9]\{2\}\)-\([0-9]\{2\}\)T\([0-9]\{2\}\)\([0-9]\{2\}\)\([0-9]\{2\}\)/\1-\2-\3 \4:\5:\6/' <<< "$ts"
}

# Test a bunch of '[ -d "foo" ]'-style assertions at once.
# For instance;  'bulk_assert_test "/foo/bar" e f r'
# is equivalent to three separate assertions with messages, etc.
bulk_assert_test()
{
    local _file="$1"
    shift

    while [ "$#" -gt "0" ]
    do
        case "$1" in
            d) _exp='-d' ; _msg='exists and is a directory'                ;;
            r) _exp='-r' ; _msg='exists and read permission is granted'    ;;
            w) _exp='-w' ; _msg='exists and write permission is granted'   ;;
            x) _exp='-x' ; _msg='exists and execute permission is granted' ;;
            f) _exp='-f' ; _msg='exists and is a regular file'             ;;
            z) _exp='-z' ; _msg='is a zero length string ("undefined")'    ;;
            n) _exp='-n' ; _msg='is a non-zero length string ("defined")'  ;;
            *) _exp='-e' ; _msg='exists'                                   ;;
        esac
        shift

        assert_true "[ "$_exp" "$_file" ]" "Path \"${_file}\" ${_msg}"
    done
}



# Test Cases
# ____________________________________________________________________________
#
# Detect if this script is being sourced by another script.
# Check Bash version for support:   man bash | less -p BASH_SOURCE
# Source:  http://stackoverflow.com/a/2684300/7802196

[[ ${BASH_VERSINFO[0]} -le 2 ]] && { echo 'No BASH_SOURCE array variable' 1>&2 ; exit 1 ; }
[[ "${BASH_SOURCE[0]}" != "${0}" ]] # && echo "script ${BASH_SOURCE[0]} is being sourced ..."


if [[ "${BASH_SOURCE[0]}" == "${0}" ]]
then
    logmsg "Starting self-tests .."
    assert_true  "[ "0" -eq "0" ]" '(Internal Test) Expect success ..'
    assert_true  "[ "1" -eq "0" ]" '(Internal Test) Expect failure ..'
    assert_false "[ "1" -eq "0" ]" '(Internal Test) Expect success ..'
    assert_false "[ "1" -ne "0" ]" '(Internal Test) Expect failure ..'
    logmsg "Finished self-tests!"
fi

