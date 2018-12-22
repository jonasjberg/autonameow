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

command -v smother &> /dev/null || {
    printf 'First do "pip3 install smother" ..\n'
    exit 1
}

[[ $# -eq 0 ]] && {
    cat <<EOF

    USAGE: $(basename -- "$0") [PATH]

    Where PATH is something like "autonameow/core/master_provider"
    *without* any trailing extension.

    Just run "smother" directly, just make sure to run the tests
    once like below, then do any number of "smother lookup" calls
    without the delay of running the unit tests between calls ..

EOF
    exit 0
}

PYTHONPATH=autonameow:tests py.test --smother autonameow tests/unit/test_*.py
PYTHONPATH=autonameow:tests smother lookup "$@"
