#!/usr/bin/env bash


# The version of readlink shipped with MacOS does not have the '-f' option.
# Description from the "readlink (GNU coreutils) 8.25" manpage:
#
#   -f, --canonicalize
#   canonicalize by following every symlink in every component of 
#   the given name recursively; all but the last component must exist

if readlink --version 2>/dev/null | grep -q 'GNU coreutils'
then
    # Using GNU coreutils version of readlink.
    AUTONAMEOW_PATH="$(dirname -- "$(readlink -fn -- "$1")")"
else
    # Running on MacOS, resolving path with perl shim.

    # TODO: This does not work properly for nested symlinks.
    readlinkf() { perl -MCwd -e 'print Cwd::abs_path shift' "$1" ; }
    AUTONAMEOW_PATH="$(dirname -- "$(readlinkf "$1")")"
fi


(cd "$AUTONAMEOW_PATH") 2>/dev/null 
if [ "$?" -ne "0" ]
then
    echo "[ERROR] Unable to cd to AUTONAMEOW_PATH: \"${SUBSHELL_PATH}\"" >&2
    exit 1
fi

python3 "${AUTONAMEOW_PATH}/autonameow" "$@"

