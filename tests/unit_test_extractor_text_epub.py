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

from unittest import (
    skipIf,
    TestCase,
)

import unit_utils as uu
from extractors.text import EpubTextExtractor
from thirdparty import epubzilla
from unit_utils_extractors import (
    CaseExtractorBasics,
    CaseExtractorOutputTypes
)


UNMET_DEPENDENCIES = not EpubTextExtractor.check_dependencies()
DEPENDENCY_ERROR = 'Extractor dependencies not satisfied'


@skipIf(UNMET_DEPENDENCIES, DEPENDENCY_ERROR)
class TestEpubTextExtractor(CaseExtractorBasics):
    __test__ = True
    EXTRACTOR_CLASS = EpubTextExtractor

    def test_method_str_returns_expected(self):
        actual = str(self.extractor)
        expect = 'EpubTextExtractor'
        self.assertEqual(actual, expect)


@skipIf(UNMET_DEPENDENCIES, DEPENDENCY_ERROR)
class TestEpubTextExtractorOutputTypes(CaseExtractorOutputTypes):
    __test__ = True
    EXTRACTOR_CLASS = EpubTextExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile('pg38145-images.epub')


# TODO:  Rework the tests or the extractors.. ?
# NOTE(jonas): Text extractors pass results to parent class that wraps the data
#              to the format returned directly by the metadata extractors ..
# @skipIf(UNMET_DEPENDENCIES, DEPENDENCY_ERROR)
# class TestEpubTextExtractorOutputTypes(TestCaseExtractorOutputTypes):
#     EXTRACTOR_CLASS = EpubTextExtractor
#     SOURCE_FILEOBJECT = uu.fileobject_testfile('magic_jpg.jpg')


@skipIf(epubzilla is None, 'Failed to import "thirdparty.epubzilla"')
class TestExtractTextWithEpubzilla(TestCase):
    def setUp(self):
        self.sample_file = uu.abspath_testfile('pg38145-images.epub')
        self.assertTrue(uu.file_exists(self.sample_file))

    def test_does_not_open_non_epub_files(self):
        not_epub_file = uu.abspath_testfile('gmail.pdf')
        self.assertTrue(uu.file_exists(not_epub_file))

        with self.assertRaises(Exception):
            _ = epubzilla.Epub.from_file(not_epub_file)

    def test_opens_sample_epub_file(self):
        actual = epubzilla.Epub.from_file(self.sample_file)
        self.assertIsNotNone(actual)

    def test_reads_sample_file_metadata(self):
        def _assert_metadata(key, expected):
            self.assertEqual(getattr(actual, key), expected)

        actual = epubzilla.Epub.from_file(self.sample_file)
        _assert_metadata('author', 'Friedrich Wilhelm Nietzsche')
        _assert_metadata('title',
                         'Human, All Too Human: A Book for Free Spirits')
