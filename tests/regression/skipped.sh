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

self_basename="$(basename -- "$0")"
self_dirpath="$(realpath -e -- "$(dirname -- "$0")")"
readonly self_basename
readonly self_dirpath


# Default configuration.
option_clear_all_skipped='false'


print_usage_info()
{
    cat <<EOF

"$self_basename"  --  skipped test helper

  USAGE:  $self_basename ([OPTIONS])

  OPTIONS:  -h   Display usage information and exit.
            -c   Clear ("unskip") all skipped tests.
                 Deletes all 'skip'-files.

  All options are optional. Default behaviour is to list any
  skipped regression tests.

EOF
}


if [ "$#" -eq "0" ]
then
    printf '(USING DEFAULTS -- "%s -h" for usage information)\n\n' "$self_basename"
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


declare -a common_find_flags=(-xdev -mindepth 2 -maxdepth 2 -type f -name skip)


printf 'Currently skipped regression tests:\n'
while IFS= read -r -d '' skipfile_path
do
    basename -- "$(dirname -- "$skipfile_path")"
done < <(find "$self_dirpath" "${common_find_flags[@]}" -print0 | sort -z)


if [ "$option_clear_all_skipped" == 'true' ]
then
    printf '\nClearing all skipped tests .. '

    if find "$self_dirpath" "${common_find_flags[@]}" -delete
    then
        printf '[SUCCESS]\n'
    else
        printf '[FAILURE]\n'
    fi
fi

