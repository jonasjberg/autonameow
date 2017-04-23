#!/usr/bin/env bash

#   Copyright(c) 2016-2017 Jonas Sjöberg
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


# This is a (kind of) integration test PROTOTYPE, subject to change.


_AUTONAMEOW="${HOME}/LNU/1DV430_IndividuelltProjekt/src/js224eh-project.git/run.sh"
_TIMESTAMP="$(date +%Y-%m-%d)"


_testfile1='2017-04-03T212516 Gibson is undoubtedly the best cat ever -- dev screenshot macbookpro.png'


printf "\n\n%78.78s %s\n" "=" "Starting integration test 1 .."
"$_AUTONAMEOW" --dry-run --list-all --verbose -- "$_testfile1" 2>&1 | tee out_file01_dryrun-listall-verbose_${_TIMESTAMP}.txt

printf "\n\n%78.78s %s\n" "=" "Starting integration test 2 .."
"$_AUTONAMEOW" --dry-run --list-all --debug -- "$_testfile1" 2>&1   | tee out_file01_dryrun-listall-debug_${_TIMESTAMP}.txt


