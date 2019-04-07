#!/usr/bin/env bash

#   Copyright(c) 2016-2018 Jonas Sjöberg <autonameow@jonasjberg.com>
#   Source repository: https://github.com/jonasjberg/autonameow
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


if [ -n "$TERM" ] && command -v tput &>/dev/null
then
    C_BOLD="$(tput bold)"
    C_GREEN="$(tput setaf 2)"
    C_RED="$(tput setaf 1)"
    C_RESET="$(tput sgr0)"
fi
# Set to empty string if unset or empty.
C_BOLD="${C_BOLD:+"$C_BOLD"}"
C_GREEN="${C_GREEN:+"$C_GREEN"}"
C_RED="${C_RED:+"$C_RED"}"
C_RESET="${C_RESET:+"$C_RESET"}"


# Initialize counter variables every time this script is sourced
# by each of the test suites. Used in 'log_test_suite_results_summary'.
suite_tests_count=0
suite_tests_passed=0
suite_tests_failed=0


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
    AUTONAMEOW_INTEGRATION_TIMESTAMP="$(date "+%Y-%m-%dT%H%M%S")"
    export AUTONAMEOW_INTEGRATION_TIMESTAMP

    AUTONAMEOW_INTEGRATION_LOG="${AUTONAMEOW_TESTRESULTS_DIR}/integration_log_${AUTONAMEOW_INTEGRATION_TIMESTAMP}.raw"
    export AUTONAMEOW_INTEGRATION_LOG

    log_msg "Logging to file: \"${AUTONAMEOW_INTEGRATION_LOG}\""
}

initialize_global_stats()
{
    if ! AUTONAMEOW_INTEGRATION_STATS="$(realpath -e -- "$(mktemp -t aw_test_stats.XXXXXX)")"
    then
        echo 'Unable to create temporary global statistics file .. Aborting' >&2
        exit 1
    fi

    log_msg "Writing global statistics to file: \"${AUTONAMEOW_INTEGRATION_STATS}\""
    export AUTONAMEOW_INTEGRATION_STATS

    # Set total, passed and failed to 0
    echo '0 0 0' >| "$AUTONAMEOW_INTEGRATION_STATS"
}

# Print message to stdout and append message to AUTONAMEOW_INTEGRATION_LOG.
# ANSI escape codes are allowed and included in the log file.
#
# Conditional piping inside the subshell allows executing only this file, in
# which case AUTONAMEOW_INTEGRATION_LOG will be undefined and the 'tee' call is
# skipped. In this case no log file is written do disk.
#
# shellcheck disable=SC2015
log_msg_timestamped()
{
    local _timestamp
    _timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
    printf '%s %s\n' "$_timestamp" "$*" |

    ( [ ! -z "${AUTONAMEOW_INTEGRATION_LOG:-}" ] && tee -a "$AUTONAMEOW_INTEGRATION_LOG" || cat )
}

log_msg()
{
    printf '%s\n' "$*" | (
        [ -n "${AUTONAMEOW_INTEGRATION_LOG:-}" ] && tee -a "$AUTONAMEOW_INTEGRATION_LOG" || cat
    )
}

log_msg_separator()
{
    log_msg "$(printf '=%.0s' {1..80})"
}

log_msg_separator_thin()
{
    log_msg "$(printf '~%.0s' {1..80})"
}


# Prints out a summary of test results for the currently sourcing script.
log_test_suite_results_summary()
{
    local -r _name="$1"
    local -r _execution_time="$2"
    local _highlight_red

    log_msg_separator_thin

    _highlight_red=''
    if [ "$suite_tests_failed" -eq "0" ]
    then
        log_msg "${C_BOLD}${C_GREEN}[ ALL TESTS PASSED ]${C_RESET}"
    else
        log_msg "${C_BOLD}${C_RED}[ SOME TESTS FAILED ]${C_RESET}"
        _highlight_red="${C_RED}"
    fi

    log_msg "$(printf "${C_BOLD}Test Suite Summary:  %d total, %d passed, ${_highlight_red}%d failed${C_RESET}" \
              "$suite_tests_count" "$suite_tests_passed" "$suite_tests_failed")"
    log_msg "${C_BOLD}Completed the ${_name} test suite tests in ${_execution_time} ms${C_RESET}"
    log_msg_separator
}

# Prints out a total test results ummary for all tests.
log_total_results_summary()
{
    local -r _execution_time="$1"
    local -r _tests_count="$2"
    local -r _tests_passed="$3"
    local -r _tests_failed="$4"
    local _highlight_red

    log_msg_separator_thin

    _highlight_red=''
    if [ "$_tests_failed" -eq "0" ]
    then
        log_msg "${C_BOLD}${C_GREEN}[ ALL TEST SUITE(S) TESTS PASSED ]${C_RESET}"
    else
        log_msg "${C_BOLD}${C_RED}[ SOME TEST SUITE(S) TESTS FAILED ]${C_RESET}"
        _highlight_red="${C_RED}"
    fi

    local _duration
    local _seconds
    _seconds="$((_execution_time / 1000))"
    _duration="$(printf '%02dh:%02dm:%02ds\n' \
               $((_seconds % 86400 / 3600))   \
               $((_seconds % 3600 / 60))      \
               $((_seconds % 60)))"

    log_msg "$(printf "${C_BOLD}Total Test Summary:  %d total, %d passed, ${_highlight_red}%d failed${C_RESET}" \
              "$_tests_count" "$_tests_passed" "$_tests_failed")"
    log_msg "${C_BOLD}Completed all tests in ${_duration}  (${_execution_time} ms)${C_RESET}"
    log_msg_separator
}

