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

# Runs basic spell checking on the sources.

set -o nounset -o pipefail


if ! command -v aspell >/dev/null 2>&1
then
    cat >&2 <<EOF

[ERROR] The executable "aspell" is not available on this system.
        Please install "aspell" before running this script.


EOF
    exit 1
fi



# Get absolute path to the autonameow source root.
if [ -z "${AUTONAMEOW_ROOT_DIR:-}" ]
then
    SELF_DIR="$(realpath -e "$(dirname "$0")")"
    AUTONAMEOW_ROOT_DIR="$( ( cd "$SELF_DIR" && realpath -e -- ".." ) )"
fi

if [ ! -d "$AUTONAMEOW_ROOT_DIR" ]
then
    printf '[ERROR] Not a directory: "%s" .. Aborting\n' "$AUTONAMEOW_ROOT_DIR" >&2
    exit 1
fi



# ______________________________________________________________________________
#
# Search source code for misspelled words. These are based on the git history.
# # git log --all -p -- *.py | grep -- '^-.*#.*' | grep -v '^-$' | grep -oi -- '[[:alpha:]]\+' | tr '[:upper:]' '[:lower:]' | sort -u | aspell list -a | less

# pushd "$AUTONAMEOW_ROOT_DIR" || exit 1
# {
#
#
#     find autonameow bin devscripts docs tests -xdev -type f \
#          \( -name "*.py" -or -name "*.sh" -or -name "*.md" \) -exec cat '{}' + \
#             | grep -v -- '^[[:space:]]\?$'
# }
# popd



# Concatenate all Python files, excluding those in sub-directories
# under 'thirdparty'. Contents of 'thirdparty' itself is included.
#
# Skip lines that are empty or contain only whitespace
#
# Remove all leading whitespace.
normalized_text="$(find "${AUTONAMEOW_ROOT_DIR}" -xdev -type f -not -path "*/thirdparty/*/*" \( -name "*.md" -or -name "*.py" \) -exec cat '{}' + \
                 | grep -v -- '^[[:space:]]\?$' \
                 | sed -e 's/^[[:space:]]*//' \
                 | tr '[:upper:]' '[:lower:]')"


# Check comments with aspell. Lists misspelled words.
# grep --line-buffered -- '# \?.*' <<< "$normalized_text" | sort -u | aspell list -a | sort -u



check_sources_do_not_match()
{
    local -r _pattern="$1"
    grep -- "$_pattern" <<< "$normalized_text"
}

declare -a PREVIOUSLY_MISSPELLED_WORDS=(
'autonamew'
'autoameow'
'autonamoew'
'automaticaly'
'bytesting'
'dependant'
'doucment'
'expeeted'
'expceted'
'filname'
'filobject'
'implment'
'meowuirs'
'mockup'
'occured'
'ocurred'
'objecst'
'probabilty'
'retuens'
'_return_non_'
'unavaiable'
)


for misspelled_word in "${PREVIOUSLY_MISSPELLED_WORDS[@]}"
do
    if check_sources_do_not_match "$misspelled_word"
    then
        exit 1
    fi
done
