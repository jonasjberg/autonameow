#!/usr/bin/env bash

AUTONAMEOW_PATH="$(dirname -- "$(readlink -fn -- "$0")")"

(cd "$AUTONAMEOW_PATH") 2>/dev/null 
if [ "$?" -ne "0" ]
then
    echo "[ERROR] Unable to cd to AUTONAMEOW_PATH: \"${SUBSHELL_PATH}\"" >&2
    exit 1
fi

python3 "${AUTONAMEOW_PATH}/autonameow" "$@"

