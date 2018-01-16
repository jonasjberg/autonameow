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


set -o noclobber -o nounset -o pipefail


SOURCE_ROOT="${HOME}/LNU/1DV430_IndividuelltProjekt/src/js224eh-project.git"
WIKI_ROOT="${HOME}/LNU/1DV430_IndividuelltProjekt/src/js224eh-project.wiki.git"

cat >&2 <<EOF

  CAUTION:  Do NOT run this script haphazaradly! ABORT NOW!

  PRE-FLIGHT CHECKLIST:

    * Set the variables "SOURCE_ROOT" and "WIKI_ROOT" in this script to
      the proper paths on the running system.
    * Make sure ALL repositories are clean.
    * Do manual run first to make sure nothing fails unexpectedly.

EOF

read -rsp $'Continue? (ctrl-c aborts)\n' -n 1 key


[ -d "$SOURCE_ROOT" ] || { echo "Invalid source root; ABORTING" 2>&1 ; exit 1 ; }
[ -d "$WIKI_ROOT" ]   || { echo "Invalid wiki root; ABORTING"   2>&1 ; exit 1 ; }


(
current_date="$(date "+%Y-%m-%d")"
cd "$SOURCE_ROOT" && \
tests/run_all_tests.sh && \
devscripts/convert-html-to.pdf.sh && \
git add --all docs/test_results/*${current_date}*.{html,pdf} && \
git commit -m 'Add HTML and PDF unit/integration test reports.' && \
cd "$WIKI_ROOT" && \
git add Test-Results.md && git commit -m 'Add HTML and PDF unit/integration test reports.'
)

