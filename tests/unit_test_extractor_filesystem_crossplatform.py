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

from datetime import datetime
from unittest import (
    skipIf,
    TestCase,
)

import unit_utils as uu
from extractors.filesystem.crossplatform import (
    CrossPlatformFileSystemExtractor,
    datetime_from_timestamp
)
from unit_utils_extractors import CaseExtractorBasics


# This really shouldn't happen. Probably caused by an error if it does.
DEPENDENCY_ERROR = 'Extractor dependencies not satisfied (!)'
UNMET_DEPENDENCIES = CrossPlatformFileSystemExtractor.check_dependencies() is False
assert not UNMET_DEPENDENCIES


@skipIf(UNMET_DEPENDENCIES, DEPENDENCY_ERROR)
class TestPlainTextExtractor(CaseExtractorBasics):
    __test__ = True
    EXTRACTOR_CLASS = CrossPlatformFileSystemExtractor

    def test_method_str_returns_expected(self):
        actual = str(self.extractor)
        expect = 'CrossPlatformFileSystemExtractor'
        self.assertEqual(actual, expect)


ALL_EXTRACTOR_FIELDS_TYPES = [
    ('abspath.full', bytes),
    ('basename.full', bytes),
    ('basename.extension', bytes),
    ('basename.suffix', bytes),
    ('basename.prefix', bytes),
    ('pathname.full', bytes),
    ('pathname.parent', bytes),
    ('contents.mime_type', str),
    ('date_accessed', datetime),
    ('date_created', datetime),
    ('date_modified', datetime)
]


class TestDatetimeFromTimestamp(TestCase):
    def test_returns_expected_type(self):
        actual = datetime_from_timestamp(1505579505.0)
        self.assertTrue(isinstance(actual, datetime))

    def test_returns_expected_datetime(self):
        actual = datetime_from_timestamp(1505579505.0)
        expected = uu.str_to_datetime('2017-09-16 183145')
        self.assertEqual(actual, expected)


class TestCrossPlatformFileSystemExtractorExtractTestFileText(TestCase):
    def setUp(self):
        _fo = uu.fileobject_testfile('magic_txt.txt')
        _extractor_instance = CrossPlatformFileSystemExtractor()
        self.actual = _extractor_instance.extract(_fo)

    def test_extract_returns_expected_type(self):
        self.assertTrue(isinstance(self.actual, dict))

    def test_extract_returns_expected_keys(self):
        for _field, _ in ALL_EXTRACTOR_FIELDS_TYPES:
            self.assertIn(_field, self.actual)

    def test_extract_returns_expected_values(self):
        def _aE(field, expected):
            actual = self.actual.get(field)
            self.assertEqual(actual, expected)

        self.assertTrue(self.actual.get('abspath.full', b'').endswith(
            b'test_files/magic_txt.txt'
        ))
        _aE('basename.full', b'magic_txt.txt')
        _aE('basename.extension', b'txt')
        _aE('basename.suffix', b'txt')
        _aE('basename.prefix', b'magic_txt')
        # _aE('pathname.full', 'TODO')
        # _aE('pathname.parent', 'TODO)
        _aE('contents.mime_type', 'text/plain')
        # _aE('date_accessed', 'TODO')
        # _aE('date_created', 'TODO')
        # _aE('date_modified', 'TODO')

    def test_extract_returns_expected_types(self):
        for _field, _type in ALL_EXTRACTOR_FIELDS_TYPES:
            actual = self.actual.get(_field)
            self.assertTrue(isinstance(actual, _type))


class TestCrossPlatformFileSystemExtractorExtractTestFileEmpty(TestCase):
    def setUp(self):
        _fo = uu.fileobject_testfile('empty')
        _extractor_instance = CrossPlatformFileSystemExtractor()
        self.actual = _extractor_instance.extract(_fo)

    def test_extract_returns_expected_type(self):
        self.assertTrue(isinstance(self.actual, dict))

    def test_extract_returns_expected_keys(self):
        for _field, _ in ALL_EXTRACTOR_FIELDS_TYPES:
            self.assertIn(_field, self.actual)

    def test_extract_returns_expected_values(self):
        def _aE(field, expected):
            actual = self.actual.get(field)
            self.assertEqual(actual, expected)

        self.assertTrue(self.actual.get('abspath.full', b'').endswith(
            b'test_files/empty'
        ))
        _aE('basename.full', b'empty')
        _aE('basename.extension', b'')
        _aE('basename.suffix', b'')
        _aE('basename.prefix', b'empty')
        # _aE('pathname.full', 'TODO')
        # _aE('pathname.parent', 'TODO)
        _aE('contents.mime_type', 'inode/x-empty')
        # _aE('date_accessed', 'TODO')
        # _aE('date_created', 'TODO')
        # _aE('date_modified', 'TODO')

    def test_extract_returns_expected_types(self):
        for _field, _type in ALL_EXTRACTOR_FIELDS_TYPES:
            actual = self.actual.get(_field)
            self.assertTrue(isinstance(actual, _type))


class TestCrossPlatformFileSystemExtractorMetainfo(TestCase):
    def setUp(self):
        _extractor_instance = CrossPlatformFileSystemExtractor()
        self.actual = _extractor_instance.metainfo()

    def test_metainfo_returns_expected_type(self):
        self.assertTrue(isinstance(self.actual, dict))

    def test_metainfo_returns_expected_fields(self):
        for _field, _ in ALL_EXTRACTOR_FIELDS_TYPES:
            self.assertIn(_field, self.actual)

    def test_metainfo_specifies_types_for_all_fields(self):
        for _field, _ in ALL_EXTRACTOR_FIELDS_TYPES:
            self.assertIn('coercer', self.actual.get(_field, {}))

    def test_metainfo_multiple_is_bool_or_none(self):
        for _field, _ in ALL_EXTRACTOR_FIELDS_TYPES:
            _field_lookup_entry = self.actual.get(_field, {})
            self.assertIn('multivalued', _field_lookup_entry)

            actual = _field_lookup_entry.get('multivalued')
            self.assertTrue(isinstance(actual, (bool, type(None))))
