#!/usr/bin/env bash

#   Copyright(c) 2016-2020 Jonas Sjöberg <autonameow@jonasjberg.com>
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


# Initialize counters every time this script is sourced by the test suites.
suite_tests_count=0
suite_tests_passed=0
suite_tests_failed=0


# Should be called once at the start of a test run.
aw_utils.initialize_logging()
{
    if [ ! -d "$AUTONAMEOW_TESTRESULTS_DIRPATH" ]
    then
        printf 'Not a directory: "%s" .. Aborting\n' "$AUTONAMEOW_TESTRESULTS_DIRPATH" >&2
        exit 1
    fi

    # Export variables to be used by all sourcing scripts during this test run.
    AUTONAMEOW_INTEGRATION_TIMESTAMP="$(date "+%Y-%m-%dT%H%M%S")"
    export AUTONAMEOW_INTEGRATION_TIMESTAMP

    AUTONAMEOW_INTEGRATION_LOG="${AUTONAMEOW_TESTRESULTS_DIRPATH}/integration_log_${AUTONAMEOW_INTEGRATION_TIMESTAMP}.raw"
    export AUTONAMEOW_INTEGRATION_LOG

    aw_utils.log_msg "Logging to file: \"${AUTONAMEOW_INTEGRATION_LOG}\""
}

aw_utils.initialize_global_stats()
{
    if ! AUTONAMEOW_INTEGRATION_STATS="$(realpath -e -- "$(mktemp -t aw_test_stats.XXXXXX)")"
    then
        printf 'Unable to create temporary global statistics file .. Aborting\n' >&2
        exit 1
    fi

    aw_utils.log_msg "Writing global statistics to file: \"${AUTONAMEOW_INTEGRATION_STATS}\""
    export AUTONAMEOW_INTEGRATION_STATS

    # Set total, passed and failed to 0
    printf '0 0 0\n' >| "$AUTONAMEOW_INTEGRATION_STATS"
}

# Print message to stdout and append message to AUTONAMEOW_INTEGRATION_LOG.
# ANSI escape codes are allowed and included in the log file.
#
# Conditional piping inside the subshell allows executing only this file, in
# which case AUTONAMEOW_INTEGRATION_LOG will be undefined and the 'tee' call is
# skipped. In this case no log file is written do disk.
#
# shellcheck disable=SC2015
aw_utils.log_msg_timestamped()
{
    local _timestamp
    _timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
    printf '%s %s\n' "$_timestamp" "$*" |

    ( [ ! -z "${AUTONAMEOW_INTEGRATION_LOG:-}" ] && tee -a "$AUTONAMEOW_INTEGRATION_LOG" || cat )
}

aw_utils.log_msg()
{
    printf '%s\n' "$*" | (
        [ -n "${AUTONAMEOW_INTEGRATION_LOG:-}" ] && tee -a "$AUTONAMEOW_INTEGRATION_LOG" || cat
    )
}

aw_utils.log_msg_separator()
{
    aw_utils.log_msg "$(printf '=%.0s' {1..80})"
}

aw_utils.log_msg_separator_thin()
{
    aw_utils.log_msg "$(printf '~%.0s' {1..80})"
}

aw_utils.log_test_suite_results_summary()
{
    local -r _name="$1"
    local -r _execution_time="$2"
    local _highlight_red

    aw_utils.log_msg_separator_thin

    _highlight_red=''
    if [ "$suite_tests_failed" -eq "0" ]
    then
        aw_utils.log_msg "${C_BOLD}${C_GREEN}[ ALL TESTS PASSED ]${C_RESET}"
    else
        aw_utils.log_msg "${C_BOLD}${C_RED}[ SOME TESTS FAILED ]${C_RESET}"
        _highlight_red="${C_RED}"
    fi

    aw_utils.log_msg "$(printf "${C_BOLD}Test Suite Summary:  %d total, %d passed, ${_highlight_red}%d failed${C_RESET}" \
              "$suite_tests_count" "$suite_tests_passed" "$suite_tests_failed")"
    aw_utils.log_msg "${C_BOLD}Completed the ${_name} test suite tests in ${_execution_time} ms${C_RESET}"
    aw_utils.log_msg_separator
}

