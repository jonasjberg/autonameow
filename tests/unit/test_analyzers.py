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
from unittest.mock import (
    Mock,
    patch,
    PropertyMock
)

import analyzers
from core import constants as C
import unit.utils as uu


# TODO: [hardcoded] Likely to break; fixed analyzer names!
EXPECT_ANALYZER_CLASSES = ['analyzers.analyze_image.ImageAnalyzer',
                           'analyzers.analyze_filename.FilenameAnalyzer',
                           'analyzers.analyze_filetags.FiletagsAnalyzer',
                           'analyzers.analyze_video.VideoAnalyzer',
                           'analyzers.analyze_document.DocumentAnalyzer',
                           'analyzers.analyze_text.TextAnalyzer',
                           'analyzers.analyze_ebook.EbookAnalyzer']
EXPECT_ANALYZER_CLASSES_BASENAME = [c.split('.')[-1]
                                    for c in EXPECT_ANALYZER_CLASSES]


def subclasses_base_analyzer(klass):
    return uu.is_class(klass) and issubclass(klass, analyzers.BaseAnalyzer)


class TestBaseAnalyzer(TestCase):
    def setUp(self):
        self.maxDiff = None

        self.mock_config = Mock()
        self.a = analyzers.BaseAnalyzer(
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

        self.a = analyzers.BaseAnalyzer(
            self.mock_fileobject, self.mock_config, None
        )

    def test_can_handle_raises_exception_if_none(self):
        with self.assertRaises(NotImplementedError):
            _ = self.a.can_handle(self.mock_fileobject)

    @patch('analyzers.BaseAnalyzer.HANDLES_MIME_TYPES',
           new_callable=PropertyMock, return_value=['text/plain'])
    def test_can_handle_returns_false(self, mock_attribute):
        a = analyzers.BaseAnalyzer(
            uu.get_mock_fileobject(), self.mock_config, None
        )
        actual = a.can_handle(self.mock_fileobject)
        self.assertFalse(actual)

    @patch('analyzers.BaseAnalyzer.HANDLES_MIME_TYPES',
           new_callable=PropertyMock, return_value=['image/jpeg'])
    def test_can_handle_returns_true(self, mock_attribute):
        a = analyzers.BaseAnalyzer(
            uu.get_mock_fileobject(), self.mock_config, None
        )
        actual = a.can_handle(self.mock_fileobject)
        self.assertTrue(actual)


class TestFindAnalyzerSourceFiles(TestCase):
    def test_find_analyzer_files_returns_expected_type(self):
        actual = analyzers.find_analyzer_files()
        self.assertIsInstance(actual, list)

    def test_find_analyzer_files_returns_expected_files(self):
        actual = analyzers.find_analyzer_files()

        # TODO: [hardcoded] Likely to break; requires manual updates.
        self.assertIn('analyze_filename.py', actual)
        self.assertIn('analyze_image.py', actual)
        self.assertIn('analyze_document.py', actual)
        self.assertIn('analyze_text.py', actual)
        self.assertIn('analyze_video.py', actual)


class TestGetAnalyzerClasses(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.klasses = analyzers.get_analyzer_classes()

    def test_get_analyzer_classes_returns_expected_type(self):
        self.assertIsInstance(self.klasses, list)
        for klass in self.klasses:
            self.assertTrue(issubclass(klass, analyzers.BaseAnalyzer))

    def test_get_analyzer_classes_does_not_include_abstract_classes(self):
        self.assertNotIn(analyzers.BaseAnalyzer, self.klasses)

    def test_get_analyzer_classes_returns_class_objects(self):
        for klass in self.klasses:
            self.assertTrue(uu.is_class(klass))

    def test_get_analyzer_classes_does_not_return_class_instances(self):
        for klass in self.klasses:
            self.assertFalse(uu.is_class_instance(klass))


class TestNumberOfAvailableAnalyzerClasses(TestCase):
    def setUp(self):
        self.actual = analyzers.get_analyzer_classes()

    # TODO: [hardcoded] Testing number of extractor classes needs fixing.
    def test_get_analyzer_classes_returns_at_least_one_analyzer(self):
        self.assertGreaterEqual(len(self.actual), 1)

    def test_get_analyzer_classes_returns_at_least_two_analyzers(self):
        self.assertGreaterEqual(len(self.actual), 2)

    def test_get_analyzer_classes_returns_at_least_three_analyzers(self):
        self.assertGreaterEqual(len(self.actual), 3)

    def test_get_analyzer_classes_returns_at_least_four_analyzers(self):
        self.assertGreaterEqual(len(self.actual), 4)

    def test_get_analyzer_classes_returns_at_least_five_analyzers(self):
        self.assertGreaterEqual(len(self.actual), 5)

    def test_get_analyzer_classes_returns_at_least_six_analyzers(self):
        self.assertGreaterEqual(len(self.actual), 6)

    def test_get_analyzer_classes_returns_at_least_seven(self):
        self.assertGreaterEqual(len(self.actual), 7)

    # TODO: [hardcoded] Likely to break; fixed analyzer names!
    def test_get_analyzer_classes_returns_expected_count(self):
        self.assertEqual(len(self.actual), len(EXPECT_ANALYZER_CLASSES))


class TestMapMeowURIToAnalyzers(TestCase):
    def setUp(self):
        self.actual = analyzers.map_meowuri_to_analyzers()

    def test_returns_expected_type(self):
        self.assertIsNotNone(self.actual)
        self.assertIsInstance(self.actual, dict)

        for meowuri, klass_list in self.actual.items():
            self.assertTrue(uu.is_internalstring(meowuri))
            self.assertTrue(C.UNDEFINED_MEOWURI_PART not in meowuri)

            for klass in klass_list:
                self.assertTrue(subclasses_base_analyzer(klass))
                self.assertTrue(uu.is_class(klass))

    def test_returns_one_analyzer_per_meowuri(self):
        # This assumption is likely bound to change some time soon.
        for meowuri, klass_list in self.actual.items():
            self.assertEqual(len(klass_list), 1)


class TestAnalyzerClassMeowURIs(TestCase):
    analyzer_class_names = [a.__name__ for a in analyzers.AnalyzerClasses]

    def setUp(self):
        self.actual = [a.meowuri_prefix() for a in analyzers.AnalyzerClasses]

    def test_returns_expected_type(self):
        for meowuri in self.actual:
            self.assertTrue(uu.is_internalstring(meowuri))
            self.assertTrue(C.UNDEFINED_MEOWURI_PART not in meowuri)

    def test_returns_meowuris_for_analyzers_assumed_always_available(self):
        def _assert_in(member):
            self.assertIn(member, self.actual)

        _assert_in('analyzer.document')
        _assert_in('analyzer.filename')
        _assert_in('analyzer.filetags')
        _assert_in('analyzer.image')
        _assert_in('analyzer.text')
        _assert_in('analyzer.video')

    def test_returns_meowuris_for_available_analyzers(self):
        def _conditional_assert_in(klass, member):
            if klass in self.analyzer_class_names:
                self.assertIn(member, self.actual)

        _conditional_assert_in('EbookAnalyzer',
                               'analyzer.ebook')

