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

from unittest import TestCase

from devscripts.update_changelog import (
    ChangelogEntry,
    is_blacklisted
)


class TestIsBlacklisted(TestCase):
    def __as_changelogentry(self, subject, body):
        return ChangelogEntry(subject, body)

    def _test_blacklist(self, subject, body, expect):
        cle = self.__as_changelogentry(subject, body)
        actual = is_blacklisted(cle)
        self.assertIsInstance(actual, bool)
        self.assertEqual(expect, actual)

    # Should not be filtered
    def test_does_not_blacklist_foo_bar(self):
        self._test_blacklist(subject='foo', body='bar', expect=False)

    # Merge commits
    def test_does_not_blacklist_merge_mention(self):
        self._test_blacklist(
            subject="Move debug logging to 'if __debug__' branches.",
            body='bar',
            expect=False
        )

    def test_does_not_blacklist_into_mention(self):
        self._test_blacklist(
            subject='Move MeowURI parsing to separate class.',
            body="Extracts parts of the 'MeowURI' class into new 'MeowURIParser'.",
            expect=False
        )

    def test_blacklists_merged_branch_from_githhub_remote(self):
        self._test_blacklist(
            subject="Merge branch 'develop' of github.com:jonasjberg/autonameow into develop",
            body='',
            expect=True
        )

    def test_blacklists_merged_remote_tracking_branch_from_githhub(self):
        self._test_blacklist(
            subject="Merge remote-tracking branch 'github/develop' into develop",
            body='',
            expect=True
        )

    def test_blacklists_merged_stash(self):
        self._test_blacklist(
            subject='Merge stash into rework_architecture ..',
            body='',
            expect=True
        )

    def test_blacklists_merged_branch_from_local_develop(self):
        self._test_blacklist(
            subject="Merge branch 'develop' into rework_generic_fields",
            body='',
            expect=True
        )

    def test_blacklists_merged_branch_from_local_develop(self):
        self._test_blacklist(
            subject="Merge branch 'rework_generic_fields' into develop",
            body='',
            expect=True
        )

    # Reverted commits
    def test_blacklists_reverted_commits(self):
        self._test_blacklist(
            subject='Revert "Set default logging level to \'ERROR\'."',
            body='This reverts commit 48b886e3c38eab69d08c972f8e782d28f237e5a4.',
            expect=True
        )

    def test_does_not_blacklist_revert_mention(self):
        self._test_blacklist(
            subject='Modify operating mode conflict resolution.',
            body='Adds reverting to "less safe" defaults in case of conflicts.',
            expect=False
        )
