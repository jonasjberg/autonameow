#!/usr/bin/env bash

# 'run.sh' -- autonameow launcher script
# ======================================
# This file is part of autonameow.
# Copyright(c) 2016-2017 Jonas Sjöberg
# https://github.com/jonasjberg
# http://www.jonasjberg.com
# University mail: js224eh[a]student.lnu.se
#
# Shell wrapper to use when executing autonameow from shortcuts, icons, desktop
# environment, other scripts, etc.  You could also launch autonameow by
# invoking Python directly, like so:  python3 <absolute path to main module>


# Make sure that Python 3 is available.
if ! command -v python3 >/dev/null 2>&1
then
    echo "[ERROR] This program requires Python v3.x to run."
    echo "        Please install python3 and make sure it is executable."
    exit 1
fi


# Get the absolute path of the main module.
#
# NOTE: The version of readlink shipped with MacOS does not have the '-f'
#       option. Description from the "readlink (GNU coreutils) 8.25" manpage:
#
#       -f, --canonicalize
#       canonicalize by following every symlink in every component of
#       the given name recursively; all but the last component must exist
#
if readlink --version 2>/dev/null | grep -q 'GNU coreutils'
then
    # Using GNU coreutils version of readlink.
    AUTONAMEOW_PATH="$(dirname -- "$(readlink -fn -- "$0")")"
else
    # Running on MacOS.

    # TODO: Untange symlinks and get an absolute path.
    AUTONAMEOW_PATH="$(dirname -- "$0")"
fi


# Make sure that the resulting path is accessible.
(cd "$AUTONAMEOW_PATH") 2>/dev/null 
if [ "$?" -ne "0" ]
then
    echo "[ERROR] Unable to cd to AUTONAMEOW_PATH: \"${AUTONAMEOW_PATH}\"" >&2
    exit 1
fi


# Execute the main module.
python3 "${AUTONAMEOW_PATH}/autonameow" "$@"

