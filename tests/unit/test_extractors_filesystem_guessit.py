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

from unittest import TestCase, skipIf

import unit.utils as uu
from extractors.filesystem.guessit import (
    GuessitExtractor,
    run_guessit
)
from unit.case_extractors import (
    CaseExtractorBasics,
    CaseExtractorOutput
)


UNMET_DEPENDENCIES = (
    GuessitExtractor.check_dependencies() is False,
    'Extractor dependencies ("guessit") are not available'
)


@skipIf(*UNMET_DEPENDENCIES)
class TestGuessitExtractor(CaseExtractorBasics, TestCase):
    EXTRACTOR_CLASS = GuessitExtractor
    EXTRACTOR_NAME = 'GuessitExtractor'


@skipIf(*UNMET_DEPENDENCIES)
class TestRunGuessit(TestCase):
    def test_run_guessit_no_options_returns_expected_type(self):
        actual = run_guessit('foo', options=None)
        self.assertIsInstance(actual, dict)

    def test_run_guessit_using_default_options_returns_expected_type(self):
        actual = run_guessit('foo')
        self.assertIsInstance(actual, dict)


@skipIf(*UNMET_DEPENDENCIES)
class TestGuessitExtractorOutputTestFileA(CaseExtractorOutput, TestCase):
    EXTRACTOR_CLASS = GuessitExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile('magic_mp4.mp4')
    EXPECTED_FIELD_TYPE_VALUE = [
        ('title', str, 'magic'),
    ]


@skipIf(*UNMET_DEPENDENCIES)
class TestRunGuessitWithDummyData(TestCase):
    def setUp(self):
        # NOTE: Below file name was copied from the guessit tests.
        self.data = 'Fear.and.Loathing.in.Las.Vegas.FRENCH.ENGLISH.720p.HDDVD.DTS.x264-ESiR.mkv'

    def test_run_guessit_no_options_returns_expected(self):
        actual = run_guessit(self.data, options=None)

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
            self.assertEqual(_expected, actual.get(_field))
