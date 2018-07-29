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

import unit.utils as uu
from extractors.text.base import BaseTextExtractor
from extractors.text.base import cleanup


class TestBaseTextExtractor(TestCase):
    def setUp(self):
        self.test_file = uu.make_temporary_file()
        self.e = BaseTextExtractor()

        class DummyFileObject(object):
            def __init__(self):
                self.mime_type = 'image/jpeg'
        self.fo = DummyFileObject()

    def test_is_available(self):
        self.assertIsNotNone(BaseTextExtractor)

    def test_can_be_instantiated(self):
        self.assertIsNotNone(self.e)

    def test_method_str_does_not_return_none(self):
        self.assertIsNotNone(str(self.e))
        self.assertIsNotNone(self.e.__str__)

    def test_method_str_returns_type_string(self):
        self.assertTrue(uu.is_internalstring(str(self.e)))
        self.assertTrue(uu.is_internalstring(str(self.e.__str__)))

    def test_method_str_returns_expected(self):
        self.assertEqual(str(self.e), 'BaseTextExtractor')

    def test_base_class_does_not_implement_can_handle(self):
        with self.assertRaises(NotImplementedError):
            _ = self.e.can_handle(self.fo)

    def test_base_class_does_not_implement_extract_text(self):
        with self.assertRaises(NotImplementedError):
            self.e._extract_text(self.test_file)

    def test_base_class_does_not_implement_extract(self):
        with self.assertRaises(NotImplementedError):
            _ = self.e.extract_text(self.test_file)

    def test_base_class_does_not_implement_dependencies_satisfied(self):
        with self.assertRaises(NotImplementedError):
            self.e.dependencies_satisfied()


class TestCleanup(TestCase):
    def _assert_returns(self, expected, given):
        actual = cleanup(given)
        self.assertEqual(expected, actual)

    def test_cleanup_removes_carriage_returns(self):
        text_with_carriage_returns = 'foo\nbar\rbaz\r\n'
        actual = cleanup(text_with_carriage_returns)
        self.assertNotIn('\r', actual)
        self.assertEqual('foo\nbarbaz\n', actual)
