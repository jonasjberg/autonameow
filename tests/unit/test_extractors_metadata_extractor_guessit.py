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

from unittest import TestCase, skipIf

import unit.utils as uu
from extractors.metadata.extractor_guessit import get_lazily_imported_guessit_module
from extractors.metadata.extractor_guessit import GuessitMetadataExtractor
from extractors.metadata.extractor_guessit import reset_lazily_imported_guessit_module
from extractors.metadata.extractor_guessit import run_guessit
from unit.case_extractors import CaseExtractorBasics
from unit.case_extractors import CaseExtractorOutput


UNMET_DEPENDENCIES = (
    not GuessitMetadataExtractor.dependencies_satisfied(),
    'Extractor dependencies ("guessit") not satified'
)


@skipIf(*UNMET_DEPENDENCIES)
class TestGuessitMetadataExtractor(CaseExtractorBasics, TestCase):
    EXTRACTOR_CLASS = GuessitMetadataExtractor
    EXTRACTOR_NAME = 'GuessitMetadataExtractor'


@skipIf(*UNMET_DEPENDENCIES)
class TestRunGuessit(TestCase):
    def setUp(self):
        self.guessit_module = get_lazily_imported_guessit_module()

    def tearDown(self):
        self.guessit_module = None
        reset_lazily_imported_guessit_module()

    def test_run_guessit_no_options_returns_expected_type(self):
        actual = run_guessit('foo', self.guessit_module, options=None)
        self.assertIsInstance(actual, dict)

    def test_run_guessit_using_default_options_returns_expected_type(self):
        actual = run_guessit('foo', self.guessit_module)
        self.assertIsInstance(actual, dict)


@skipIf(*UNMET_DEPENDENCIES)
class TestGuessitMetadataExtractorOutputTestFileA(CaseExtractorOutput, TestCase):
    EXTRACTOR_CLASS = GuessitMetadataExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile('magic_mp4.mp4')
    EXPECTED_FIELD_TYPE_VALUE = [
        ('title', str, 'magic'),
    ]


@skipIf(*UNMET_DEPENDENCIES)
class TestRunGuessitWithDummyData(TestCase):
    def setUp(self):
        # NOTE: Below file name was copied from the guessit tests.
        self.data = 'Fear.and.Loathing.in.Las.Vegas.FRENCH.ENGLISH.720p.HDDVD.DTS.x264-ESiR.mkv'
        self.guessit_module = get_lazily_imported_guessit_module()

    def tearDown(self):
        self.guessit_module = None
        reset_lazily_imported_guessit_module()

    def test_run_guessit_no_options_returns_expected(self):
        actual = run_guessit(self.data, self.guessit_module, options=None)

        field_expected = [('title', 'Fear and Loathing in Las Vegas'),
                          ('type', 'movie'),
                          # ('language', ['fr', 'en']),
                          ('screen_size', '720p'),
                          ('format', 'HD-DVD'),
                          ('audio_codec', 'DTS'),
                          ('video_codec', 'h264'),
                          ('release_group', 'ESiR'),
                          ('container', 'mkv'),
                          ('mimetype', 'video/x-matroska')]

        for _field, _expected in field_expected:
            with self.subTest():
                self.assertEqual(_expected, actual.get(_field))