# Logs a test failure message and increments counters.
test_fail()
{
    log_msg "${C_RED}[FAIL]${C_RESET}" "$*"
    suite_tests_failed="$((suite_tests_failed + 1))"
    suite_tests_count="$((suite_tests_count + 1))"
}

# Logs a test success message and increments counters.
test_pass()
{
    log_msg "${C_GREEN}[PASS]${C_RESET}" "$*"
    suite_tests_passed="$((suite_tests_passed + 1))"
    suite_tests_count="$((suite_tests_count + 1))"
}

update_global_test_results()
{
    while IFS=' ' read -r _count _pass _fail
    do
        _total_count="$((_count + suite_tests_count))"
        _total_passed="$((_pass + suite_tests_passed))"
        _total_failed="$((_fail + suite_tests_failed))"
    done < "$AUTONAMEOW_INTEGRATION_STATS"

    echo "${_total_count} ${_total_passed} ${_total_failed}" >| "$AUTONAMEOW_INTEGRATION_STATS"
}


# Evaluates an expression, given as the first argument.
# Calls 'test_fail' if the expression returns NON-zero.
# Calls 'test_pass' if the expression returns zero.
assert_true()
{
    ( eval "${1}" &>/dev/null ) >/dev/null
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
    ( eval "${1}" &>/dev/null ) >/dev/null
    if [ "$?" -ne "0" ]
    then
        shift ; test_pass "$*"
    else
        shift ; test_fail "$*"
    fi
}

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
        darwin*) python3 -c 'import time ; t="%.9f"%time.time() ; print(t.replace(".",""))';;
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
    local -r _time_start="$1"
    local -r _time_end="$2"
    echo "$(((_time_end - _time_start) / 1000000))"
}

# Get the absolute path to a file in the "$SRCROOT/test_files" directory.
# Expects the first and only argument to be the basename of the desired file.
abspath_testfile()
{
    ( cd "$AUTONAMEOW_ROOT_DIR" && realpath -e "test_files/${1}" )
}

# Test a bunch of '[ -d "foo" ]'-style assertions at once.
# For instance;  'assert_bulk_test "/foo/bar" e f r'
# is equivalent to three separate assertions with messages, etc.
#
# shellcheck disable=SC2016
assert_bulk_test()
{
    local -r _file="$1"
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

        [ -n "$_exp" ] || { printf '\nINTERNAL ERROR! Aborting..\n' ; exit 1 ; }
        [ -n "$_msg" ] || { printf '\nINTERNAL ERROR! Aborting..\n' ; exit 1 ; }
        assert_true '[ "$_exp" "$_file" ]' "Path \"${_file}\" ${_msg}"
    done
}

# Asserts that the given argument would be interpreted as a function if used as
# a command name.
assert_bash_function()
{
    local -r _func_name="$1"
    assert_true '[ "$(type -t "${_func_name}")" = "function" ]' \
                "${_func_name} is a bash function"
}

# Tests that a command or list of commands are available.
# Returns true if ALL commands are available. Else false.
command_exists()
{
    for arg in "$@"
    do
        if ! command -v "$arg" &>/dev/null
        then
            return 1
        fi
    done

    return 0
}

assert_has_command()
{
    local -r _cmd_name="$1"
    assert_true 'command_exists "$_cmd_name"' \
                "System provides executable command \"${_cmd_name}\""
}



# Test Cases
# ____________________________________________________________________________
#
# Detect if this script is being sourced by another script.
# Check Bash version for support:   man bash | less -p BASH_SOURCE
# Source:  http://stackoverflow.com/a/2684300/7802196

[[ ${BASH_VERSINFO[0]} -le 2 ]] && { echo 'No BASH_SOURCE array variable' 1>&2 ; exit 1 ; }
[[ ${BASH_SOURCE[0]} != ${0} ]] # && echo "script ${BASH_SOURCE[0]} is being sourced ..."


if [[ "${BASH_SOURCE[0]}" == "${0}" ]]
then
    log_msg "Starting self-tests .."
    assert_true  '[ "0" -eq "0" ]' '(Internal Test) Expect success ..'
    assert_true  '[ "1" -eq "0" ]' '(Internal Test) Expect failure ..'
    assert_false '[ "1" -eq "0" ]' '(Internal Test) Expect success ..'
    assert_false '[ "1" -ne "0" ]' '(Internal Test) Expect failure ..'
    log_msg "Finished self-tests!"
fi

