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




C_RED="$(tput setaf 1)"
C_GREEN="$(tput setaf 2)"
C_RESET="$(tput sgr0)"

_SELF_DIR="$(dirname "$0")"


# Get absolute path to log file directory and make sure it is valid.
_LOGFILE_DIR="$( ( cd "$SELF_DIR" && realpath -e -- "../docs/test_results/" ) )"
if [ ! -d "$_LOGFILE_DIR" ]
then
    echo "Not a directory: \"${_LOGFILE_DIR}\" .. Aborting" >&2
    exit 1
fi

# Get absolute path to the log file, used by all sourcing scripts.
_LOGFILE_TIMESTAMP="$(date "+%Y-%m-%dT%H%M%S")"
LOGFILE="${_LOGFILE_DIR}/${_LOGFILE_TIMESTAMP}.txt"
if [ -f "$LOGFILE" ]
then
    echo "File exists: \"${LOGFILE}\" .. Aborting" >&2
    exit 1
fi



tests_total=0
tests_passed=0
tests_failed=0


# Print message to stdout. ANSI escape codes allowed.
printmsg()
{
    local _timestamp="$(date "+%Y-%m-%d %H:%M:%S")"
    printf "%s %s\n" "$_timestamp" "$*"
}

# Append message to LOGFILE.
logmsg()
{
    local _timestamp="$(date "+%Y-%m-%d %H:%M:%S")"
    printf "%s %s\n" "$_timestamp" "$*" >> "$LOGFILE"
}

# Print message to stdout and append to LOGFILE.
msg()
{
    printmsg "$*"
    logmsg "$*"
}

calculate_statistics()
{
    if [ "$tests_failed" -eq "0" ]
    then
        printmsg "${C_GREEN}[ ALL TESTS PASSED ]${C_RESET}"
        logmsg "[ ALL TESTS PASSED ]"
    else
        printmsg "${C_RED}[ SOME TESTS FAILED ]${C_RESET}"
        logmsg "[ SOME TESTS FAILED ]"
    fi

    msg "$(printf "Summary:  %d total, %d passed, %d failed" "$tests_total" "$tests_passed" "$tests_failed")"
}

test_fail()
{
    printmsg "${C_RED}[FAILED]${C_RESET} " "$*"
    logmsg "[FAILED] " "$*"
    tests_failed="$((tests_failed + 1))"
    tests_total="$((tests_total + 1))"
}

test_pass()
{
    printmsg "${C_GREEN}[PASSED]${C_RESET} " "$*"
    logmsg "[PASSED] " "$*"
    tests_passed="$((tests_passed + 1))"
    tests_total="$((tests_total + 1))"
}

assert_true()
{
    eval "${1}"
    if [ "$?" -ne "0" ]
    then
        shift ; test_fail "$*"
    else
        shift ; test_pass "$*"
    fi
}

assert_false()
{
    eval "${1}"
    if [ "$?" -ne "0" ]
    then
        shift ; test_pass "$*"
    else
        shift ; test_fail "$*"
    fi
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
    printmsg "Starting self-tests .."
    assert_true  "[ "0" -eq "0" ]" '(Internal Test) Expect success ..'
    assert_true  "[ "1" -eq "0" ]" '(Internal Test) Expect failure ..'
    assert_false "[ "1" -eq "0" ]" '(Internal Test) Expect success ..'
    assert_false "[ "1" -ne "0" ]" '(Internal Test) Expect failure ..'
    printmsg "Finished self-tests!"
fi

