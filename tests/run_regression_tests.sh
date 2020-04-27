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

set -o nounset

self_dirpath="$(realpath --canonicalize-existing -- "$(dirname -- "$0")")"
readonly self_dirpath

# shellcheck source=tests/setup_environment.sh
if ! source "${self_dirpath}/setup_environment.sh"
then
    cat >&2 <<EOF

[ERROR] Unable to source "${self_dirpath}/setup_environment.sh"
        Environment variable setup script is missing. Aborting ..

EOF
    exit 1
fi


(
    cd "$AUTONAMEOW_ROOT_DIRPATH" &&
    PYTHONPATH=autonameow:tests \
    python3 tests/regression/regression_runner.py "$@"
)
