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

# Runs static analysis on YAML sources using 'yamllint'.

set -o errexit -o nounset -o pipefail

readonly EXITSTATUS_INTERNAL_ERROR=70


command -v git &>/dev/null || exit "$EXITSTATUS_INTERNAL_ERROR"
command -v yamllint &>/dev/null || exit "$EXITSTATUS_INTERNAL_ERROR"
command -v xargs &>/dev/null || exit "$EXITSTATUS_INTERNAL_ERROR"


(
    cd -- "$(
        command git rev-parse --show-toplevel
    )" || exit "$EXITSTATUS_INTERNAL_ERROR"

    # Ignore "known bad" sample configuration files.
    command git ls-files '*.yaml' ':!:*bad_*.yaml' -z |
    command xargs -0 yamllint -c ./.yamllint
)
