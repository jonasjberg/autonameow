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
from unittest.mock import patch

from core.renamer import (
    FilenameDelta,
    FileRenamer
)


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
    @patch('core.autonameow.disk.rename_file')
    def test_dry_run_true_will_not_call_diskutils_rename_file(
            self, mock_disk_rename_file
    ):
        fr = FileRenamer(dry_run=True, timid=False)
        fr._rename_file(b'/tmp/dummy/foo', b'mjao')
        mock_disk_rename_file.assert_not_called()

    @patch('core.autonameow.disk.rename_file')
    def test_dry_run_false_calls_diskutils_rename_file(
            self, mock_disk_rename_file
    ):
        fr = FileRenamer(dry_run=False, timid=False)
        fr._rename_file(b'/tmp/dummy/foo', b'mjao')
        mock_disk_rename_file.assert_called_with(b'/tmp/dummy/foo', b'mjao')


class TestFileRenamer(TestCase):
    def setUp(self):
        self.fr = FileRenamer(dry_run=True, timid=False)

    def test_add_pending_with_equal_basenames_become_skipped(self):
        dummy_source_path = b'/tmp/foo/bar'
        dummy_new_basename = 'bar'
        self.fr.add_pending(dummy_source_path, dummy_new_basename)

        actual_skipped = list(self.fr.skipped)
        self.assertEqual(1, len(actual_skipped))
        # Check that iterator does not exhaust list
        actual_skipped = list(self.fr.skipped)
        self.assertEqual(1, len(actual_skipped))

        actual_pending = list(self.fr.pending)
        self.assertEqual(0, len(actual_pending))
        actual_to_be_confirmed = list(self.fr.needs_confirmation)
        self.assertEqual(0, len(actual_to_be_confirmed))

    def test_add_pending_with_different_basenames_become_pending(self):
        dummy_source_path = b'/tmp/foo/bar'
        dummy_new_basename = 'baz'
        self.fr.add_pending(dummy_source_path, dummy_new_basename)

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
        dummy_source_path = b'/tmp/foo/bar'
        dummy_new_basename = 'baz'
        fr.add_pending(dummy_source_path, dummy_new_basename)

        actual_skipped = list(fr.skipped)
        self.assertEqual(0, len(actual_skipped))

        actual_pending = list(fr.pending)
        self.assertEqual(0, len(actual_pending))

        actual_to_be_confirmed = list(fr.needs_confirmation)
        self.assertEqual(1, len(actual_to_be_confirmed))
        # Check that iterator does not exhaust list
        actual_to_be_confirmed = list(fr.needs_confirmation)
        self.assertEqual(1, len(actual_to_be_confirmed))

    @patch('core.renamer.FileRenamer._rename_file')
    def test_rename_file_dry_run_true(self, mock__rename_file):
        fr = FileRenamer(dry_run=True, timid=False)
        dummy_source_path = b'/tmp/foo/bar'
        dummy_new_basename = 'baz'
        fr.add_pending(dummy_source_path, dummy_new_basename)
        fr.do_renames()
        mock__rename_file.assert_called_once_with(dummy_source_path, b'baz')
        self.assertEqual(0, len(list(fr.pending)))

    @patch('core.renamer.FileRenamer._rename_file')
    def test_rename_file_dry_run_false(self, mock__rename_file):
        fr = FileRenamer(dry_run=False, timid=False)
        dummy_source_path = b'/tmp/foo/bar'
        dummy_new_basename = 'baz'
        fr.add_pending(dummy_source_path, dummy_new_basename)
        fr.do_renames()
        mock__rename_file.assert_called_once_with(dummy_source_path, b'baz')
        self.assertEqual(0, len(list(fr.pending)))

    @patch('core.renamer.FileRenamer._rename_file')
    def test_file_not_renamed_before_being_confirmed_dry_run_true(
            self, mock__rename_file
    ):
        fr = FileRenamer(dry_run=True, timid=True)
        dummy_source_path = b'/tmp/foo/bar'
        dummy_new_basename = 'baz'
        fr.add_pending(dummy_source_path, dummy_new_basename)
        fr.do_renames()
        mock__rename_file.assert_not_called()
        self.assertEqual(0, len(list(fr.pending)))

    @patch('core.renamer.FileRenamer._rename_file')
    def test_file_not_renamed_before_being_confirmed_dry_run_false(
            self, mock__rename_file
    ):
        fr = FileRenamer(dry_run=False, timid=True)
        dummy_source_path = b'/tmp/foo/bar'
        dummy_new_basename = 'baz'
        fr.add_pending(dummy_source_path, dummy_new_basename)
        fr.do_renames()
        mock__rename_file.assert_not_called()
        self.assertEqual(0, len(list(fr.pending)))

    @patch('core.renamer.FileRenamer._rename_file')
    def test_rename_file_after_confirm_dry_run_true(self, mock__rename_file):
        fr = FileRenamer(dry_run=True, timid=True)
        dummy_source_path = b'/tmp/foo/bar'
        dummy_new_basename = 'baz'
        fr.add_pending(dummy_source_path, dummy_new_basename)

        to_be_confirmed = list(fr.needs_confirmation)
        fr.confirm(to_be_confirmed[0])

        fr.do_renames()
        mock__rename_file.assert_called_once_with(dummy_source_path, b'baz')
        self.assertEqual(0, len(list(fr.pending)))

    @patch('core.renamer.FileRenamer._rename_file')
    def test_rename_file_after_confirm_dry_run_false(self, mock__rename_file):
        fr = FileRenamer(dry_run=False, timid=True)
        dummy_source_path = b'/tmp/foo/bar'
        dummy_new_basename = 'baz'
        fr.add_pending(dummy_source_path, dummy_new_basename)

        to_be_confirmed = list(fr.needs_confirmation)
        fr.confirm(to_be_confirmed[0])

        fr.do_renames()
        mock__rename_file.assert_called_once_with(dummy_source_path, b'baz')
        self.assertEqual(0, len(list(fr.pending)))
