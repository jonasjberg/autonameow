#!/usr/bin/env python3
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

import os
import types
from unittest import TestCase

from analyzers.analyze_abstract import (
    get_analyzer_classes,
)
from core.fileobject import FileObject
from unit_utils import (
    make_temp_dir,
    make_temporary_file,
    get_mock_analyzer,
    get_mock_fileobject
)


class TestUnitUtilityMakeTempDir(TestCase):
    def test_make_temp_dir(self):
        self.assertIsNotNone(make_temp_dir())
        self.assertTrue(os.path.exists(make_temp_dir()))
        self.assertTrue(os.path.isdir(make_temp_dir()))


class TestUnitUtilityMakeTemporaryFile(TestCase):
    def test_make_temporary_file(self):
        self.assertIsNotNone(make_temporary_file)
        self.assertTrue(os.path.exists(make_temporary_file()))
        self.assertTrue(os.path.isfile(make_temporary_file()))
        self.assertTrue(isinstance(make_temporary_file(), str))

    def test_make_temporary_file_with_prefix(self):
        self.assertTrue(os.path.exists(make_temporary_file(prefix='prefix_')))
        self.assertTrue(os.path.isfile(make_temporary_file(prefix='prefix_')))
        self.assertTrue(os.path.basename(make_temporary_file(prefix='prefix_')).startswith('prefix_'))

    def test_make_temporary_file_with_suffix(self):
        self.assertTrue(os.path.exists(make_temporary_file(suffix='_suffix')))
        self.assertTrue(os.path.isfile(make_temporary_file(suffix='_suffix')))
        self.assertTrue(make_temporary_file(suffix='_suffix').endswith('_suffix'))

    def test_make_temporary_file_with_prefix_and_suffix(self):
        self.assertTrue(os.path.exists(make_temporary_file(prefix='mjao',
                                                           suffix='.jpg')))
        self.assertTrue(os.path.isfile(make_temporary_file(prefix='mjao',
                                                           suffix='.jpg')))
        self.assertTrue(os.path.basename(make_temporary_file(prefix='mjao', suffix='.jpg')).endswith('.jpg'))
        self.assertTrue(os.path.basename(make_temporary_file(prefix='mjao', suffix='.jpg')).startswith('mjao'))

    def test_make_temporary_file_with_basename(self):
        self.assertTrue(os.path.exists(make_temporary_file(basename='mjao.jpg')))
        self.assertTrue(os.path.isfile(make_temporary_file(basename='mjao.jpg')))
        self.assertEqual(os.path.basename(make_temporary_file(basename='mjao.jpg')), 'mjao.jpg')


class TestUnitUtilityGetMockAnalyzer(TestCase):
    def test_get_mock_analyzer_is_defined(self):
        self.assertIsNotNone(get_mock_analyzer)
        self.assertIsNotNone(get_mock_analyzer())

    def test_get_mock_analyzer_is_generator(self):
        self.assertTrue(isinstance(get_mock_analyzer(), types.GeneratorType))

    def test_get_mock_analyzer_returns_analyzers(self):
        for a in get_mock_analyzer():
            self.assertIn(type(a), get_analyzer_classes())


class TestUnitUtilityGetMockFileObject(TestCase):
    def test_get_mock_fileobject_is_defined(self):
        self.assertIsNotNone(get_mock_fileobject)
        self.assertIsNotNone(get_mock_fileobject())

    def test_get_mock_fileobject_returns_expected_type(self):
        self.assertTrue(isinstance(get_mock_fileobject(), FileObject))
