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

from devscripts.generate_changelog import ChangelogEntry
from devscripts.generate_changelog import is_blacklisted


class TestIsBlacklisted(TestCase):
    def __as_changelogentry(self, subject, body):
        return ChangelogEntry(subject, body)

    def _assert_blacklists(self, subject, body):
        cle = self.__as_changelogentry(subject, body)
        actual = is_blacklisted(cle)
        self.assertIsInstance(actual, bool)
        self.assertTrue(actual)

    def _assert_not_blacklisted(self, subject, body):
        cle = self.__as_changelogentry(subject, body)
        actual = is_blacklisted(cle)
        self.assertIsInstance(actual, bool)
        self.assertFalse(actual)

    # Should not be filtered
    def test_does_not_blacklist_foo_bar(self):
        self._assert_not_blacklisted(subject='foo', body='bar')

    # Merge commits
    def test_does_not_blacklist_merge_mention(self):
        self._assert_not_blacklisted(
            subject="Move debug logging to 'if __debug__' branches.",
            body='bar',
        )

    def test_does_not_blacklist_into_mention(self):
        self._assert_not_blacklisted(
            subject='Move MeowURI parsing to separate class.',
            body="Extracts parts of the 'MeowURI' class into new 'MeowURIParser'.",
        )

    def test_blacklists_merged_branch_from_githhub_remote(self):
        self._assert_blacklists(
            subject="Merge branch 'develop' of github.com:jonasjberg/autonameow into develop",
            body='',
        )

    def test_blacklists_merged_remote_tracking_branch_from_githhub(self):
        self._assert_blacklists(
            subject="Merge remote-tracking branch 'github/develop' into develop",
            body='',
        )

    def test_blacklists_merged_stash(self):
        self._assert_blacklists(
            subject='Merge stash into rework_architecture ..',
            body='',
        )

    def test_blacklists_merged_branch_from_local_develop(self):
        self._assert_blacklists(
            subject="Merge branch 'develop' into rework_generic_fields",
            body='',
        )

    def test_blacklists_merged_branch_from_local_develop(self):
        self._assert_blacklists(
            subject="Merge branch 'rework_generic_fields' into develop",
            body='',
        )

    # Reverted commits
    def test_blacklists_reverted_commits(self):
        self._assert_blacklists(
            subject='Revert "Set default logging level to \'ERROR\'."',
            body='This reverts commit 48b886e3c38eab69d08c972f8e782d28f237e5a4.',
        )

    def test_does_not_blacklist_revert_mention(self):
        self._assert_not_blacklisted(
            subject='Modify operating mode conflict resolution.',
            body='Adds reverting to "less safe" defaults in case of conflicts.',
        )

    # Adding new TODOs
    def test_blacklists_new_todos_with_ids(self):
        self._assert_blacklists(
            subject='Add TODO [TD0163] on prematurely initializing providers.',
            body='',
        )

    def test_blacklists_new_todo_notes(self):
        self._assert_blacklists(
            subject='Add TODO-note on killing descendant processes.',
            body='',
        )
        self._assert_blacklists(
            subject='Add TODOs on bad unit test dependencies.',
            body='',
        )
        self._assert_blacklists(
            subject='Add TODO-notes on provider boundary cleanup.',
            body='Adds TODO-items [TD0126][TD0127][TD0128].',
        )

    def test_does_not_blacklist_todo_mention(self):
        self._assert_not_blacklisted(
            subject='Modify handling of "generic fields" in analyzers.',
            body='Adds TODO [TD0146] on reworking "generic fields" and possibly'
                 + 'bundling multiple fields in some type of "records".',
        )

    # Unused imports
    def test_blacklists_removal_of_unused_imports(self):
        self._assert_blacklists(
            subject='Remove unused imports.',
            body='',
        )
        self._assert_blacklists(
            subject='Remove unused import.',
            body='',
        )

    # Trivial and uninformative commits
    def test_blacklists_trivial_uninformative_fix(self):
        self._assert_blacklists(
            subject='Fix unit tests.',
            body='',
        )

    def test_blacklists_trivial_uninformative_trivial_fix(self):
        self._assert_blacklists(
            subject='Trivial fix to TODO-list.',
            body='',
        )

    def test_does_not_blacklist_fix_mention(self):
        self._assert_not_blacklisted(
            subject='Fix testing for capitalized "Usage".',
            body='',
        )

    # Adding comments
    def test_blacklists_added_comment(self):
        self._assert_blacklists(
            subject='Add comment on requiring all extractors.',
            body='',
        )

    # Fixed typos
    def test_blacklists_fixed_typo_and_added_comment(self):
        self._assert_blacklists(
            subject='Fix typo in comment. Add comment.',
            body='',
        )

    # Added/changed notes.
    def test_blacklists_added_notes(self):
        self._assert_blacklists(
            subject='Add notes on extractors.',
            body='',
        )
        self._assert_blacklists(
            subject='Add notes on MeowURis.',
            body='',
        )

    def test_blacklists_modified_notes(self):
        self._assert_blacklists(
            subject='Update notes on extractors.',
            body='',
        )
        self._assert_blacklists(
            subject='Update notes on MeowURis.',
            body='',
        )
        self._assert_blacklists(
            subject='Modify notes on extractors.',
            body='',
        )
        self._assert_blacklists(
            subject='Modify notes on MeowURis.',
            body='',
        )
        self._assert_blacklists(
            subject="Update 'ideas.md'.",
            body='',
        )
        self._assert_blacklists(
            subject="Update 'notes/ideas.md'.",
            body='',
        )
        self._assert_blacklists(
            subject="Modify 'ideas.md'.",
            body='',
        )
        self._assert_blacklists(
            subject="Modify 'notes/ideas.md'.",
            body='',
        )

    def test_blacklists_fixed_notes(self):
        self._assert_blacklists(
            subject='Fix notes on extractors.',
            body='',
        )
        self._assert_blacklists(
            subject='Fix notes on MeowURis.',
            body='',
        )

    # Added/changed notes.
    def test_blacklists_changes_to_gitignore(self):
        self._assert_blacklists(
            subject='Add .* to \'.gitignore\'',
            body='',
        )
        self._assert_blacklists(
            subject="Add 'junk' directory to .gitignore.",
            body='',
        )

    def test_does_not_blacklist_changed_gitignore_with_additional_info(self):
        self._assert_not_blacklisted(
            subject="Add regression tests to '.gitignore'.",
            body="Ignores 'skip' files and regression tests named '*LOCAL*'."
        )

    def test_blacklists_this_script_itself(self):
        self._assert_blacklists(
            subject="Add blacklist patterns to 'generate_changelog.py'.",
            body='',
        )
        self._assert_blacklists(
            subject="Add blacklist patterns to 'generate_changelog.py'.",
            body='',
        )
