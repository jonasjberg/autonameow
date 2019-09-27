#!/usr/bin/env bash

#   Copyright(c) 2016-2019 Jonas Sjöberg <autonameow@jonasjberg.com>
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

# Check text file style violations, whitespace, line separators, etc.
# Returns 1 at first failing check. Returns 0 if all checks pass.

set -o nounset -o noclobber


if [ -n "$TERM" ] && command -v tput &>/dev/null
then
    C_GREEN="$(tput setaf 2)"
    C_RED="$(tput setaf 1)"
    C_RESET="$(tput sgr0)"
fi
# Set to empty string if unset or empty.
C_GREEN="${C_GREEN:+"$C_GREEN"}"
C_RED="${C_RED:+"$C_RED"}"
C_RESET="${C_RESET:+"$C_RESET"}"


# Get absolute path to the autonameow source root.
if [ -z "${AUTONAMEOW_ROOT_DIR:-}" ]
then
    self_dirpath="$(realpath -e -- "$(dirname -- "$0")")"
    AUTONAMEOW_ROOT_DIR="$(realpath -e -- "${self_dirpath}/..")"
fi

if [ ! -d "$AUTONAMEOW_ROOT_DIR" ]
then
    printf '[ERROR] Not a directory: "%s"\n' "$AUTONAMEOW_ROOT_DIR"   >&2
    printf '        Unable to set "AUTONAMEOW_ROOT_DIR". Aborting.\n' >&2
    exit 1
fi


msg_failure()
{
    printf "${C_RED}[FAILURE]${C_RESET} %s\\n" "$*"
}

msg_success()
{
    printf "${C_GREEN}[SUCCESS]${C_RESET} %s\\n" "$*"
}


# Check that (most) committed files do not contain carriage returns (\r) (0x0D)
find_files_with_carriage_returns()
{
    git grep -l -I $'\r''$' | grep -v 'samplefiles\|local\|junk\|vendor'
}

if [ "$(find_files_with_carriage_returns | wc -l)" -ne "0" ]
then
    msg_failure 'Files using carriage returns has been committed to git:'
    printf '%s\n' "$(find_files_with_carriage_returns)"
    exit 1
fi


# Get committed text files to check for whitespace issues, then remove quite a few exceptions.
textfiles_to_check=(
    $(git ls-files |
      xargs file --mime-type -- |
      grep ' text/' |
      cut -d':' -f1 |
      grep -v -- 'tests.*\.yaml\|\.md\|test_results\|local\|junk\|samplefiles\|notes\|thirdparty\|.gitmodules\|vendor' |
      grep -v -- 'write_sample_textfiles.py\|test_extractors_text_rtf.py')
)

files_with_trailing_whitespace="$(grep -l "[[:space:]]\+$" -- "${textfiles_to_check[@]}")"
if [ -n "$files_with_trailing_whitespace" ]
then
    msg_failure 'Committed text files has trailing whitespace:'
    printf '%s\n' "$files_with_trailing_whitespace"
    exit 1
fi

files_with_tabs="$(grep -l $'\t' -- "${textfiles_to_check[@]}")"
if [ -n "$files_with_tabs" ]
then
    msg_failure 'Committed text files uses tabs --- SUPER WEAK! Gibson disapproves ..'
    printf '%s\n' "$files_with_tabs"
    exit 1
fi


msg_success 'All checks passed'
exit 0
