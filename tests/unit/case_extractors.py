# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg
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

import unit.utils as uu
from core import constants as C
from core.model import MeowURI
from extractors import BaseExtractor


"""
Extractor test class mixins with common functionality.
"""


class CaseExtractorOutputTypes(object):
    EXTRACTOR_CLASS = None
    SOURCE_FILEOBJECT = None

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None

        assert cls.EXTRACTOR_CLASS is not None
        assert cls.SOURCE_FILEOBJECT is not None

        cls.extractor = cls.EXTRACTOR_CLASS()
        cls.actual_extracted = cls.extractor.extract(cls.SOURCE_FILEOBJECT)

    @classmethod
    def tearDownClass(cls):
        assert cls.extractor
        if hasattr(cls.extractor, 'shutdown'):
            cls.extractor.shutdown()

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

    def test_extract_does_not_return_none(self):
        self.assertIsNotNone(
            self.actual_extracted,
            'Got None extracted data from "{!s}"'.format(self.extractor)
        )

    def test_extract_returns_expected_container_type(self):
        self.assertIsInstance(
            self.actual_extracted, dict,
            'Expected "dict". Got "{!s}"'.format(type(self.actual_extracted))
        )


ALL_TESTFILES = [
    uu.fileobject_testfile(f) for f in uu.all_testfiles()
]


class CaseExtractorBasics(object):
    EXTRACTOR_NAME = None
    EXTRACTOR_CLASS = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def setUpClass(cls):
        assert cls.EXTRACTOR_CLASS is not None
        assert cls.EXTRACTOR_NAME is not None
        cls.extractor = cls.EXTRACTOR_CLASS()

    @classmethod
    def tearDownClass(cls):
        assert cls.extractor
        if hasattr(cls.extractor, 'shutdown'):
            cls.extractor.shutdown()

    def test_instance_metainfo_returns_expected_type(self):
        actual = self.extractor.metainfo()
        self.assertIsInstance(actual, dict)

    def test_instance_metainfo_is_not_mutable(self):
        first = self.extractor.metainfo()
        first['foo'] = 'bar'
        second = self.extractor.metainfo()
        self.assertNotEqual(first, second)
        self.assertNotIn('foo', second)

    def test_class_metainfo_returns_expected_type(self):
        actual = self.EXTRACTOR_CLASS.metainfo()
        self.assertIsInstance(actual, dict)

    def test_class_metainfo_is_not_mutable(self):
        first = self.EXTRACTOR_CLASS.metainfo()
        first['foo'] = 'bar'
        second = self.EXTRACTOR_CLASS.metainfo()
        self.assertNotEqual(first, second)
        self.assertNotIn('foo', second)

    def test_instance_python_source_filepath_returns_expected_type(self):
        actual = self.extractor.python_source_filepath()
        self.assertIsInstance(actual, str)

    def test_instance_python_source_filepath_returns_an_absolute_path(self):
        actual = self.extractor.python_source_filepath()
        self.assertTrue(os.path.isabs(actual))

    def test_class_python_source_filepath_returns_expected_type(self):
        actual = self.EXTRACTOR_CLASS.python_source_filepath()
        self.assertIsInstance(actual, str)

    def test_class_python_source_filepath_returns_an_absolute_path(self):
        actual = self.EXTRACTOR_CLASS.python_source_filepath()
        self.assertTrue(os.path.isabs(actual))

    def test_instance_fieldmeta_filepath_is_path_to_an_existing_file(self):
        actual = self.extractor.fieldmeta_filepath()
        self.assertTrue(os.path.exists(actual))
        self.assertTrue(os.path.isfile(actual))

    def test_class_fieldmeta_filepath_is_path_to_an_existing_file(self):
        actual = self.EXTRACTOR_CLASS.fieldmeta_filepath()
        self.assertTrue(os.path.exists(actual))
        self.assertTrue(os.path.isfile(actual))

    def test_instance_metainfo_from_yaml_file_returns_expected_type(self):
        actual = self.extractor.metainfo_from_yaml_file()
        self.assertIsInstance(actual, dict)

    def test_instance_metainfo_from_yaml_file_returns_some_contents(self):
        actual = self.extractor.metainfo_from_yaml_file()
        self.assertGreaterEqual(len(actual), 1)

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
        self.assertIsInstance(actual, list)

    def test_class_attribute_handles_mime_type_is_a_list_of_strings(self):
        actual = self.extractor.HANDLES_MIME_TYPES
        for a in actual:
            self.assertIsInstance(a, str)

    def test_method_str_returns_type_unicode_string(self):
        actual = str(self.extractor)
        self.assertIsInstance(
            actual, str,
            'Expected "str". Got "{!s}"'.format(type(actual))
        )

    def test_method_str_returns_expected_value(self):
        actual = str(self.extractor)
        expect = self.EXTRACTOR_NAME
        self.assertEqual(expect, actual)

    def test_method_dependencies_satisfied_returns_expected_type(self):
        actual = self.extractor.dependencies_satisfied()
        self.assertIsInstance(
            actual, bool,
            'Expected "bool". Got "{!s}"'.format(type(actual))
        )

    def test_method_can_handle_returns_expected_type(self):
        actual_list = list()

        for f in ALL_TESTFILES:
            actual = self.extractor.can_handle(f)
            actual_list.append(actual)

        for actual in actual_list:
            self.assertIsInstance(
                actual, bool,
                'Expected "bool". Got "{!s}"'.format(type(actual))
            )

    def test_method_meowuri_prefix_does_not_return_none(self):
        actual = self.extractor.meowuri_prefix()
        self.assertIsNotNone(
            actual, 'expected "meowuri_prefix()" to not return none'
        )

    def test_method_meowuri_prefix_returns_instance_of_meowuri(self):
        actual = self.extractor.meowuri_prefix()
        self.assertIsInstance(actual, MeowURI)

    def test_method_meowuri_prefix_return_starts_with_extractor_root(self):
        actual = str(self.extractor.meowuri_prefix())
        expect_starts_with = C.MEOWURI_ROOT_SOURCE_EXTRACTORS
        self.assertTrue(
            actual.startswith(expect_starts_with),
            'Expected "meowuri_prefix()" to return a string that starts with '
            '"{!s}".  Got "{!s}"'.format(expect_starts_with, actual)
        )

    def test_class_method_name_returns_expected_value(self):
        expect = self.EXTRACTOR_NAME
        # TODO: [TD0151] Fix inconsistent use of classes vs. class instances.
        self.assertEqual(expect, self.EXTRACTOR_CLASS.name())
        self.assertEqual(expect, self.extractor.name())


