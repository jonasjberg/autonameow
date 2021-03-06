# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2020 Jonas Sjöberg <autonameow@jonasjberg.com>
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

    def test_does_not_blacklist_foo_bar(self):
        self._assert_not_blacklisted(subject='foo', body='bar')

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

    def test_blacklists_removal_of_unused_imports(self):
        self._assert_blacklists(
            subject='Remove unused imports.',
            body='',
        )
        self._assert_blacklists(
            subject='Remove unused import.',
            body='',
        )

    def test_blacklists_trivial_uninformative_fix(self):
        self._assert_blacklists(
            subject='Fix variable shadowing argument.',
            body='',
        )

        self._assert_blacklists(
            subject='Fix unit tests.',
            body='',
        )

    def test_blacklists_various_minor_fixes_without_body(self):
        self._assert_blacklists(
            subject="Various minor fixes in 'util/encoding.py'.",
            body='',
        )
        self._assert_blacklists(
            subject="Various fixes in 'run_unit_tests.sh'.",
            body='',
        )

    def test_does_not_blacklist_various_minor_fixes_with_body(self):
        self._assert_not_blacklisted(
            subject="Minor fixes in 'known_data_loader.py'.",
            body="""Wraps filename string operation with 'lru_cache'.

Also adds additional unit tests and modifies calls
to 'clear_lookup_cache()' between unit tests.""",
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

    def test_blacklists_trivial_test_fixes(self):
        self._assert_blacklists(
            subject='Fix unit tests.',
            body='',
        )
        self._assert_blacklists(
            subject='Fix broken unit test.',
            body='',
        )
        self._assert_blacklists(
            subject='Fix broken tests.',
            body='',
        )

    def test_blacklists_trivial_refactorings(self):
        self._assert_blacklists(
            subject='Minor refactoring regression rename assertions.',
            body='',
        )

    def test_blacklists_trivial_removals(self):
        self._assert_blacklists(
            subject="Remove unused 'FilesContext' argument 'ui'.",
            body='',
        )

    def test_blacklists_whitespace_changes(self):
        self._assert_blacklists(
            subject='Whitespace fixes.',
            body='',
        )
        self._assert_blacklists(
            subject='Remove trailing whitespace.',
            body='',
        )

    def test_does_not_blacklist_arguably_less_trivial_test_fixes(self):
        self._assert_not_blacklisted(
            subject='Fix unit test failing on MacOS.',
            body='',
        )

    def test_blacklists_added_comment(self):
        self._assert_blacklists(
            subject='Add comment on requiring all extractors.',
            body='',
        )

    def test_blacklists_fixed_typo_and_added_comment(self):
        self._assert_blacklists(
            subject='Fix typo in comment. Add comment.',
            body='',
        )

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

    def test_blacklists_devscripts(self):
        self._assert_blacklists(
            subject="Modify yamllint configuration",
            body='',
        )
        self._assert_blacklists(
            subject="Modify yamllint configuration.",
            body='',
        )
        self._assert_blacklists(
            subject="Modify pylint configuration",
            body='',
        )
        self._assert_blacklists(
            subject="Modify pylint configuration.",
            body='',
        )
