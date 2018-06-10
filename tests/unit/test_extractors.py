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

from unittest import TestCase

import unit.utils as uu
from extractors import AUTONAMEOW_EXTRACTOR_PATH
from extractors import EXTRACTOR_CLASS_PACKAGES
from extractors import EXTRACTOR_CLASS_PACKAGES_FILESYSTEM
from extractors import EXTRACTOR_CLASS_PACKAGES_METADATA
from extractors import _find_extractor_classes_in_packages
from extractors import collect_included_excluded_extractors
from extractors.metadata.base import BaseMetadataExtractor


def _collect_included_excluded_extractors(**kwargs):
    packages = kwargs.get('packages', dict())
    return collect_included_excluded_extractors(packages)


class TestExtractorsConstants(TestCase):
    def test_autonameow_extractor_path_is_defined(self):
        self.assertIsNotNone(AUTONAMEOW_EXTRACTOR_PATH)

    def test_extractor_path_is_an_existing_directory(self):
        self.assertTrue(
            uu.dir_exists(AUTONAMEOW_EXTRACTOR_PATH)
        )

    def test_extractor_path_contains_expected_top_level_directory(self):
        _top = 'extractors'
        self.assertTrue(AUTONAMEOW_EXTRACTOR_PATH.endswith(_top))

    def _assert_list_of_strings(self, given):
        self.assertIsInstance(given, list)
        for element in given:
            self.assertIsInstance(element, str)

    def test_extractor_class_packages(self):
        self._assert_list_of_strings(EXTRACTOR_CLASS_PACKAGES)

    def test_extractor_class_packages_filesystem(self):
        self._assert_list_of_strings(EXTRACTOR_CLASS_PACKAGES_FILESYSTEM)

    def test_extractor_class_packages_metadata(self):
        self._assert_list_of_strings(EXTRACTOR_CLASS_PACKAGES_METADATA)


class TestFindExtractorClassesInPackages(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.actual = _find_extractor_classes_in_packages(EXTRACTOR_CLASS_PACKAGES)

    def test_returns_expected_type(self):
        self.assertIsInstance(self.actual, list)

    def test_returns_subclasses_of_base_extractor(self):
        for klass in self.actual:
            with self.subTest(klass):
                self.assertTrue(uu.is_class(klass))
                self.assertTrue(issubclass(klass, BaseMetadataExtractor))

    def test_does_not_include_base_extractor(self):
        self.assertNotIn(BaseMetadataExtractor, self.actual)


class TestCollectAndCheckExtractorClassesIncluded(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.actual, _ = _collect_included_excluded_extractors(
            packages=EXTRACTOR_CLASS_PACKAGES,
        )

    def test_get_extractor_classes_returns_expected_type(self):
        self.assertIsInstance(self.actual, list)

    def test_get_extractor_classes_returns_subclasses_of_base_extractor(self):
        for klass in self.actual:
            self.assertTrue(uu.is_class(klass))
            self.assertTrue(issubclass(klass, BaseMetadataExtractor))

    def test_get_extractor_classes_does_not_include_base_extractor(self):
        self.assertNotIn(BaseMetadataExtractor, self.actual)

    def test_get_extractor_classes_does_not_include_abstract_extractors(self):
        from extractors.text.base import BaseTextExtractor
        self.assertNotIn(BaseTextExtractor, self.actual)


class TestCollectAndCheckMetadataExtractorClassesIncluded(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.actual, _ = _collect_included_excluded_extractors(
            packages=EXTRACTOR_CLASS_PACKAGES_METADATA,
        )

    def test_get_extractor_classes_returns_expected_type(self):
        self.assertIsInstance(self.actual, list)

    def test_get_extractor_classes_returns_subclasses_of_base_extractor(self):
        for klass in self.actual:
            self.assertTrue(uu.is_class(klass))
            self.assertTrue(issubclass(klass, BaseMetadataExtractor))

    def test_get_extractor_classes_does_not_include_base_extractor(self):
        self.assertNotIn(BaseMetadataExtractor, self.actual)

    def test_get_extractor_classes_does_not_include_abstract_extractors(self):
        from extractors.text.base import BaseTextExtractor
        self.assertNotIn(BaseTextExtractor, self.actual)

    def test_returns_metadata_extractors_verified_by_name(self):
        for klass in self.actual:
            # TODO: [TD0151] Fix inconsistent use of classes vs. class instances.
            _klass_name = klass.name()
            self.assertIn('Metadata', _klass_name)

    def test_returns_metadata_extractors_verified_by_meowuri_prefix(self):
        for klass in self.actual:
            _meowuri_prefix = str(klass.meowuri_prefix())
            self.assertTrue(_meowuri_prefix.startswith('extractor.metadata'))


class TestExtractorClassMeowURIs(TestCase):
    @classmethod
    def setUpClass(cls):
        provider_klasses, _ = _collect_included_excluded_extractors(
            packages=EXTRACTOR_CLASS_PACKAGES
        )
        # TODO: [TD0151] Fix inconsistent use of classes vs. class instances.
        cls.extractor_class_names = [e.name() for e in provider_klasses]

    def _assert_collected_included(self, extractor_name):
        self.assertIn(extractor_name, self.extractor_class_names)

    def test_collects_assumedly_available_extractors(self):
        self._assert_collected_included('CrossPlatformFileSystemExtractor')
        self._assert_collected_included('ExiftoolMetadataExtractor')


class TestNumberOfAvailableExtractorClasses(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.actual, _ = _collect_included_excluded_extractors(
            packages=EXTRACTOR_CLASS_PACKAGES,
        )

    # This tests up to the current number of extractors without dependencies.
    # TODO: [hardcoded] Testing number of extractor classes needs fixing.
    def test_get_extractor_classes_returns_at_least_one_extractor(self):
        self.assertGreaterEqual(len(self.actual), 1)

    def test_get_extractor_classes_returns_at_least_two_extractors(self):
        self.assertGreaterEqual(len(self.actual), 2)

    def test_get_extractor_classes_returns_at_least_three_extractors(self):
        self.assertGreaterEqual(len(self.actual), 3)
