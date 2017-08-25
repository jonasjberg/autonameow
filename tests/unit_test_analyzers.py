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

import analyzers
from core import (
    exceptions,
    constants
)
import unit_utils as uu


# TODO: [hardcoded] Likely to break; fixed analyzer names!
EXPECT_ANALYZER_CLASSES = ['analyzers.analyze_image.ImageAnalyzer',
                           'analyzers.analyze_filesystem.FilesystemAnalyzer',
                           'analyzers.analyze_filename.FilenameAnalyzer',
                           'analyzers.analyze_filetags.FiletagsAnalyzer',
                           'analyzers.analyze_video.VideoAnalyzer',
                           'analyzers.analyze_pdf.PdfAnalyzer',
                           'analyzers.analyze_text.TextAnalyzer',
                           'analyzers.analyze_ebook.EbookAnalyzer']
EXPECT_ANALYZER_CLASSES_BASENAME = [c.split('.')[-1]
                                    for c in EXPECT_ANALYZER_CLASSES]


class TestBaseAnalyzer(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.a = analyzers.BaseAnalyzer(uu.get_mock_fileobject(), None, None)

        class DummyFileObject(object):
            def __init__(self):
                self.mime_type = 'image/jpeg'
        self.dummy_fo = DummyFileObject()

    def test_run_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            self.a.run()

    def test_get_with_invalid_field_name_raises_exception(self):
        with self.assertRaises(exceptions.AnalysisResultsFieldError):
            self.a.get('not_a_field')

    def test_get_with_invalid_non_callable_field_name_raises_exception(self):
        with self.assertRaises(exceptions.AnalysisResultsFieldError):
            self.a.get('__str__')

    def test_get_with_none_field_name_raises_exception(self):
        with self.assertRaises(exceptions.AnalysisResultsFieldError):
            self.a.get(None)

    def test_get_with_valid_field_name_raises_attribute_error(self):
        _field_name = constants.ANALYSIS_RESULTS_FIELDS[0]
        with self.assertRaises(NotImplementedError):
            self.a.get(_field_name)

    def test_get_with_valid_field_names_raises_not_implemented_error(self):
        for _field_name in constants.ANALYSIS_RESULTS_FIELDS:
            with self.assertRaises(NotImplementedError):
                self.a.get(_field_name)

    def test_get_datetime_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.a.get_datetime()

    def test_get_title_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.a.get_title()

    def test_get_author_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.a.get_author()

    def test_get_tags_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.a.get_tags()

    def test_get_publisher_raises_attrbitute_error(self):
        with self.assertRaises(AttributeError):
            self.a.get_publisher()

    def test_class_method_can_handle_is_defined_and_does_not_return_none(self):
        self.assertIsNotNone(self.a.can_handle)
        self.assertIsNotNone(self.a.can_handle(self.dummy_fo))

    def test_class_method_can_handle_returns_false(self):
        self.assertFalse(self.a.can_handle(self.dummy_fo))


class TestFindAnalyzerSourceFiles(TestCase):
    def test_find_analyzer_files_is_defined(self):
        self.assertIsNotNone(analyzers.find_analyzer_files)

    def test_find_analyzer_files_returns_expected_type(self):
        actual = analyzers.find_analyzer_files()
        self.assertTrue(isinstance(actual, list))

    def test_find_analyzer_files_returns_expected_files(self):
        actual = analyzers.find_analyzer_files()

        # TODO: [hardcoded] Likely to break; requires manual updates.
        self.assertIn('analyze_filename.py', actual)
        self.assertIn('analyze_filesystem.py', actual)
        self.assertIn('analyze_image.py', actual)
        self.assertIn('analyze_pdf.py', actual)
        self.assertIn('analyze_text.py', actual)
        self.assertIn('analyze_video.py', actual)


class TestSuitableAnalyzersForFile(TestCase):
    def test_returns_expected_analyzers_for_mp4_video_file(self):
        self.fo = uu.get_mock_fileobject(mime_type='video/mp4')
        actual = [c.__name__ for c in
                  analyzers.suitable_analyzers_for(self.fo)]
        self.assertIn('FilesystemAnalyzer', actual)
        self.assertIn('FilenameAnalyzer', actual)
        self.assertIn('VideoAnalyzer', actual)

    def test_returns_expected_analyzers_for_png_image_file(self):
        self.fo = uu.get_mock_fileobject(mime_type='image/png')
        actual = [c.__name__ for c in
                  analyzers.suitable_analyzers_for(self.fo)]
        self.assertIn('FilenameAnalyzer', actual)
        self.assertIn('FilesystemAnalyzer', actual)
        self.assertIn('ImageAnalyzer', actual)

    def test_returns_expected_analyzers_for_pdf_file(self):
        self.fo = uu.get_mock_fileobject(mime_type='application/pdf')
        actual = [c.__name__ for c in
                  analyzers.suitable_analyzers_for(self.fo)]
        self.assertIn('FilenameAnalyzer', actual)
        self.assertIn('FilesystemAnalyzer', actual)
        self.assertIn('PdfAnalyzer', actual)


class TestGetAnalyzerClasses(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.klasses = analyzers.get_analyzer_classes()

    def test_get_analyzer_classes_returns_expected_type(self):
        self.assertTrue(isinstance(self.klasses, list))
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

