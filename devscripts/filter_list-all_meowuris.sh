#!/usr/bin/env bash

#   Copyright(c) 2016-2018 Jonas Sjöberg
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

set -o nounset -o pipefail

SELF_BASENAME="$(basename "$0")"


if [ "$#" -eq "0" ]
then
    cat >&2 <<EOF

  USAGE:  ${SELF_BASENAME} [FILE(S)]

  Runs autonameow with the given file(s) and the "--list-all"
  option and filters the output to display a lexicographically
  sorted list of unique MeowURIs.

EOF
    exit 1
fi


AUTONAMEOW_RUNNER='../bin/autonameow.sh'

if [ ! -f "$AUTONAMEOW_RUNNER" ]
then
    cat >&2 <<EOF

  [ERROR] The autonameow runner is not at "$AUTONAMEOW_RUNNER" ..
  Run this script in a manner in which this assumption holds true.

EOF
    exit 1
fi


"$AUTONAMEOW_RUNNER" --list-all --dry-run "$@" 2>/dev/null \
    | grep -Eo '^([0-9a-zA-Z:-]+\.)+.*: ' \
    | cut -d':' -f1- \
    | sed 's/[ \t]*$//' | sed 's/:$//' \
    | sort -u

# Double sed-call strips trailing whitespace, then trailing ':'s.