class CaseExtractorOutput(object):
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

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None

        assert cls.EXTRACTOR_CLASS is not None
        assert cls.SOURCE_FILEOBJECT is not None

        cls.extractor = cls.EXTRACTOR_CLASS()
        cls.actual_extracted = cls.extractor.extract(cls.SOURCE_FILEOBJECT)

    @classmethod
    def tearDownClass(cls):
        assert cls.extractor
        if hasattr(cls.extractor, 'shutdown'):
            cls.extractor.shutdown()

    def test_extracted_data_is_not_none(self):
        self.assertIsNotNone(
            self.actual_extracted, 'Extracted data unexpectedly None!'
        )

    def test_extracted_data_contains_all_expected_fields(self):
        for expect_field, _, _ in self.EXPECTED_FIELD_TYPE_VALUE:
            self.assertIn(expect_field, self.actual_extracted)

    def test_extracted_data_does_not_contains_certain_fields(self):
        if hasattr(self, 'EXPECTED_NOT_PRESENT_FIELDS'):
            for expected_missing_field in self.EXPECTED_NOT_PRESENT_FIELDS:
                self.assertNotIn(expected_missing_field, self.actual_extracted)

    def test_extracted_data_contains_no_none_values_when_expected_not_none(self):
        for expect_field, _, expect_value in self.EXPECTED_FIELD_TYPE_VALUE:
            if expect_value is None:
                continue

            actual_value = self.actual_extracted.get(expect_field)
            self.assertIsNotNone(
                actual_value,
                'Field value is unexpectedly None: "{!s}"'.format(expect_field)
            )

    def test_extracted_data_has_expected_values(self):
        for expect_field, expect_type, expect_value in self.EXPECTED_FIELD_TYPE_VALUE:
            actual_value = self.actual_extracted.get(expect_field)
            self.assertEqual(expect_value, actual_value,
                             '''Assertion failed for field "{!s}"
EXPECTED VALUE of type {}:
{!s}

ACTUAL VALUE is of type {}:
{!s}
'''.format(expect_field, expect_type, expect_value, type(actual_value), actual_value))

    def test_extracted_data_has_expected_types(self):
        for expect_field, expect_type, _ in self.EXPECTED_FIELD_TYPE_VALUE:
            actual_results = self.actual_extracted.get(expect_field, None)
            if actual_results is None:
                # Fail only if types differ and not if data is missing, even
                # if it is expected to be there.
                continue

            self.assertIsInstance(
                actual_results, expect_type,
                'Expected type "{!s}" but got {!s} for "{!s}"'.format(
                    expect_type, type(actual_results), actual_results
                )
            )
