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

set -o nounset

SELF_DIRPATH="$(realpath -e "$(dirname "$0")")"

if ! source "${SELF_DIRPATH}/setup_environment.sh"
then
    cat >&2 <<EOF

[ERROR] Unable to source "${SELF_DIRPATH}/setup_environment.sh"
        Environment variable setup script is missing. Aborting ..

EOF
    exit 1
fi


(
    cd "$AUTONAMEOW_ROOT_DIR" &&
    PYTHONPATH=autonameow:tests \
    python3 tests/regression/regression_runner.py "$@"
)
