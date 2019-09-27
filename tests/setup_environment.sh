#!/usr/bin/env bash

#   Copyright(c) 2016-2019 Jonas Sjöberg <autonameow@jonasjberg.com>
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


_autonameow_setup_environment_main()
{
    local _self_relative_filepath
    local _self_absolute_filepath
    _self_relative_filepath="${BASH_SOURCE[${#BASH_SOURCE[@]} - 1]}"
    _self_absolute_filepath="$(
        dirname -- "$(realpath -- "$_self_relative_filepath")"
    )"

    # Absolute path to the autonameow source root.
    AUTONAMEOW_ROOT_DIRPATH="$(realpath -- "${_self_absolute_filepath}/..")"

    unset _self_relative_filepath
    unset _self_absolute_filepath

    if [ ! -d "$AUTONAMEOW_ROOT_DIRPATH" ]
    then
        printf '[ERROR] Not a directory: "%s"\n' "$AUTONAMEOW_ROOT_DIRPATH" >&2
        return 1
    fi
    export AUTONAMEOW_ROOT_DIRPATH

    # Absolute path to the main executable for running autonameow.
    export AUTONAMEOW_RUNNER="${AUTONAMEOW_ROOT_DIRPATH}/bin/autonameow"

    # Absolute path to the "samplefiles" directory.
    export AUTONAMEOW_SAMPLEFILES_DIR="${AUTONAMEOW_ROOT_DIRPATH}/tests/samplefiles"

    # Create the test results directory if missing and export the absolute path.
    AUTONAMEOW_TESTRESULTS_DIR="${AUTONAMEOW_ROOT_DIRPATH}/docs/test_results/"
    [ ! -d "$AUTONAMEOW_TESTRESULTS_DIR" ] && mkdir -p "$AUTONAMEOW_TESTRESULTS_DIR"
    export AUTONAMEOW_TESTRESULTS_DIR

    return 0
}


_autonameow_setup_environment_main
_autonameow_setup_environment_main_retval=$?

# Handle either case of this script being sourced or executed.
if [ "$0" != "$BASH_SOURCE" ]
then
    return $_autonameow_setup_environment_main_retval
else
    exit $_autonameow_setup_environment_main_retval
fi
