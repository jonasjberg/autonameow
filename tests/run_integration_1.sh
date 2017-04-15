#!/usr/bin/env bash
# This file is part of autonameow.
# Copyright 2016-2017, Jonas Sjoberg.


# This is a (kind of) integration test PROTOTYPE, subject to change.


_AUTONAMEOW="${HOME}/LNU/1DV430_IndividuelltProjekt/src/js224eh-project.git/run.sh"
_TIMESTAMP="$(date +%Y-%m-%d)"


_testfile1='2017-04-03T212516 Gibson is undoubtedly the best cat ever -- dev screenshot macbookpro.png'


printf "\n\n%78.78s %s\n" "=" "Starting integration test 1 .."
"$_AUTONAMEOW" --dry-run --list-all --verbose -- "$_testfile1" 2>&1 | tee out_file01_dryrun-listall-verbose_${_TIMESTAMP}.txt

printf "\n\n%78.78s %s\n" "=" "Starting integration test 2 .."
"$_AUTONAMEOW" --dry-run --list-all --debug -- "$_testfile1" 2>&1   | tee out_file01_dryrun-listall-debug_${_TIMESTAMP}.txt


