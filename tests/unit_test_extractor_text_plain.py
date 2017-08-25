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

from extractors.text_plain import read_entire_text_file
import unit_utils as uu


class TestReadEntireTextFile(TestCase):
    def setUp(self):
        self.sample_file = uu.abspath_testfile('magic_txt.txt')
        self.assertTrue(uu.file_exists(self.sample_file))

    def test_read_entire_text_file(self):
        actual = read_entire_text_file(self.sample_file)
        self.assertIsNotNone(actual)

    def test_returns_expected_encoding(self):
        actual = read_entire_text_file(self.sample_file)
        self.assertTrue(isinstance(actual, str))

    def test_returns_expected_contents(self):
        actual = read_entire_text_file(self.sample_file)
        self.assertEqual(actual, 'text\n')
