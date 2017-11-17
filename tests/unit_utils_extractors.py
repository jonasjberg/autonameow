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

import unittest

import unit_utils as uu
from extractors import BaseExtractor

"""
Shared utilities for extractor unit tests.
"""


class TestCaseExtractorOutputTypes(unittest.TestCase):
    __test__ = False

    EXTRACTOR_CLASS = None
    SOURCE_FILEOBJECT = None

    def setUp(self):
        if self.EXTRACTOR_CLASS is None:
            self.skipTest('Base class attribute "EXTRACTOR_CLASS" is None')

        if self.SOURCE_FILEOBJECT is None:
            self.skipTest('Base class attribute "SOURCE_FILEOBJECT" is None')

        self.extractor = self.EXTRACTOR_CLASS()
        self.actual_extracted = self.extractor.extract(self.SOURCE_FILEOBJECT)

    def test_instantiated_extractor_is_not_none(self):
        actual = self.extractor
        self.assertIsNotNone(
            actual,
            'Got None when instantiating extractor: "{!s}" ({!s})'.format(
                self.EXTRACTOR_CLASS, type(self.EXTRACTOR_CLASS)
            )
        )

    def test_instantiated_extractor_is_class_instance(self):
        actual = self.extractor
        self.assertTrue(
            uu.is_class_instance(actual),
            'Instantiated extractor is not a class instance: '
            '"{!s}" ({!s})'.format(actual, type(actual))
        )

    def test_instantiated_extractor_is_subclass_of_base_extractor(self):
        actual = self.extractor
        self.assertTrue(
            issubclass(actual.__class__, BaseExtractor),
            'Instantiated extractor is not a subclass of "BaseExtractor": '
            '"{!s}" ({!s})'.format(actual, type(actual))
        )

    def test_setup_extracts_data_from_fileobject_source(self):
        actual = self.actual_extracted
        self.assertIsNotNone(
            actual,
            'None extracted by "{!s}" from source "{!s}"'.format(
                self.extractor, self.SOURCE_FILEOBJECT
            )
        )

    def test_extract_does_not_return_none(self):
        _actual_extracted = self.actual_extracted
        self.assertIsNotNone(
            _actual_extracted,
            'Got None extracted data from "{!s}"'.format(self.extractor)
        )

    def test_extract_returns_expected_outer_type(self):
        _actual_extracted = self.actual_extracted
        self.assertTrue(
            isinstance(_actual_extracted, dict),
            'Expected "dict". Got "{!s}"'.format(type(_actual_extracted))
        )

    def test_extract_returns_expected_contained_types(self):
        _actual_extracted = self.actual_extracted
        for meowuri, datadict in _actual_extracted.items():
            self.assertTrue(
                isinstance(datadict, dict),
                'Expected "dict". Got "{!s}" for MeowURI "{!s}"'.format(
                    type(datadict), meowuri
                )
            )


ALL_TESTFILES = [
    uu.fileobject_testfile(f) for f in uu.all_testfiles()
]


