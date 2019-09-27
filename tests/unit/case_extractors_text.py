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

import unit.utils as uu
from extractors.text.base import BaseTextExtractor


"""
Text extractor test class mixins with common functionality.
"""


class CaseTextExtractorOutputTypes(object):
    EXTRACTOR_CLASS = None
    SOURCE_FILEOBJECT = None

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None

        assert cls.EXTRACTOR_CLASS is not None
        assert cls.SOURCE_FILEOBJECT is not None

        cls.extractor = cls.EXTRACTOR_CLASS()
        # Disable the cache
        cls.extractor.cache = None

        cls.actual_extracted = cls.extractor.extract_text(cls.SOURCE_FILEOBJECT)

    @classmethod
    def tearDownClass(cls):
        assert cls.extractor
        if hasattr(cls.extractor, 'shutdown'):
            cls.extractor.shutdown()

    def test_instantiated_extractor_is_not_none(self):
        actual = self.extractor
        self.assertIsNotNone(
            actual,
            'Got None when instantiating text extractor: "{!s}" ({!s})'.format(
                self.EXTRACTOR_CLASS, type(self.EXTRACTOR_CLASS)
            )
        )

    def test_instantiated_extractor_is_class_instance(self):
        actual = self.extractor
        self.assertTrue(
            uu.is_class_instance(actual),
            'Instantiated text extractor is not a class instance: '
            '"{!s}" ({!s})'.format(actual, type(actual))
        )

    def test_instantiated_extractor_is_subclass_of_base_extractor(self):
        actual = self.extractor
        self.assertTrue(
            issubclass(actual.__class__, BaseTextExtractor),
            'Instantiated text extractor is not a subclass of "BaseExtractor": '
            '"{!s}" ({!s})'.format(actual, type(actual))
        )

    def test_extract_does_not_return_none(self):
        self.assertIsNotNone(
            self.actual_extracted,
            'Got None extracted data from "{!s}"'.format(self.extractor)
        )

    def test_extract_returns_expected_type(self):
        self.assertIsInstance(
            self.actual_extracted, str,
            'Expected type "str". Got "{!s}"'.format(type(self.actual_extracted))
        )


ALL_TESTFILES = [
    uu.fileobject_testfile(f) for f in uu.all_samplefiles()
]


class CaseTextExtractorBasics(object):
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

    def test_instantiated_text_extractor_is_not_none(self):
        actual = self.extractor
        self.assertIsNotNone(
            actual,
            'Got None when instantiating text extractor: "{!s}" ({!s})'.format(
                self.EXTRACTOR_CLASS, type(self.EXTRACTOR_CLASS)
            )
        )

    def test_instantiated_text_extractor_is_class_instance(self):
        actual = self.extractor
        self.assertTrue(
            uu.is_class_instance(actual),
            'Instantiated text extractor is not a class instance: '
            '"{!s}" ({!s})'.format(actual, type(actual))
        )

    def test_instantiated_extractor_is_subclass_of_base_text_extractor(self):
        actual = self.extractor
        self.assertTrue(
            issubclass(actual.__class__, BaseTextExtractor),
            'Instantiated text extractor is not a subclass of "BaseExtractor": '
            '"{!s}" ({!s})'.format(actual, type(actual))
        )

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

    def test_class_method_name_returns_expected_value(self):
        # TODO: [TD0151] Fix inconsistent use of classes vs. class instances.
        expect = self.EXTRACTOR_NAME
        self.assertEqual(expect, self.EXTRACTOR_CLASS.name())
        self.assertEqual(expect, self.extractor.name())


class CaseTextExtractorOutput(object):
    EXTRACTOR_CLASS = None
    SOURCE_FILEOBJECT = None

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None

        assert cls.EXTRACTOR_CLASS is not None
        assert cls.SOURCE_FILEOBJECT is not None
        assert cls.EXPECTED_TEXT is not None

        cls.extractor = cls.EXTRACTOR_CLASS()
        # Disable the cache
        cls.extractor.cache = None

        cls.actual_text = cls.extractor.extract_text(cls.SOURCE_FILEOBJECT)

    @classmethod
    def tearDownClass(cls):
        assert cls.extractor
        if hasattr(cls.extractor, 'shutdown'):
            cls.extractor.shutdown()

    def test_extracted_text_is_not_none(self):
        self.assertIsNotNone(
            self.actual_text, 'Extracted text is unexpectedly None!'
        )

    def test_extracted_text_has_expected_values(self):
        self.assertEqual(self.EXPECTED_TEXT, self.actual_text)

    def test_extracted_text_is_of_expected_type(self):
        self.assertIsInstance(self.actual_text, str)

