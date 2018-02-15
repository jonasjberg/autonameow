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


import sys
from unittest import (
    skipIf,
    TestCase
)
from unittest.mock import patch

try:
    import prompt_toolkit
except ImportError:
    prompt_toolkit = None
    print(
        'Missing required module "prompt_toolkit". '
        'Make sure "prompt_toolkit" is available before running this program.',
        file=sys.stderr
    )

from core.renamer import (
    FilenameDelta,
    FileRenamer
)


def prompt_toolkit_unavailable():
    return prompt_toolkit is None, 'Failed to import "prompt_toolkit"'


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


@skipIf(*prompt_toolkit_unavailable())
class TestDoRename(TestCase):
    # TODO: Add tests for 'mode_timid'.

    @patch('core.autonameow.disk.rename_file')
    def test_dry_run_true_will_not_call_diskutils_rename_file(self, mockrename):
        fr = FileRenamer(dry_run=True, mode_timid=False)
        fr.do_rename(b'/tmp/dummy/path', 'mjaopath')
        mockrename.assert_not_called()

    @patch('core.autonameow.disk.rename_file')
    def test_dry_run_false_calls_diskutils_rename_file(self, mockrename):
        fr = FileRenamer(dry_run=False, mode_timid=False)
        fr.do_rename(b'/tmp/dummy/path', 'mjaopath')
        mockrename.assert_called_with(b'/tmp/dummy/path', b'mjaopath')

    @patch('core.autonameow.disk.rename_file')
    def test_skip_rename_if_new_name_equals_old_name(self, mockrename):
        fr = FileRenamer(dry_run=False, mode_timid=False)
        fr.do_rename(b'/tmp/dummy/foo', 'foo')
        mockrename.assert_not_called()

    @patch('core.autonameow.disk.rename_file')
    def test_skip_rename_if_new_name_equals_old_name_dry_run(self, mockrename):
        fr = FileRenamer(dry_run=True, mode_timid=False)
        fr.do_rename(b'/tmp/dummy/foo', 'foo')
        mockrename.assert_not_called()
