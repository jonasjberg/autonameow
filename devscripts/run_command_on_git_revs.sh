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

set -o nounset -o pipefail -o errexit


self_basename="$(basename -- "$0")"
readonly self_basename

if [ "$#" -ne '3' ]
then
    cat >&2 <<EOF

  USAGE:  $self_basename [HASH_NEWEST] [HASH_OLDEST] [COMMAND]

  Checks out git revisions from HASH_NEWEST to HASH_OLDEST (inclusive)
  in sequence and executes COMMAND after checking out each revision.
  Note that revision HASH_NEWEST must be more recent than HASH_OLDEST.

  This script exits if COMMAND returns non-zero . The repository might
  be left in a "detached HEAD" state if COMMAND returns non-zero or is
  terminated by SIGINT (ctrl-c) or any other signal.

  Primary usage for this script is to pass a test runner as COMMAND,
  which allows finding revisions that fail the tests and leaves this
  revision checked out for further examination.
  Prefer using 'git bisect' if the use case doesn't require checking
  out all revisions sequentially!

EOF
    exit 0
fi

HASH_NEWEST="$1"  # most recent revision
HASH_OLDEST="$2"  # older revision
COMMAND="$3"


# TODO: [incomplete] Probably missing some checks.
if ! ( git status 2>&1 ) >/dev/null
then
    printf 'Not currently in a git repository\n'
    exit 1
fi

if ! git diff-files --quiet
then
    printf 'Working tree has changes that could be staged\n'
    exit 1
fi

if ! git diff-index --quiet --cached HEAD
then
    printf 'Repository has staged (uncommitted) changes\n'
    exit 1
fi

if ! initial_branch="$(git symbolic-ref --short -q HEAD)"
then
    printf 'You are in "detached HEAD" state --- Aborting!\n'
    exit 1
fi


# Display warning and wait for user confirmation.
cat >&2 <<EOF

  CAUTION:  Do NOT run this script haphazaradly! ABORT NOW!

  This script might clobber untracked and/or unstaged files!
  Make sure that the repository is clean before running.

EOF
read -rsp $'  Press ANY key to continue or ctrl-c to abort\n\n' -n 1 key


# Get revision hashes within range.
revisions=$(git rev-list --reverse ${HASH_OLDEST}..${HASH_NEWEST})
if [ -z "$revisions" ]
then
    printf 'Got no revisions for range %s..%s\n' "$HASH_OLDEST" "$HASH_NEWEST"
    exit 1
fi


checkout_revision_and_eval_command()
{
    local -r _rev="$1"
    # printf 'Checking out revision %s\n' "$_rev"
    git checkout --quiet "$_rev"
    eval "$COMMAND"
}

# Range does not include this revision.
checkout_revision_and_eval_command "$HASH_OLDEST"

# Iterate over revisions.
for rev in $revisions
do
    checkout_revision_and_eval_command "$rev"
done

git checkout --quiet $initial_branch
