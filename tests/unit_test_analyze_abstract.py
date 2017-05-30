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

from core.analyze.analyze_abstract import (
    AbstractAnalyzer,
    get_analyzer_classes_basename,
    get_analyzer_mime_mappings,
    get_instantiated_analyzers,
    get_analyzer_classes
)
from core.analyze.analyze_filename import FilenameAnalyzer
from core.analyze.analyze_filesystem import FilesystemAnalyzer
from core.analyze.analyze_image import ImageAnalyzer
from core.analyze.analyze_pdf import PdfAnalyzer
from core.analyze.analyze_text import TextAnalyzer
from core.analyze.analyze_video import VideoAnalyzer
from core.config.constants import ANALYSIS_RESULTS_FIELDS
from core.exceptions import AnalysisResultsFieldError

from unit_utils import get_mock_fileobject


# TODO: [hardcoded] Likely to break; fixed analyzer names!
EXPECT_ANALYZER_CLASSES = ['core.analyze.analyze_image.ImageAnalyzer',
                           'core.analyze.analyze_filesystem.FilesystemAnalyzer',
                           'core.analyze.analyze_filename.FilenameAnalyzer',
                           'core.analyze.analyze_video.VideoAnalyzer',
                           'core.analyze.analyze_pdf.PdfAnalyzer',
                           'core.analyze.analyze_text.TextAnalyzer']
EXPECT_ANALYZER_CLASSES_BASENAME = [c.split('.')[-1]
                                    for c in EXPECT_ANALYZER_CLASSES]


class TestAbstractAnalyzer(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.a = AbstractAnalyzer(get_mock_fileobject())

    def test_run_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            self.a.run()

    def test_get_with_invalid_field_name_raises_exception(self):
        with self.assertRaises(AnalysisResultsFieldError):
            self.a.get('not_a_field')

    def test_get_with_none_field_name_raises_exception(self):
        with self.assertRaises(AnalysisResultsFieldError):
            self.a.get(None)

    def test_get_with_valid_field_name_raises_not_implemented_error(self):
        _field_name = ANALYSIS_RESULTS_FIELDS[0]
        with self.assertRaises(NotImplementedError):
            self.a.get(_field_name)

    def test_get_with_valid_field_names_raises_not_implemented_error(self):
        for _field_name in ANALYSIS_RESULTS_FIELDS:
            with self.assertRaises(NotImplementedError):
                self.a.get(_field_name)

    def test_get_datetime_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            self.a.get_datetime()

    def test_get_title_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            self.a.get_title()

    def test_get_author_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            self.a.get_author()

    def test_get_tags_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            self.a.get_tags()

    def test_get_publisher_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            self.a.get_publisher()


class TestAnalysisUtilityFunctions(TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_get_analyzer_classes_returns_expected_count(self):
        _classes = get_analyzer_classes()
        self.assertEqual(len(_classes), len(EXPECT_ANALYZER_CLASSES))

    def test_get_analyzer_classes_returns_class_objects(self):
        analyzers = get_analyzer_classes()
        for a in analyzers:
            self.assertTrue(hasattr(a, '__class__'))

    def test_get_analyzer_classes_basename_returns_expected_count(self):
        _classes = get_analyzer_classes_basename()
        self.assertEqual(len(_classes), len(EXPECT_ANALYZER_CLASSES_BASENAME))

    def test_get_analyzer_classes_basename_returns_expected_contents(self):
        _classes = get_analyzer_classes_basename()
        self.assertEqual(sorted(_classes),
                         sorted(EXPECT_ANALYZER_CLASSES_BASENAME))

    def test_get_analyzer_classes_basename_returns_list_of_strings(self):
        self.assertTrue(isinstance(get_analyzer_classes_basename(), list))

        for a in get_analyzer_classes_basename():
            self.assertTrue(isinstance(a, str))

    def test_get_analysis_mime_mappings(self):
        # TODO: [hardcoded] Likely to break; fixed analyzer type mapping.
        ANALYZER_TYPE_LOOKUP = {ImageAnalyzer: ['jpg', 'png'],
                                PdfAnalyzer: 'pdf',
                                TextAnalyzer: ['txt', 'md'],
                                VideoAnalyzer: 'mp4',
                                FilesystemAnalyzer: None,
                                FilenameAnalyzer: None}
        self.assertEqual(ANALYZER_TYPE_LOOKUP, get_analyzer_mime_mappings())

    def test_get_analyzer_mime_mappings_returns_expected_type(self):
        for analyzer, mime_type in get_analyzer_mime_mappings().items():
            self.assertEqual(type(analyzer), type)

            # TODO: Do not use None mime_type to indicate "all types" ..
            if type(mime_type) != list:
                if type(mime_type) != str:
                    from _pytest.compat import NoneType
                    if not isinstance(mime_type, NoneType):
                        self.fail('Expected type: list, str or None')


    def test_get_instantiated_analyzers_returns_class_objects(self):
        analyzers = get_instantiated_analyzers()
        for a in analyzers:
            self.assertTrue(hasattr(a, '__class__'))

    def test_get_instantiated_analyzers_returns_arbitrary_number(self):
        # TODO: [hardcoded] Likely to break; Fix or remove!
        self.assertGreaterEqual(len(get_instantiated_analyzers()), 6)

    def test_get_instantiated_analyzers_returns_list(self):
        self.assertTrue(isinstance(get_instantiated_analyzers(), list))

    #def test_get_instantiated_analyzers(self):
        # TODO: Fix test ..
        # _analyzers = get_instantiated_analyzers()
        # INSTANTIATED_ANALYZERS = [ImageAnalyzer(None), PdfAnalyzer(None),
        #                           TextAnalyzer(None), VideoAnalyzer(None),
        #                           FilesystemAnalyzer(None),
        #                           FilenameAnalyzer(None)]
        # self.assertEqual(INSTANTIATED_ANALYZERS, _analyzers)
