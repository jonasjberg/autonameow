#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

import datetime
import os
import re
import subprocess
import sys

from core import version
from util import coercers
from util import process
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


GIT_LOG_SEP_FIELD = '\x1f'
GIT_LOG_SEP_RECORD = '\x1e'
GIT_LOG_FORMAT_SEP_FIELD = '%x1f'
GIT_LOG_FORMAT_SEP_RECORD = '%x1e'
GIT_COMMIT_FIELDS = ['id', 'lauthor_name', 'author_email', 'date', 'subject', 'body']
GIT_LOG_FORMAT = ['%H', '%an', '%ae', '%ad', '%s', '%b']
GIT_LOG_FORMAT = GIT_LOG_FORMAT_SEP_FIELD.join(GIT_LOG_FORMAT) + GIT_LOG_FORMAT_SEP_RECORD


class ChangelogEntry(object):
    def __init__(self, subject, body):
        self.subject = subject
        self.body = body or ''
        assert isinstance(self.subject, str)
        assert isinstance(self.body, str)

    def __eq__(self, other):
        if self.subject.lower().strip() == other.subject.lower().strip():
            if self.body.lower().strip() == other.body.lower().strip():
                return True
        return False

    def __str__(self):
        if self.body:
            return self.subject + '\n' + self.body
        return self.subject


class ChangelogEntryClassifier(object):
    @classmethod
    def is_addition(cls, entry):
        SUBJECT_WORDS = ['Add', 'Implement']
        if cls._subject_matches_any(entry, SUBJECT_WORDS):
            return True

        BODY_WORDS = ['Implements']
        if cls._body_matches_any(entry, BODY_WORDS):
            return True

    @classmethod
    def is_change(cls, entry):
        SUBJECT_WORDS = ['Change', 'Modify', 'Remove', 'Rework']
        if cls._subject_matches_any(entry, SUBJECT_WORDS):
            return True

        BODY_WORDS = ['Changes', 'Modifies', 'Removes', 'Reworks']
        if cls._body_matches_any(entry, BODY_WORDS):
            return True

    @classmethod
    def is_fix(cls, entry):
        SUBJECT_WORDS = ['Fix', 'fixes', 'Remove redundant']
        if cls._subject_matches_any(entry, SUBJECT_WORDS):
            return True

        BODY_WORDS = ['Fixes', 'redundant', 'incomplete', 'superfluous']
        if cls._body_matches_any(entry, BODY_WORDS):
            return True

        return False

    @classmethod
    def _subject_matches_any(cls, entry, string_list):
        return any(s in entry.subject for s in string_list)

    @classmethod
    def _body_matches_any(cls, entry, string_list):
        return any(s in entry.body for s in string_list)


def is_blacklisted(entry):
    body = str(entry.body).rstrip('.')
    subject = str(entry.subject).rstrip('.')

    def _subject_match(*args):
        return re.match(*args, subject)

    def _body_match(*args):
        return re.match(*args, body)

    def _any_match(*args):
        return _subject_match(*args) or _body_match(*args)

    # Merge commits
    if _subject_match(r'^Merge .* into \w+') and not body:
        return True

    # Reverted commits
    if _subject_match(r'^Revert .*') and _body_match(r'^This reverts commit.*'):
        return True

    # Simple additions of new TODOs
    if _subject_match(r'^Add TODO.*'):
        if not body or _body_match(r'^Adds TODO.*'):
            return True

    # Cleaned up imports
    if _subject_match(r'^Remove unused imports?') and not body:
        return True

    # Trivial/uninformative commits
    if _subject_match(r'^Fix unit tests$') and not body:
        return True

    if _subject_match(r'^Trivial fix .*') and not body:
        return True

    # Added comments
    if _subject_match(r'^Add comment.*'):
        if not body or _body_match(r'^Adds comment.*'):
            return True

    # Fixed typos
    if not body and _subject_match(r'^Fix typo.*') and 'and' not in subject:
        return True

    # Shameful
    if not body:
        if (_subject_match(r'\bNOTE:.*(BROKEN|broken).*')
                or _subject_match(r'.*\(WIP\).*(BROKEN|broken).*')):
            return True

    # Trivial changes
    if not body:
        if (_subject_match(r'(Add|Modify|Remove).*logging.*')
                or _subject_match(r'Trivial.*')
                or _subject_match(r'Minor (changes?|fix|fixes) .*')
                or _subject_match(r'Whitespace fixes')
                or _subject_match(r'.*trailing whitespace.*')
                or _subject_match(r'Rename variables')
                or _subject_match(r'Rename function \'.*\'')
                or _subject_match(r'Fix( broken)?( unit)? tests?$')
                or _subject_match(r'Minor refactor.*assert(ions)?')
                or _subject_match(r'Fix variable shadowing .*')
                or _subject_match(r'Remove unused .* argument.*')
                or _subject_match(r'.*[sS]pelling.*')):
            return True

    # Changes to notes
    if not body:
        if (_subject_match(r'.*(related\.md|notes\.md).*')
                or _subject_match(r'(Changes|Fixes).*(in|to)? \'.*\.md\'')):
            return True

    if not body:
        if _subject_match(r'^(Add|Fix|Modify|Remove|Update)'):
            if (_subject_match(r'.*notes on \w+')
                    or _subject_match(r'.*(to|in|from)? \'.*\.md\'')
                    or _subject_match(r'.* \'?\w+(\/\w+)?\.md\'?')
                    or _subject_match(r'.* \w+ notes')):
                return True

    # Changes related to various developer tools
    if _any_match(r'.*\bpylint(rc)?\b.*'):
        return True

    if (_any_match(r'.*update_changelog.*')
            or _any_match(r'.*generate_changelog.*')):
        return True

    # Changes to '.gitignore'
    if not body:
        if _subject_match(r'.*\'?\.gitignore\'?'):
            return True

    return False


