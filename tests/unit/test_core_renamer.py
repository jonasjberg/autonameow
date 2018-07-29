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

from unittest import TestCase
from unittest.mock import Mock, patch

from core.renamer import FilenameDelta
from core.renamer import FileRenamer


class TestFilenameDelta(TestCase):
    def test_comparison_with_equal_source_path_and_equal_new_names(self):
        a = FilenameDelta(b'/tmp/foo/bar', 'baz')
        b = FilenameDelta(b'/tmp/foo/bar', 'baz')
        self.assertEqual(a, b)

    def test_comparison_with_equal_source_path_but_different_new_names(self):
        a = FilenameDelta(b'/tmp/foo/bar', 'baz')
        b = FilenameDelta(b'/tmp/foo/bar', 'meow')
        self.assertNotEqual(a, b)

    def test_comparison_with_different_source_paths_and_equal_new_names(self):
        a = FilenameDelta(b'/tmp/a/bar', 'meow')
        b = FilenameDelta(b'/tmp/a/foo', 'meow')
        self.assertNotEqual(a, b)

    def test_comparison_with_different_source_paths_and_different_new_names(self):
        a = FilenameDelta(b'/tmp/a/bar', 'meeeooow')
        b = FilenameDelta(b'/tmp/a/foo', 'meow')
        self.assertNotEqual(a, b)

    def test_membership(self):
        container = set()
        a = FilenameDelta(b'/foo/a', 'meow')
        container.add(a)
        self.assertEqual(1, len(container))

        b = FilenameDelta(b'/foo/a', 'meow')
        container.add(b)
        self.assertEqual(1, len(container))

        c = FilenameDelta(b'/foo/a', 'meeeooowwww')
        container.add(c)
        self.assertEqual(2, len(container))

    def test___repr__(self):
        a = FilenameDelta(b'/tmp/foo', 'bar')
        self.assertEqual('"foo" -> "bar"', repr(a))


class TestRenameFile(TestCase):
    def setUp(self):
        self.mock_rename_func = Mock()

    def test_rename_func_should_not_be_called_when_dry_run_is_true(self):
        fr = FileRenamer(dry_run=True, timid=False, rename_func=self.mock_rename_func)
        fr._rename_file(b'/tmp/dummy/foo', b'mjao')
        self.mock_rename_func.assert_not_called()

    def test_rename_func_should_be_called_when_dry_run_is_false_(self):
        fr = FileRenamer(dry_run=False, timid=False, rename_func=self.mock_rename_func)
        fr._rename_file(b'/tmp/dummy/foo', b'mjao')
        self.mock_rename_func.assert_called_with(b'/tmp/dummy/foo', b'mjao')


