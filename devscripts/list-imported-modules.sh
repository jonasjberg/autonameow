#!/usr/bin/env bash

#   Copyright(c) 2016-2018 Jonas Sjöberg
#   Personal site:   http://www.jonasjberg.com
#   GitHub:          https://github.com/jonasjberg
#   University mail: js224eh[a]student.lnu.se
#   _________________________________________________________________________
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
#   _________________________________________________________________________

set -o noclobber -o nounset -o pipefail -o errexit

SELF="$(basename "$0")"


# TODO: Figure out if this is stupid. Still not sure whether it is stupid.
# TODO: UPDATE 2017-11-09 Still not sure whether this is stupid..


if [ "$#" -ne "1" ] || [ ! -e "$1" ]
then
    cat <<EOF

  USAGE:  ${SELF} [PATH TO PYTHON PROGRAM]

  Lists modules imported by the specified Python program.
  Imports used by a simple "no-op" program is used to filter the
  listing.  The idea is to get rid of default standard libraries.

  NOTE:  This method *might* be thoroughly unsound and misguided.

EOF
    exit 1
fi


# Grabs imports by searching the verbose output for module imports.
# Matching is _NOT_ robust to future changes of the output format!

# Get a reference list of imports from a trivial program.
trivial_imports="$(python3 -v -c 'print("no-op")' 2>&1 |
    grep -Eo -- "^import\ \'[A-Za-z0-9]+" |
    sort -u |
    while IFS=$'\n' read -r __line
    do
        __module="${__line#import \'}"
        echo "$__module"
    done)"

# Get list of imports from the specified Python program.
python3 -v "$1" 2>&1 |
grep -Eo -- "^import\ \'[A-Za-z0-9]+" |
sort -u |
while IFS=$'\n' read -r _line
do
    _module="${_line#import \'}"
    echo "$_module"
done |
# Filter out the trivial program imports.
grep -vF -- "$trivial_imports"


exit 0