def git_changelog_entries_for_range(hash_first, hash_second):
    git_log = git_log_for_range(hash_first, hash_second)
    parsed_git_log = parse_git_log(git_log)

    log_entries = list()
    for commit in parsed_git_log:
        subject = commit.get('subject', '').strip()
        body = commit.get('body', '').strip()

        if not subject:
            continue

        cle = ChangelogEntry(subject, body)
        if cle not in log_entries and not is_blacklisted(cle):
            log_entries.append(cle)

    return log_entries


def parse_git_log(git_log_string):
    log = str(git_log_string)
    log = log.strip('\n' + GIT_LOG_SEP_RECORD).split(GIT_LOG_SEP_RECORD)
    log = [row.strip().split(GIT_LOG_SEP_FIELD) for row in log]
    log = [dict(zip(GIT_COMMIT_FIELDS, row)) for row in log]
    return log


def git_log_for_range(hash_first, hash_second):
    _commit_range = '{}..{}'.format(hash_first, hash_second)
    stdout = subprocess.check_output(
        ['git', 'log', '--format="{}"'.format(GIT_LOG_FORMAT), _commit_range]
    )
    return coercers.force_string(stdout.strip())


def get_previous_version_tag():
    stdout = subprocess.check_output(
        ['git', 'describe', '--abbrev=0', '--tags']
    )
    return coercers.force_string(stdout.strip())


def get_commit_for_tag(tag_name):
    stdout = subprocess.check_output(
        ['git', 'rev-list', '-n', '1', tag_name]
    )
    return coercers.force_string(stdout.strip())


def is_readable_file(filepath):
    return os.path.isfile(filepath) and os.access(filepath, os.R_OK)


def get_changelog_header_line():
    _current_version_string = '.'.join(map(str, version.__version_info__))

    now = datetime.datetime.utcnow()
    _current_date = max([
        d.strftime('%Y-%m-%d') for d in (now, now + datetime.timedelta(hours=1))
    ])
    return '{}  [autonameow v{}]'.format(_current_date, _current_version_string)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        prog=SELFNAME,
        epilog='"{}" -- Change log utility.'.format(SELFNAME)
    )
    opts = parser.parse_args(sys.argv[1:])

    # Make sure that the changelog file exists.
    if not is_readable_file(changelog_path):
        print('File does not exist or is not readable: "{!s}"'.format(_path),
              file=sys.stderr)
        sys.exit(EXIT_FAILURE)

    if not process.is_executable('git'):
        print('This script requires "qit" to run. Exiting ..',
              file=sys.stderr)
        sys.exit(EXIT_FAILURE)

    exit_status = EXIT_SUCCESS

    header = get_changelog_header_line()
    print(header)

    prev_tag = get_previous_version_tag()
    prev_tag_hash = get_commit_for_tag(prev_tag)
    current_hash = process.git_commit_hash()
    # print('Previous version tag: {!s}'.format(prev_tag))
    # print('Previous version tag commit hash: {!s}'.format(prev_tag_hash))
    # print('Current commit hash: {!s}'.format(current_hash))

    log_entries = git_changelog_entries_for_range(prev_tag_hash, current_hash)

    SECTION_ENTRIES = {
        'Additions': list(),
        'Changes': list(),
        'Fixes': list()
    }
    for entry in log_entries:
        if ChangelogEntryClassifier.is_change(entry):
            SECTION_ENTRIES['Changes'].append(entry)
        elif ChangelogEntryClassifier.is_addition(entry):
            SECTION_ENTRIES['Additions'].append(entry)
        elif ChangelogEntryClassifier.is_fix(entry):
            SECTION_ENTRIES['Fixes'].append(entry)
        else:
            # TODO: Handle undetermined entry better?
            SECTION_ENTRIES['Changes'].append(entry)

    for section, entries in sorted(SECTION_ENTRIES.items()):
        print('\n' + text.indent(section, columns=12))

        for entry in entries:
            print(text.indent('- ' + entry.subject, columns=12))
            print(text.indent(entry.body, columns=14))
            if entry.body:
                print()

    sys.exit(exit_status)
