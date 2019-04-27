# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2019 Jonas Sjöberg <autonameow@jonasjberg.com>
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

import os
from unittest import TestCase
from unittest.mock import Mock, patch, PropertyMock

import unit.constants as uuconst
import unit.utils as uu
from analyzers import BaseAnalyzer
from analyzers import find_analyzer_files
from analyzers import get_analyzer_classes
from core import constants as C


# TODO: [hardcoded] Likely to break; fixed analyzer names!
EXPECT_ANALYZER_CLASSES = [
    'analyzers.analyze_filename.FilenameAnalyzer',
    'analyzers.analyze_document.DocumentAnalyzer',
    'analyzers.analyze_ebook.EbookAnalyzer'
]
EXPECT_ANALYZER_CLASSES_BASENAME = [
    c.split('.')[-1] for c in EXPECT_ANALYZER_CLASSES
]


class TestBaseAnalyzer(TestCase):
    def setUp(self):
        self.maxDiff = None

        self.mock_config = Mock()
        self.a = BaseAnalyzer(
            uu.get_mock_fileobject(), self.mock_config, None
        )

        self.mock_fileobject = Mock()
        self.mock_fileobject.mime_type = 'image/jpeg'

    def test_run_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            self.a.run()


class TestBaseAnalyzerClassMethods(TestCase):
    def setUp(self):
        self.mock_fileobject = Mock()
        self.mock_fileobject.mime_type = 'image/jpeg'

        self.mock_config = Mock()

        self.a = BaseAnalyzer(
            self.mock_fileobject, self.mock_config, None
        )

    def test_can_handle_raises_exception_if_none(self):
        with self.assertRaises(NotImplementedError):
            _ = self.a.can_handle(self.mock_fileobject)

    @patch('analyzers.BaseAnalyzer.HANDLES_MIME_TYPES',
           new_callable=PropertyMock, return_value=['text/plain'])
    def test_can_handle_returns_false(self, mock_attribute):
        a = BaseAnalyzer(
            uu.get_mock_fileobject(), self.mock_config, None
        )
        actual = a.can_handle(self.mock_fileobject)
        self.assertFalse(actual)

    @patch('analyzers.BaseAnalyzer.HANDLES_MIME_TYPES',
           new_callable=PropertyMock, return_value=['image/jpeg'])
    def test_can_handle_returns_true(self, mock_attribute):
        a = BaseAnalyzer(
            uu.get_mock_fileobject(), self.mock_config, None
        )
        actual = a.can_handle(self.mock_fileobject)
        self.assertTrue(actual)


class TestFindAnalyzerSourceFiles(TestCase):
    def test_find_analyzer_files_returns_expected_type(self):
        actual = find_analyzer_files()
        self.assertIsInstance(actual, list)

    def test_find_analyzer_files_returns_expected_files(self):
        actual = find_analyzer_files()

        # TODO: [hardcoded] Likely to break; requires manual updates.
        self.assertIn('analyze_filename.py', actual)
        self.assertIn('analyze_document.py', actual)
        self.assertIn('analyze_ebook.py', actual)


class TestGetAnalyzerClasses(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.klasses, _ = get_analyzer_classes()

    def test_get_analyzer_classes_returns_expected_type(self):
        self.assertIsInstance(self.klasses, list)
        for klass in self.klasses:
            uu.is_class(klass)
            self.assertTrue(issubclass(klass, BaseAnalyzer))

    def test_get_analyzer_classes_does_not_include_abstract_classes(self):
        self.assertNotIn(BaseAnalyzer, self.klasses)

    def test_get_analyzer_classes_returns_class_objects(self):
        for klass in self.klasses:
            self.assertTrue(uu.is_class(klass))

    def test_get_analyzer_classes_does_not_return_class_instances(self):
        for klass in self.klasses:
            self.assertFalse(uu.is_class_instance(klass))


class TestNumberOfAvailableAnalyzerClasses(TestCase):
    def setUp(self):
        self.actual, _ = get_analyzer_classes()

    def test_get_analyzer_classes_returns_expected_number_of_analyzers(self):
        expected = len([
            f for f in
            os.listdir(
                os.path.join(uuconst.PATH_AUTONAMEOW_SRCROOT, 'analyzers')
            )
            if f.startswith('analyze_') and f.endswith('.py')
        ])
        self.assertGreaterEqual(len(self.actual), expected)

    def test_get_analyzer_classes_returns_expected_count(self):
        self.assertEqual(len(self.actual), len(EXPECT_ANALYZER_CLASSES))


class TestAnalyzerClassMeowURIs(TestCase):
    @classmethod
    def setUpClass(cls):
        import analyzers
        all_providers = analyzers.registry.all_providers
        cls.actual = [a.meowuri_prefix() for a in all_providers]
        # TODO: [TD0151] Fix inconsistent use of classes vs. class instances.
        cls.analyzer_class_names = [a.name() for a in all_providers]

    def test_returns_expected_type(self):
        from core.model import MeowURI
        for meowuri in self.actual:
            self.assertIsInstance(meowuri, MeowURI)
            self.assertTrue(C.MEOWURI_UNDEFINED_PART not in meowuri)

    def test_returns_meowuris_for_analyzers_assumed_always_available(self):
        def _assert_in(member):
            self.assertIn(member, self.actual)

        _assert_in('analyzer.document')
        _assert_in('analyzer.filename')

    def test_returns_meowuris_for_available_analyzers(self):
        def _conditional_assert_in(klass, member):
            if klass in self.analyzer_class_names:
                self.assertIn(member, self.actual)

        _conditional_assert_in('EbookAnalyzer', 'analyzer.ebook')