class TestCaseExtractorBasics(unittest.TestCase):
    __test__ = False

    EXTRACTOR_CLASS = None

    def setUp(self):
        if self.EXTRACTOR_CLASS is None:
            self.skipTest('Base class attribute "EXTRACTOR_CLASS" is None')

        self.extractor = self.EXTRACTOR_CLASS()

    def test_instantiated_extractor_is_not_none(self):
        actual = self.extractor
        self.assertIsNotNone(
            actual,
            'Got None when instantiating extractor: "{!s}" ({!s})'.format(
                self.EXTRACTOR_CLASS, type(self.EXTRACTOR_CLASS)
            )
        )

    def test_instantiated_extractor_is_class_instance(self):
        actual = self.extractor
        self.assertTrue(
            uu.is_class_instance(actual),
            'Instantiated extractor is not a class instance: '
            '"{!s}" ({!s})'.format(actual, type(actual))
        )

    def test_instantiated_extractor_is_subclass_of_base_extractor(self):
        actual = self.extractor
        self.assertTrue(
            issubclass(actual.__class__, BaseExtractor),
            'Instantiated extractor is not a subclass of "BaseExtractor": '
            '"{!s}" ({!s})'.format(actual, type(actual))
        )

    def test_class_attribute_handles_mime_type_is_not_none(self):
        actual = self.extractor.HANDLES_MIME_TYPES
        self.assertIsNotNone(actual)

    def test_class_attribute_handles_mime_type_is_a_list(self):
        actual = self.extractor.HANDLES_MIME_TYPES
        self.assertTrue(isinstance(actual, list))

    def test_class_attribute_handles_mime_type_is_a_list_of_strings(self):
        actual = self.extractor.HANDLES_MIME_TYPES
        for a in actual:
            self.assertTrue(isinstance(a, str))

    def test_method_str_returns_type_unicode_string(self):
        actual = str(self.extractor)
        self.assertTrue(
            isinstance(actual, str),
            'Expected "str". Got "{!s}"'.format(type(actual))
        )

    def test_method_check_dependencies_returns_expected_type(self):
        actual = self.extractor.check_dependencies()
        self.assertTrue(
            isinstance(actual, bool),
            'Expected "bool". Got "{!s}"'.format(type(actual))
        )

    def test_method_can_handle_returns_expected_type(self):
        actual_list = []

        for f in ALL_TESTFILES:
            actual = self.extractor.can_handle(f)
            actual_list.append(actual)

        for actual in actual_list:
            self.assertTrue(
                isinstance(actual, bool),
                'Expected "bool". Got "{!s}"'.format(type(actual))
            )


class TestCaseExtractorOutput(unittest.TestCase):
    __test__ = False

    EXTRACTOR_CLASS = None
    SOURCE_FILEOBJECT = None

    # List of tuples of expected extracted data for a given "SOURCE_FILEOBJECT"
    #
    # Tuple values:    FIELD      EXPECTED_TYPE   EXPECTED_VALUE
    #      Example:    'is_jpeg'  bool            True
    #
    EXPECTED_FIELD_TYPE_VALUE = [
        (None, None, None),
    ]

    def setUp(self):
        if self.EXTRACTOR_CLASS is None:
            self.skipTest('Base class attribute "EXTRACTOR_CLASS" is None')

        if self.SOURCE_FILEOBJECT is None:
            self.skipTest('Base class attribute "SOURCE_FILEOBJECT" is None')

        self.extractor = self.EXTRACTOR_CLASS()
        self.actual_extracted = self.extractor.extract(self.SOURCE_FILEOBJECT)

    def test_extracted_data_is_not_none(self):
        self.assertIsNotNone(
            self.actual_extracted, 'Extracted data unexpectedly None!'
        )

    def test_extracted_data_contains_all_expected_fields(self):
        for expect_field, _, expect_value in self.EXPECTED_FIELD_TYPE_VALUE:
            self.assertIn(expect_field, self.actual_extracted)

    def test_extracted_data_contains_no_none_values_when_expected_not_none(self):
        for expect_field, _, expect_value in self.EXPECTED_FIELD_TYPE_VALUE:
            if expect_value is None:
                continue

            actual_datadict = self.actual_extracted.get(expect_field)
            actual_value = actual_datadict.get('value')
            self.assertIsNotNone(
                actual_value,
                'Field value is unexpectedly None: "{!s}"'.format(expect_field)
            )

    def test_extracted_data_has_expected_values(self):
        for expect_field, expect_type, expect_value in self.EXPECTED_FIELD_TYPE_VALUE:
            actual_datadict = self.actual_extracted.get(expect_field)
            actual_value = actual_datadict.get('value')
            self.assertEqual(
                actual_value, expect_value,
                '[{!s}] :: Expected "{!s}" ({!s}) NOT "{!s}" ({!s})'.format(
                    expect_field, expect_value, expect_type, actual_value,
                    type(actual_value)
                )
            )

    def test_extracted_data_has_expected_types(self):
        for expect_field, expect_type, _ in self.EXPECTED_FIELD_TYPE_VALUE:
            actual_datadict = self.actual_extracted.get(expect_field)
            actual_value = actual_datadict.get('value')
            self.assertTrue(
                isinstance(actual_value, expect_type),
                'Expected "{!s}" ({!s}) to be of type "{!s}"'.format(
                    actual_value, type(actual_value), expect_type
                )
            )