aw_utils.log_total_results_summary()
{
    local -r _execution_time="$1"
    local -r _tests_count="$2"
    local -r _tests_passed="$3"
    local -r _tests_failed="$4"
    local _highlight_red

    aw_utils.log_msg_separator_thin

    _highlight_red=''
    if [ "$_tests_failed" -eq "0" ]
    then
        aw_utils.log_msg "${C_BOLD}${C_GREEN}[ ALL TEST SUITE(S) TESTS PASSED ]${C_RESET}"
    else
        aw_utils.log_msg "${C_BOLD}${C_RED}[ SOME TEST SUITE(S) TESTS FAILED ]${C_RESET}"
        _highlight_red="${C_RED}"
    fi

    local _duration
    local _seconds
    _seconds="$((_execution_time / 1000))"
    _duration="$(printf '%02dh:%02dm:%02ds\n' \
               $((_seconds % 86400 / 3600))   \
               $((_seconds % 3600 / 60))      \
               $((_seconds % 60)))"

    aw_utils.log_msg "$(printf "${C_BOLD}Total Test Summary:  %d total, %d passed, ${_highlight_red}%d failed${C_RESET}" \
              "$_tests_count" "$_tests_passed" "$_tests_failed")"
    aw_utils.log_msg "${C_BOLD}Completed all tests in ${_duration}  (${_execution_time} ms)${C_RESET}"
    aw_utils.log_msg_separator
}

# Logs a test failure message and increments counters.
aw_utils.test_fail()
{
    aw_utils.log_msg "${C_RED}FAIL:${C_RESET}" "$*"
    suite_tests_failed="$((suite_tests_failed + 1))"
    suite_tests_count="$((suite_tests_count + 1))"
}

# Logs a test success message and increments counters.
aw_utils.test_pass()
{
    aw_utils.log_msg "${C_GREEN}PASS:${C_RESET}" "$*"
    suite_tests_passed="$((suite_tests_passed + 1))"
    suite_tests_count="$((suite_tests_count + 1))"
}

aw_utils.update_global_test_results()
{
    while IFS=' ' read -r _count _pass _fail
    do
        _total_count="$((_count + suite_tests_count))"
        _total_passed="$((_pass + suite_tests_passed))"
        _total_failed="$((_fail + suite_tests_failed))"
    done < "$AUTONAMEOW_INTEGRATION_STATS"

    printf '%d %d %d\n' "$_total_count" "$_total_passed" "$_total_failed" >| "$AUTONAMEOW_INTEGRATION_STATS"
}

aw_utils.assert_true()
{
    ( eval "$1" &>/dev/null ) >/dev/null
    local _eval_exitstatus="$?"
    shift

    if [ "$_eval_exitstatus" -ne '0' ]
    then
        aw_utils.test_fail "$*"
    else
        aw_utils.test_pass "$*"
    fi
}

aw_utils.assert_false()
{
    ( eval "$1" &>/dev/null ) >/dev/null
    local _eval_exitstatus="$?"
    shift

    if [ "$_eval_exitstatus" -ne '0' ]
    then
        aw_utils.test_pass "$*"
    else
        aw_utils.test_fail "$*"
    fi
}

aw_utils.current_unix_time()
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
              *) { printf 'ERROR: Unsupported Operating System!\n' 1>&2 ; exit 1 ; } ;;
    esac
}

# Returns the time delta in milliseconds.
aw_utils.calculate_execution_time()
{
    local -r _time_start="$1"
    local -r _time_end="$2"
    printf '%s\n' "$(((_time_end - _time_start) / 1000000))"
}

aw_utils.samplefile_abspath()
{
    [ -d "$AUTONAMEOW_SAMPLEFILES_DIRPATH" ] || exit 70
    realpath --canonicalize-existing -- "${AUTONAMEOW_SAMPLEFILES_DIRPATH}/${1}"
}

# Test a bunch of '[ -d "foo" ]'-style assertions at once.
# For instance;  'aw_utils.assert_bulk_test "/foo/bar" e f r'
# is equivalent to three separate assertions with messages, etc.
#
# shellcheck disable=SC2016
aw_utils.assert_bulk_test()
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
        aw_utils.assert_true '[ "$_exp" "$_file" ]' "Path \"${_file}\" ${_msg}"
    done
}

aw_utils.command_exists()
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

aw_utils.assert_has_command()
{
    local -r _cmd_name="$1"
    aw_utils.assert_true 'aw_utils.command_exists "$_cmd_name"' \
                "System provides executable command \"${_cmd_name}\""
}
