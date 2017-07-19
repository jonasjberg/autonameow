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
import unit_utils as uu

from analyzers.analyzer import (
    Analyzer
)
from analyzers.analyze_filename import FilenameAnalyzer
from analyzers.analyze_filesystem import FilesystemAnalyzer
from analyzers.analyze_image import ImageAnalyzer
from analyzers.analyze_pdf import PdfAnalyzer
from analyzers.analyze_text import TextAnalyzer
from analyzers.analyze_video import VideoAnalyzer
from core.constants import ANALYSIS_RESULTS_FIELDS
from core.exceptions import AnalysisResultsFieldError


def get_filename_analyzer(file_object):
    return FilenameAnalyzer(file_object, None)


class TestAnalyzer(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.a = Analyzer(uu.get_mock_fileobject(), None, None)

        class DummyFileObject(object):
            def __init__(self):
                self.mime_type = 'image/jpeg'
        self.dummy_fo = DummyFileObject()

    def test_run_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            self.a.run()

    def test_get_with_invalid_field_name_raises_exception(self):
        with self.assertRaises(AnalysisResultsFieldError):
            self.a.get('not_a_field')

    def test_get_with_invalid_non_callable_field_name_raises_exception(self):
        with self.assertRaises(AnalysisResultsFieldError):
            self.a.get('__str__')

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

    def test_class_method_can_handle_is_defined_and_does_not_return_none(self):
        self.assertIsNotNone(self.a.can_handle)
        self.assertIsNotNone(self.a.can_handle(self.dummy_fo))

    def test_class_method_can_handle_returns_false(self):
        self.assertFalse(self.a.can_handle(self.dummy_fo))
