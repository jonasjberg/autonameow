# -*- coding: utf-8 -*-

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

from unittest import TestCase

import unit.utils as uu
from core.exceptions import FilesystemError
from util.disk.yaml import (
    load_yaml_file,
    write_yaml_file
)


class TestLoadYAML(TestCase):
    def test_loads_valid_file(self):
        _yaml_path = uu.abspath_testconfig()
        actual = load_yaml_file(_yaml_path)
        self.assertIsNotNone(actual)
        self.assertIsInstance(actual, dict)

    def test_raises_exception_given_invalid_arguments(self):
        def _fail(yaml_path):
            with self.assertRaises(FilesystemError):
                _ = load_yaml_file(yaml_path)

        _fail(None)
        _fail('')
        _fail(b'')
        _fail('foo')
        _fail(b'foo')
        _fail(uu.abspath_testfile('magic_png.png'))


class TestWriteYAML(TestCase):
    def test_writes_valid_data_to_valid_path(self):
        _dest_path = uu.make_temporary_file()
        self.assertTrue(uu.file_exists(_dest_path))

        _data = {'foo': 'bar', 'baz': 1337}
        write_yaml_file(_dest_path, _data)
        self.assertTrue(uu.file_exists(_dest_path))

        _loaded = load_yaml_file(_dest_path)
        self.assertEqual(_data, _loaded,
                         'Loaded data differs from the written data.')

    def test_raises_exception_given_invalid_arguments(self):
        def _fail(dest_path, data):
            with self.assertRaises(FilesystemError):
                _ = write_yaml_file(dest_path, data)

        _fail(None, None)
        _fail('', None)
        _fail(b'', None)
