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

from core import constants as C
from extractors import extract
import unit.utils as uu


class TestStandaloneExtract(TestCase):
    def test_main_exits_with_exit_success_if_not_given_any_input_paths(self):
        with self.assertRaises(SystemExit) as e:
            extract.main()
            self.assertEqual(e.type, SystemExit)
            self.assertEqual(e.value.code, C.EXIT_SUCCESS)

    def test_main_exits_with_exit_success_if_not_specifying_actions(self):
        _path = uu.abspath_testfile('magic_txt.txt')
        _options = {'input_paths': [_path]}

        with self.assertRaises(SystemExit) as e:
            extract.main(_options)
            self.assertEqual(e.type, SystemExit)
            self.assertEqual(e.value.code, C.EXIT_SUCCESS)
