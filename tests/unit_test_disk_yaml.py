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

from core.exceptions import FilesystemError
from core.disk import load_yaml_file
import unit_utils as uu


class TestLoadYAML(TestCase):
    def test_loads_valid_file(self):
        _yaml_path = uu.abspath_testfile('default_config.yaml')
        actual = load_yaml_file(_yaml_path)
        self.assertEqual(type(actual), dict)

    def test_raises_exception_given_invalid_argument(self):
        def _fail(yaml_path):
            with self.assertRaises(FilesystemError):
                _ = load_yaml_file(yaml_path)

        _fail(None)
        _fail('')
        _fail(b'')
        _fail('foo')
        _fail(b'foo')
        _fail(uu.abspath_testfile('magic_png.png'))
