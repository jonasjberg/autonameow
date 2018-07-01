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

SELF_BASENAME="$(basename "$0")"
SELF_DIR="$(realpath -e "$(dirname "$0")")"


# Default configuration.
option_clear_all_skipped='false'


print_usage_info()
{
    cat <<EOF

"${SELF_BASENAME}"  --  skipped test helper

  USAGE:  ${SELF_BASENAME} ([OPTIONS])

  OPTIONS:  -h   Display usage information and exit.
            -c   Clear ("unskip") all skipped tests.
                 Deletes all 'skip'-files.

  All options are optional. Default behaviour is to list any
  skipped regression tests.

EOF
}


if [ "$#" -eq "0" ]
then
    printf '(USING DEFAULTS -- "%s -h" for usage information)\n\n' "$SELF_BASENAME"
else
    while getopts hc opt
    do
        case "$opt" in
            h) print_usage_info ; exit 0 ;;
            c) option_clear_all_skipped='true' ;;
        esac
    done

    shift $(( OPTIND - 1 ))
fi


printf 'Currently skipped regression tests:\n'
( cd "$SELF_DIR" && find . -xdev -type f -name 'skip' -printf '%P\n' | sed 's/\/skip//' )

if [ "$option_clear_all_skipped" == 'true' ]
then
    printf '\nClearing all skipped tests .. '
    if ( cd "$SELF_DIR" && find . -xdev -type f -name 'skip' -delete )
    then
        printf '[SUCCESS]\n'
    else
        printf '[FAILURE]\n'
    fi
fi

