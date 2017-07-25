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
import unit_utils as uu

import analyzers
from analyzers import BaseAnalyzer
from core.fileobject import FileObject


class TestUnitUtilityMakeTempDir(TestCase):
    def test_make_temp_dir(self):
        self.assertIsNotNone(uu.make_temp_dir())
        self.assertTrue(os.path.exists(uu.make_temp_dir()))
        self.assertTrue(os.path.isdir(uu.make_temp_dir()))


class TestUnitUtilityMakeTemporaryFile(TestCase):
    def test_make_temporary_file(self):
        self.assertIsNotNone(uu.make_temporary_file)
        self.assertTrue(os.path.exists(uu.make_temporary_file()))
        self.assertTrue(os.path.isfile(uu.make_temporary_file()))
        self.assertTrue(isinstance(uu.make_temporary_file(), bytes))

    def test_make_temporary_file_with_prefix(self):
        actual = uu.make_temporary_file(prefix='prefix_')
        self.assertTrue(os.path.exists(actual))
        self.assertTrue(os.path.isfile(actual))

        actual_basename = os.path.basename(actual)
        self.assertTrue(actual_basename.startswith(b'prefix_'))

    def test_make_temporary_file_with_suffix(self):
        actual = uu.make_temporary_file(suffix='_suffix')
        self.assertTrue(os.path.exists(actual))
        self.assertTrue(os.path.isfile(actual))
        self.assertTrue(actual.endswith(b'_suffix'))

    def test_make_temporary_file_with_prefix_and_suffix(self):
        actual = uu.make_temporary_file(prefix='mjao', suffix='.jpg')
        self.assertTrue(os.path.exists(actual))
        self.assertTrue(os.path.isfile(actual))

        actual_basename = os.path.basename(actual)
        self.assertTrue(actual_basename.endswith(b'.jpg'))
        self.assertTrue(actual_basename.startswith(b'mjao'))

    def test_make_temporary_file_with_basename(self):
        actual = uu.make_temporary_file(basename='mjao.jpg')
        self.assertTrue(os.path.exists(actual))
        self.assertTrue(os.path.isfile(actual))

        actual_basename = os.path.basename(actual)
        self.assertEqual(actual_basename, B'mjao.jpg')


class TestUnitUtilityGetMockAnalyzer(TestCase):
    def test_get_mock_analyzer_is_defined(self):
        self.assertIsNotNone(uu.get_mock_analyzer)
        self.assertIsNotNone(uu.get_mock_analyzer())

    def test_get_mock_analyzer_is_generator(self):
        self.assertTrue(isinstance(uu.get_mock_analyzer(), types.GeneratorType))

    def test_get_mock_analyzer_returns_analyzers(self):
        for a in uu.get_mock_analyzer():
            self.assertIn(type(a), analyzers.get_analyzer_classes())


class TestUnitUtilityGetMockFileObject(TestCase):
    def test_get_mock_fileobject_is_defined(self):
        self.assertIsNotNone(uu.get_mock_fileobject)
        self.assertIsNotNone(uu.get_mock_fileobject())

    def test_get_mock_fileobject_returns_expected_type(self):
        self.assertTrue(isinstance(uu.get_mock_fileobject(), FileObject))

    def test_get_mock_fileobject_with_mime_type_video_mp4(self):
        actual = uu.get_mock_fileobject(mime_type='video/mp4')
        self.assertEqual(actual.mime_type, 'video/mp4')

    def test_get_mock_fileobject_with_mime_type_all_types(self):
        mime_types = ['application/pdf', 'image/gif', 'image/jpeg', 'image/png',
                      'image/x-ms-bmp', 'text/plain', 'video/mp4']

        for mt in mime_types:
            actual = uu.get_mock_fileobject(mime_type=mt)
            self.assertEqual(actual.mime_type, mt)


class TestCaptureStdout(TestCase):
    def test_capture_stdout(self):
        with uu.capture_stdout() as out:
            print('should_be_captured')

        self.assertEqual(out.getvalue().strip(), 'should_be_captured')
        self.assertEqual(out.getvalue(), 'should_be_captured\n')


class TestUnitUtilityGetInstantiatedAnalyzers(TestCase):
    def test_get_instantiated_analyzers_returns_something(self):
        self.assertIsNotNone(uu.get_instantiated_analyzers())

    def test_get_instantiated_analyzers_returns_class_objects(self):
        instances = uu.get_instantiated_analyzers()
        for analyzer_instance in instances:
            self.assertTrue(hasattr(analyzer_instance, '__class__'))

    def test_get_instantiated_analyzers_returns_expected_type(self):
        instances = uu.get_instantiated_analyzers()
        self.assertEqual(type(instances), list)

        for analyzer_instance in instances:
            self.assertTrue(issubclass(analyzer_instance.__class__, BaseAnalyzer))

    def test_get_instantiated_analyzers_returns_arbitrary_number(self):
        # TODO: [hardcoded] Likely to break; Fix or remove!
        self.assertGreaterEqual(len(uu.get_instantiated_analyzers()), 6)

    def test_get_instantiated_analyzers_returns_list(self):
        self.assertTrue(isinstance(uu.get_instantiated_analyzers(), list))
