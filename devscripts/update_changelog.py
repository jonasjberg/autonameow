#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

import os
import re
import subprocess
import sys

import util
from core import types
from util import text

'''
Helper utility for updating the change log from git log entries.
'''

CHANGELOG_BASENAME = 'CHANGES.txt'

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

SELFNAME = str(os.path.basename(__file__))
_THIS_DIR = os.path.abspath(os.path.dirname(__file__))
AUTONAMEOW_SRC_ROOT = os.path.normpath(os.path.join(_THIS_DIR, os.pardir))

changelog_path = os.path.join(AUTONAMEOW_SRC_ROOT, CHANGELOG_BASENAME)


GIT_LOG_FORMAT_SEP_FIELD = '%x1f'
GIT_LOG_FORMAT_SEP_RECORD = '%x1e'
GIT_COMMIT_FIELDS = ['id', 'lauthor_name', 'author_email', 'date', 'subject', 'body']
GIT_LOG_FORMAT = ['%H', '%an', '%ae', '%ad', '%s', '%b']
GIT_LOG_FORMAT = GIT_LOG_FORMAT_SEP_FIELD.join(GIT_LOG_FORMAT) + GIT_LOG_FORMAT_SEP_RECORD


class ChangelogEntry(object):
    def __init__(self, subject, body):
        self.subject = subject
        self.body = body or ''

        assert self.subject

    def __eq__(self, other):
        if self.subject == other.subject:
            if self.body == other.body:
                return True

        return False

    def __str__(self):
        if self.body:
            return self.subject + '\n' + self.body
        return self.subject


def parse_git_log(git_log_string):
    log = str(git_log_string)
    log = log.strip('\n\x1e').split('\x1e')
    log = [row.strip().split('\x1f') for row in log]
    log = [dict(zip(GIT_COMMIT_FIELDS, row)) for row in log]
    return log


def git_log_for_range(hash_first, hash_second):
    _commit_range = '{}..{}'.format(hash_first, hash_second)
    stdout = subprocess.check_output(
        ['git', 'log', '--format="{}"'.format(GIT_LOG_FORMAT), _commit_range]
    )
    return types.force_string(stdout.strip())



def get_previous_version_tag():
    stdout = subprocess.check_output(
        ['git', 'describe', '--abbrev=0', '--tags']
    )
    return types.force_string(stdout.strip())


def get_commit_for_tag(tag_name):
    stdout = subprocess.check_output(
        ['git', 'rev-list', '-n', '1', tag_name]
    )
    return types.force_string(stdout.strip())



def is_readable_file(file_path):
    return os.path.isfile(file_path) and os.access(file_path, os.R_OK)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        prog=SELFNAME,
        epilog='"{}" -- Change log utility.'.format(SELFNAME)
    )

    argument_group_actions = parser.add_mutually_exclusive_group()
    opts = parser.parse_args(sys.argv[1:])

    # Make sure that the changelog file exists.
    if not is_readable_file(changelog_path):
        print('File does not exist or is not readable: "{!s}"'.format(_path),
              file=sys.stderr)
        sys.exit(EXIT_FAILURE)

    if not util.is_executable('git'):
        print('This script requires "qit" to run. Exiting ..',
              file=sys.stderr)
        sys.exit(EXIT_FAILURE)


    exit_status = EXIT_SUCCESS

    _prev_tag = get_previous_version_tag()
    _prev_tag_hash = get_commit_for_tag(_prev_tag)
    _current_hash = util.git_commit_hash()
    # print('Previous version tag: {!s}'.format(_prev_tag))
    # print('Previous version tag commit hash: {!s}'.format(_prev_tag_hash))
    # print('Current commit hash: {!s}'.format(_current_hash))

    _git_log = git_log_for_range(_prev_tag_hash, _current_hash)

    parsed_git_log = parse_git_log(_git_log)
    log_entries = list()
    for commit in parsed_git_log:
        _subject = commit.get('subject')
        _body = commit.get('body')

        if not _subject:
            continue

        cle = ChangelogEntry(_subject, _body)
        if not cle in log_entries:
            log_entries.append(cle)

    INDENT = ' ' * 7
    for _le in log_entries:
        print(text.indent('- ' + _le.subject, amount=7))
        print(text.indent(_le.body, amount=9))
        if _le.body:
            print()
    print('=' * 80)

    sys.exit(exit_status)
