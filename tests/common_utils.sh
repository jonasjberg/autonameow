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


C_RED="$(tput setaf 1)"
C_GREEN="$(tput setaf 2)"
C_RESET="$(tput sgr0)"


kill_running_task()
{
    kill "$TASK_PID"
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
    local -r _opt_quiet="$1"
    local -r _msg="$2"
    local -r _cmd="$3"

    # Print tasks is starting message.
    if [ "$_opt_quiet" = 'true' ]
    then
        printf '%s ..' "$_msg"
    else
        printf '%s ..\n' "$_msg"
    fi

    # Catch SIGUP (1) SIGINT (2) and SIGTERM (15)
    trap kill_running_task SIGHUP SIGINT SIGTERM

    # Run task and check exit code.
    if [ "$_opt_quiet" != 'true' ]
    then
        eval "${_cmd}" &
        TASK_PID="$!"
    else
        eval "${_cmd}" >/dev/null 2>&1 &
        TASK_PID="$!"
    fi
    wait "$TASK_PID"

    local _retcode="$?"
    if [ "$_retcode" -ne '0' ]
    then
        COUNT_FAIL="$((COUNT_FAIL + 1))"
    fi

    # Print task has ended message, interpreting exit codes as;
    #
    #     0     -- OK
    #     130   -- ABORTED (Terminated by Control-C)
    #     other -- ERROR
    #
    [ "$_opt_quiet" = 'true' ] || printf '%s ..' "$_msg"
    if [ "$_retcode" -eq '0' ]
    then
        # Success
        printf ' %s\n' "${C_GREEN}[FINISHED]${C_RESET}"
    else
        # Failure
        if [ "$_retcode" -eq '130' ]
        then
            printf ' %s' "${C_RED}[ABORTED]${C_RESET}"
        else
            printf ' %s' "${C_RED}[FAILED]${C_RESET}"
        fi
        printf ' (exit code %s)\n' "$_retcode"
    fi
}