class TestFileRenamer(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dummy_bar_filepath = b'/tmp/foo/bar'
        cls.dummy_bar_basename = 'bar'
        cls.dummy_foo_basename = 'foo'
        cls.dummy_foo_basename_bytes = b'foo'

    def setUp(self):
        self.fr = FileRenamer(dry_run=True, timid=False)

    def test_add_pending_with_equal_basenames_become_skipped(self):
        self.fr.add_pending(self.dummy_bar_filepath, self.dummy_bar_basename)

        actual_skipped = list(self.fr.skipped)
        self.assertEqual(1, len(actual_skipped))
        # Check that iterator exhausts list
        actual_skipped = list(self.fr.skipped)
        self.assertEqual(0, len(actual_skipped))

        actual_pending = list(self.fr.pending)
        self.assertEqual(0, len(actual_pending))
        actual_to_be_confirmed = list(self.fr.needs_confirmation)
        self.assertEqual(0, len(actual_to_be_confirmed))

    def test_add_pending_with_different_basenames_become_pending(self):
        self.fr.add_pending(self.dummy_bar_filepath, self.dummy_foo_basename)

        actual_skipped = list(self.fr.skipped)
        self.assertEqual(0, len(actual_skipped))
        actual_to_be_confirmed = list(self.fr.needs_confirmation)
        self.assertEqual(0, len(actual_to_be_confirmed))

        actual_pending = list(self.fr.pending)
        self.assertEqual(1, len(actual_pending))
        # Check that iterator does not exhaust list
        actual_pending = list(self.fr.pending)
        self.assertEqual(1, len(actual_pending))

    def test_add_pending_with_different_basenames_must_be_confirmed(self):
        fr = FileRenamer(dry_run=True, timid=True)
        fr.add_pending(self.dummy_bar_filepath, self.dummy_foo_basename)

        actual_skipped = list(fr.skipped)
        self.assertEqual(0, len(actual_skipped))

        actual_pending = list(fr.pending)
        self.assertEqual(0, len(actual_pending))

        actual_to_be_confirmed = list(fr.needs_confirmation)
        self.assertEqual(1, len(actual_to_be_confirmed))
        # Check that iterator does not exhaust list
        actual_to_be_confirmed = list(fr.needs_confirmation)
        self.assertEqual(1, len(actual_to_be_confirmed))

    def test_rejecting_a_pending_file_removes_it_from_to_be_confirmed_list(self):
        fr = FileRenamer(dry_run=True, timid=True)
        fr.add_pending(self.dummy_bar_filepath, self.dummy_foo_basename)

        to_be_confirmed = list(fr.needs_confirmation)
        self.assertEqual(1, len(to_be_confirmed))
        # Check that iterator does not exhaust list
        to_be_confirmed = list(fr.needs_confirmation)
        self.assertEqual(1, len(to_be_confirmed))

        fr.reject(to_be_confirmed[0])
        to_be_confirmed = list(fr.needs_confirmation)
        self.assertEqual(0, len(to_be_confirmed))

    @patch('core.renamer.FileRenamer._rename_file')
    def test_rename_file_dry_run_true(self, mock__rename_file):
        fr = FileRenamer(dry_run=True, timid=False)
        fr.add_pending(self.dummy_bar_filepath, self.dummy_foo_basename)

        fr.do_renames()
        mock__rename_file.assert_called_once_with(self.dummy_bar_filepath,
                                                  self.dummy_foo_basename_bytes)
        self.assertEqual(0, len(list(fr.pending)))

    @patch('core.renamer.FileRenamer._rename_file')
    def test_rename_file_dry_run_false(self, mock__rename_file):
        fr = FileRenamer(dry_run=False, timid=False)
        fr.add_pending(self.dummy_bar_filepath, self.dummy_foo_basename)

        fr.do_renames()
        mock__rename_file.assert_called_once_with(self.dummy_bar_filepath,
                                                  self.dummy_foo_basename_bytes)
        self.assertEqual(0, len(list(fr.pending)))

    @patch('core.renamer.FileRenamer._rename_file')
    def test_file_not_renamed_before_being_confirmed_dry_run_true(
            self, mock__rename_file
    ):
        fr = FileRenamer(dry_run=True, timid=True)
        fr.add_pending(self.dummy_bar_filepath, self.dummy_foo_basename)

        fr.do_renames()
        mock__rename_file.assert_not_called()
        self.assertEqual(0, len(list(fr.pending)))
        self.assertEqual(1, len(list(fr.needs_confirmation)))

    @patch('core.renamer.FileRenamer._rename_file')
    def test_file_not_renamed_before_being_confirmed_dry_run_false(
            self, mock__rename_file
    ):
        fr = FileRenamer(dry_run=False, timid=True)
        fr.add_pending(self.dummy_bar_filepath, self.dummy_bar_basename)

        fr.do_renames()
        mock__rename_file.assert_not_called()
        self.assertEqual(0, len(list(fr.pending)))
        self.assertEqual(0, len(list(fr.needs_confirmation)))

    @patch('core.renamer.FileRenamer._rename_file')
    def test_file_not_renamed_after_reject_dry_run_true(
            self, mock__rename_file
    ):
        fr = FileRenamer(dry_run=True, timid=True)
        fr.add_pending(self.dummy_bar_filepath, self.dummy_foo_basename)

        to_be_confirmed = list(fr.needs_confirmation)
        fr.reject(to_be_confirmed[0])

        fr.do_renames()
        mock__rename_file.assert_not_called()
        self.assertEqual(0, len(list(fr.pending)))
        self.assertEqual(0, len(list(fr.needs_confirmation)))

    @patch('core.renamer.FileRenamer._rename_file')
    def test_file_not_renamed_after_reject_dry_run_false(
            self, mock__rename_file
    ):
        fr = FileRenamer(dry_run=False, timid=True)
        fr.add_pending(self.dummy_bar_filepath, self.dummy_foo_basename)

        to_be_confirmed = list(fr.needs_confirmation)
        fr.reject(to_be_confirmed[0])

        fr.do_renames()
        mock__rename_file.assert_not_called()
        self.assertEqual(0, len(list(fr.pending)))
        self.assertEqual(0, len(list(fr.needs_confirmation)))

    @patch('core.renamer.FileRenamer._rename_file')
    def test_rename_file_after_confirm_dry_run_true(self, mock__rename_file):
        fr = FileRenamer(dry_run=True, timid=True)
        fr.add_pending(self.dummy_bar_filepath, self.dummy_foo_basename)

        to_be_confirmed = list(fr.needs_confirmation)
        fr.confirm(to_be_confirmed[0])

        fr.do_renames()
        mock__rename_file.assert_called_once_with(self.dummy_bar_filepath,
                                                  self.dummy_foo_basename_bytes)
        self.assertEqual(0, len(list(fr.pending)))
        self.assertEqual(0, len(list(fr.needs_confirmation)))

    @patch('core.renamer.FileRenamer._rename_file')
    def test_rename_file_after_confirm_dry_run_false(self, mock__rename_file):
        fr = FileRenamer(dry_run=False, timid=True)
        fr.add_pending(self.dummy_bar_filepath, self.dummy_foo_basename)

        to_be_confirmed = list(fr.needs_confirmation)
        fr.confirm(to_be_confirmed[0])

        fr.do_renames()
        mock__rename_file.assert_called_once_with(self.dummy_bar_filepath,
                                                  self.dummy_foo_basename_bytes)
        self.assertEqual(0, len(list(fr.pending)))
        self.assertEqual(0, len(list(fr.needs_confirmation)))
