#!/usr/bin/env bash

# Copyright(c) 2016-2017 Jonas Sjöberg
# https://github.com/jonasjberg
# http://www.jonasjberg.com
# University mail: js224eh[a]student.lnu.se
# _____________________________________________________________________________
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
# _____________________________________________________________________________
#

SELF="$(basename "$0")"

if [ "$#" -ne "1" ] || [ ! -e "$1" ]
then
    echo "USAGE: $SELF [PYTHON_PROGRAM]"
    echo "Lists modules imported by the specified Python program."
    echo "Imports used by a simple \"no-op\" program is used to filter the"
    echo "listing.  The idea is to get rid of default standard libraries."
    echo "NOTE:  This method *might* be thoroughly unsound and misguided."
    # TODO: Figure out if this is stupid.
    exit 1
fi


# Searches the verbose output for module imports, sorts and makes a list.
# Then another trivial Python program is executed, and a similar module listing
# is produced.  This second listing is used to filter the first listing;
# the "trivial program" module listing is used a wordlist in the 'grep -vFf'
# call by means of process substitution.

python3 -v "$1" 2>&1 | grep -Eo "^import\ \'[A-Za-z0-9]+" | sort -u | \
while IFS='\n' read -r _line
do
    _module="${_line#import \'}"
    echo "$_module"
done | grep -vFf <(python3 -v -c 'print("no-op")' 2>&1 | grep -Eo "^import\ \'[A-Za-z0-9]+" | sort -u | while IFS='\n' read -r __line ; do __module="${__line#import \'}" ; echo "$__module" ; done)

