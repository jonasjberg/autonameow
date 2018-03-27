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
from core import constants as C
from extractors import (
    AUTONAMEOW_EXTRACTOR_PATH,
    EXTRACTOR_CLASS_PACKAGES,
    EXTRACTOR_CLASS_PACKAGES_FILESYSTEM,
    EXTRACTOR_CLASS_PACKAGES_METADATA,
    EXTRACTOR_CLASS_PACKAGES_TEXT,
    _find_extractor_classes_in_packages,
    _get_extractor_classes,
)
from extractors.common import BaseExtractor


def get_extractor_classes(**kwargs):
    packages = kwargs.get('packages', dict())
    return _get_extractor_classes(packages)


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

    def test_extractor_class_packages_text(self):
        self._assert_list_of_strings(EXTRACTOR_CLASS_PACKAGES_TEXT)


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
                self.assertTrue(issubclass(klass, BaseExtractor))

    def test_does_not_include_base_extractor(self):
        self.assertNotIn(BaseExtractor, self.actual)


class TestGetImplementedExtractorClasses(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.actual, _ = get_extractor_classes(
            packages=EXTRACTOR_CLASS_PACKAGES,
        )

    def test_get_extractor_classes_returns_expected_type(self):
        self.assertIsInstance(self.actual, list)

    def test_get_extractor_classes_returns_subclasses_of_base_extractor(self):
        for klass in self.actual:
            self.assertTrue(uu.is_class(klass))
            self.assertTrue(issubclass(klass, BaseExtractor))

    def test_get_extractor_classes_does_not_include_base_extractor(self):
        self.assertNotIn(BaseExtractor, self.actual)

    def test_get_extractor_classes_does_not_include_abstract_extractors(self):
        from extractors.text.common import AbstractTextExtractor
        self.assertNotIn(AbstractTextExtractor, self.actual)


class TestGetTextExtractorClasses(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.actual, _ = get_extractor_classes(
            packages=EXTRACTOR_CLASS_PACKAGES_TEXT,
        )

    def test_get_extractor_classes_returns_expected_type(self):
        self.assertIsInstance(self.actual, list)

    def test_get_extractor_classes_returns_subclasses_of_base_extractor(self):
        for klass in self.actual:
            self.assertTrue(uu.is_class(klass))
            self.assertTrue(issubclass(klass, BaseExtractor))

    def test_get_extractor_classes_does_not_include_base_extractor(self):
        self.assertNotIn(BaseExtractor, self.actual)

    def test_get_extractor_classes_does_not_include_abstract_extractors(self):
        from extractors.text.common import AbstractTextExtractor
        self.assertNotIn(AbstractTextExtractor, self.actual)

    def test_returns_text_extractors(self):
        from extractors.text.common import AbstractTextExtractor
        for klass in self.actual:
            self.assertTrue(issubclass(klass, AbstractTextExtractor))


class TestGetMetadataExtractorClasses(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.actual, _ = get_extractor_classes(
            packages=EXTRACTOR_CLASS_PACKAGES_METADATA,
        )

    def test_get_extractor_classes_returns_expected_type(self):
        self.assertIsInstance(self.actual, list)

    def test_get_extractor_classes_returns_subclasses_of_base_extractor(self):
        for klass in self.actual:
            self.assertTrue(uu.is_class(klass))
            self.assertTrue(issubclass(klass, BaseExtractor))

    def test_get_extractor_classes_does_not_include_base_extractor(self):
        self.assertNotIn(BaseExtractor, self.actual)

    def test_get_extractor_classes_does_not_include_abstract_extractors(self):
        from extractors.text.common import AbstractTextExtractor
        self.assertNotIn(AbstractTextExtractor, self.actual)

    def test_returns_metadata_extractors_verified_by_name(self):
        for klass in self.actual:
            # TODO: [TD0151] Fix inconsistent use of classes vs. class instances.
            _klass_name = klass.name()
            self.assertIn('Metadata', _klass_name)

    def test_returns_metadata_extractors_verified_by_meowuri_prefix(self):
        for klass in self.actual:
            _meowuri_prefix = str(klass.meowuri_prefix())
            self.assertTrue(_meowuri_prefix.startswith('extractor.metadata'))


class TestNumberOfAvailableExtractorClasses(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.actual, _ = get_extractor_classes(
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


class TestExtractorClassMeowURIs(TestCase):
    @classmethod
    def setUpClass(cls):
        provider_klasses, _ = get_extractor_classes(
            packages=EXTRACTOR_CLASS_PACKAGES
        )
        # TODO: [TD0151] Fix inconsistent use of classes vs. class instances.
        cls.extractor_class_names = [e.name() for e in provider_klasses]
        cls.actual = [k.meowuri_prefix() for k in provider_klasses]

    def test_returns_expected_type(self):
        from core.model import MeowURI
        for meowuri in self.actual:
            self.assertIsInstance(meowuri, MeowURI)
            self.assertTrue(C.UNDEFINED_MEOWURI_PART not in meowuri)

    def test_returns_meowuris_for_extractors_assumed_always_available(self):
        def _assert_in(member):
            self.assertIn(member, self.actual)

        _assert_in('extractor.filesystem.xplat')
        _assert_in('extractor.text.plain')

    def test_returns_meowuris_for_available_extractors(self):
        def _conditional_assert_in(klass, member):
            if klass in self.extractor_class_names:
                self.assertIn(member, self.actual)

        _conditional_assert_in('CrossPlatformFileSystemExtractor',
                               'extractor.filesystem.xplat')
        _conditional_assert_in('ExiftoolMetadataExtractor',
                               'extractor.metadata.exiftool')
        _conditional_assert_in('PdfTextExtractor',
                               'extractor.text.pdf')
        _conditional_assert_in('TesseractOCRTextExtractor',
                               'extractor.text.tesseractocr')
        _conditional_assert_in('RichTextFormatTextExtractor',
                               'extractor.text.rtf')
        _conditional_assert_in('MarkdownTextExtractor',
                               'extractor.text.markdown')
