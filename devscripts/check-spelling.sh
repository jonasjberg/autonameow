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
#
# ______________________________________________________________________________
#
# Searches the sources for previously and/or commonly misspelled words.
# These are based on searching the git history with something like this;
#
#     git log --all -p -- *.py | grep -- '^-.*#.*' | grep -v '^-$' \
#     | grep -oi -- '[[:alpha:]]\+' | tr '[:upper:]' '[:lower:]' | sort -u \
#     | aspell list -a
# ______________________________________________________________________________

set -o nounset -o pipefail


if ! command -v aspell >/dev/null 2>&1
then
    cat >&2 <<EOF

[ERROR] The executable "aspell" is not available on this system.
        Please install "aspell" before running this script.


EOF
    exit 1
fi


SELF_DIRPATH="$(realpath -e "$(dirname "$0")")"

# Get absolute path to the autonameow source root.
if [ -z "${AUTONAMEOW_ROOT_DIR:-}" ]
then
    AUTONAMEOW_ROOT_DIR="$( ( cd "$SELF_DIRPATH" && realpath -e -- ".." ) )"
fi

if [ ! -d "$AUTONAMEOW_ROOT_DIR" ]
then
    printf '[ERROR] Not a directory: "%s"\n' "$AUTONAMEOW_ROOT_DIR" >&2
    exit 1
fi


# Check that a wordlist exists.
wordlist_filepath="${SELF_DIRPATH}/check-spelling-wordlist.txt"
[ -f "$wordlist_filepath" ] || { printf '[ERROR] Wordlist not found at "%s"\n' "$wordlist_filepath" ; exit 1 ; }


declare -i exitstatus
exitstatus=0

while IFS= read -r -d '' filepath
do
    [ -f "$filepath" ] || continue

    # Skip lines that are empty or contain only whitespace
    # Remove all leading whitespace.
    if grep -v -- '^[[:space:]]\?$' "$filepath" \
        | sed -e 's/^[[:space:]]*//' \
        | grep --ignore-case --fixed-strings --file="$wordlist_filepath"
    then
        printf '%s\n\n' "$filepath"
        exitstatus=1
    fi

done < <(find "${AUTONAMEOW_ROOT_DIR}" -xdev -type f \
         -not -path "*/thirdparty/*/*" \( -name "*.md" -or -name "*.py" \) \
         -print0 | sort -z)


# # Check comments with aspell. Lists misspelled words.
# grep --line-buffered -- '# \?.*' <<< "$normalized_text" | sort -u | aspell list -a | sort -u


exit "$exitstatus"
