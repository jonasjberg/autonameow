# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2020 Jonas Sjöberg <autonameow@jonasjberg.com>
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

from datetime import datetime
from unittest import skipIf, TestCase

import unit.utils as uu
from extractors.metadata.extractor_crossplatform import CrossPlatformFileSystemExtractor
from extractors.metadata.extractor_crossplatform import datetime_from_timestamp
from unit.case_extractors import CaseExtractorBasics


UNMET_DEPENDENCIES = (
    not CrossPlatformFileSystemExtractor.dependencies_satisfied(),
    'Extractor dependencies not satisfied'
)
assert not UNMET_DEPENDENCIES[0], (
    'Expected extractor to not have any dependencies (always satisfied)'
)


@skipIf(*UNMET_DEPENDENCIES)
class TestCrossPlatformFileSystemExtractor(CaseExtractorBasics, TestCase):
    EXTRACTOR_CLASS = CrossPlatformFileSystemExtractor
    EXTRACTOR_NAME = 'CrossPlatformFileSystemExtractor'


ALL_EXTRACTOR_FIELDS_TYPES = [
    ('abspath_full', bytes),
    ('basename_full', bytes),
    ('extension', bytes),
    ('basename_suffix', bytes),
    ('basename_prefix', bytes),
    ('pathname_full', bytes),
    ('pathname_parent', bytes),
    ('mime_type', str),
    ('date_accessed', datetime),
    ('date_created', datetime),
    ('date_modified', datetime)
]


class TestDatetimeFromTimestamp(TestCase):
    def test_returns_expected_type(self):
        actual = datetime_from_timestamp(1505579505.0)
        self.assertIsInstance(actual, datetime)

    def test_returns_expected_datetime(self):
        actual = datetime_from_timestamp(1505579505.0)
        expected = uu.str_to_datetime('2017-09-16 183145')
        self.assertEqual(actual, expected)


class TestCrossPlatformFileSystemExtractorExtractSamplefileText(TestCase):
    @classmethod
    def setUpClass(cls):
        _fo = uu.fileobject_from_samplefile('magic_txt.txt')
        _extractor_instance = CrossPlatformFileSystemExtractor()
        cls.actual = _extractor_instance.extract(_fo)

    def test_extract_returns_expected_type(self):
        self.assertIsInstance(self.actual, dict)

    def test_extract_returns_expected_keys(self):
        for _field, _ in ALL_EXTRACTOR_FIELDS_TYPES:
            self.assertIn(_field, self.actual)

    def test_extract_returns_expected_values(self):
        def _aE(field, expected):
            actual = self.actual.get(field)
            self.assertEqual(actual, expected)

        self.assertTrue(self.actual.get('abspath_full', b'').endswith(
            b'samplefiles/magic_txt.txt'
        ))
        _aE('basename_full', b'magic_txt.txt')
        _aE('extension', b'txt')
        _aE('basename_suffix', b'txt')
        _aE('basename_prefix', b'magic_txt')
        # _aE('pathname_full', 'TODO')
        # _aE('pathname_parent', 'TODO)
        _aE('mime_type', 'text/plain')
        # _aE('date_accessed', 'TODO')
        # _aE('date_created', 'TODO')
        # _aE('date_modified', 'TODO')

    def test_extract_returns_expected_types(self):
        for _field, _type in ALL_EXTRACTOR_FIELDS_TYPES:
            actual = self.actual.get(_field)
            self.assertIsInstance(actual, _type)


class TestCrossPlatformFileSystemExtractorExtractSamplefileEmpty(TestCase):
    @classmethod
    def setUpClass(cls):
        _fo = uu.fileobject_from_samplefile('empty')
        _extractor_instance = CrossPlatformFileSystemExtractor()
        cls.actual = _extractor_instance.extract(_fo)

    def test_extract_returns_expected_type(self):
        self.assertIsInstance(self.actual, dict)

    def test_extract_returns_expected_keys(self):
        for _field, _ in ALL_EXTRACTOR_FIELDS_TYPES:
            self.assertIn(_field, self.actual)

    def test_extract_returns_expected_values(self):
        def _aE(field, expected):
            actual = self.actual.get(field)
            self.assertEqual(actual, expected)

        self.assertTrue(self.actual.get('abspath_full', b'').endswith(
            b'samplefiles/empty'
        ))
        _aE('basename_full', b'empty')
        _aE('extension', b'')
        _aE('basename_suffix', b'')
        _aE('basename_prefix', b'empty')
        # _aE('pathname_full', 'TODO')
        # _aE('pathname_parent', 'TODO)
        _aE('mime_type', 'inode/x-empty')
        # _aE('date_accessed', 'TODO')
        # _aE('date_created', 'TODO')
        # _aE('date_modified', 'TODO')

    def test_extract_returns_expected_types(self):
        for _field, _type in ALL_EXTRACTOR_FIELDS_TYPES:
            actual = self.actual.get(_field)
            self.assertIsInstance(actual, _type)


class TestCrossPlatformFileSystemExtractorMetainfo(TestCase):
    @classmethod
    def setUpClass(cls):
        _extractor_instance = CrossPlatformFileSystemExtractor()
        cls.actual = _extractor_instance.metainfo()

    def test_metainfo_returns_expected_type(self):
        self.assertIsInstance(self.actual, dict)

    def test_metainfo_returns_expected_fields(self):
        for _field, _ in ALL_EXTRACTOR_FIELDS_TYPES:
            self.assertIn(_field, self.actual)

    def test_metainfo_specifies_types_for_all_fields(self):
        for _field, _ in ALL_EXTRACTOR_FIELDS_TYPES:
            self.assertIn('coercer', self.actual.get(_field, {}))

    def test_metainfo_multivalued_is_none_or_boolean(self):
        for _field, _ in ALL_EXTRACTOR_FIELDS_TYPES:
            _field_lookup_entry = self.actual.get(_field, {})
            self.assertIn('multivalued', _field_lookup_entry)

            actual = _field_lookup_entry.get('multivalued')
            self.assertIsInstance(actual, (bool, type(None)))


class TestFieldFileobjectAttributeMap(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.actual_map = CrossPlatformFileSystemExtractor.FIELD_FILEOBJECT_ATTRIBUTE_MAP
        cls.fo = uu.get_mock_fileobject()

    def test_map_field_names_are_non_empty_unicode_strings(self):
        for field, _ in self.actual_map:
            with self.subTest(field=field):
                self.assertIsInstance(field, str)
                self.assertGreater(len(field), 0)

    def test_map_field_names_are_unique(self):
        seen = set()
        all_fields = [field for field, _ in self.actual_map]
        all_fields_deduped = set(all_fields)
        self.assertEqual(len(all_fields), len(all_fields_deduped))

    def test_attributes_defined_in_map_are_all_part_of_actual_fileobject(self):
        for _, attribute in self.actual_map:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.fo, attribute))

    def test_attributes_defined_in_map_are_not_none_in_actual_fileobject(self):
        for _, attribute in self.actual_map:
            with self.subTest(attribute=attribute):
                actual_attr_value = getattr(self.fo, attribute)
                self.assertIsNotNone(actual_attr_value)
