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

from collections import namedtuple
from datetime import datetime
from unittest import (
    skipIf,
    TestCase,
)

import unit.utils as uu
from extractors.filesystem.filetags import (
    FiletagsExtractor,
    FiletagsParts,
    follows_filetags_convention,
    partition_basename
)
from unit.case_extractors import (
    CaseExtractorBasics,
    CaseExtractorOutput
)


UNMET_DEPENDENCIES = (
    FiletagsExtractor.check_dependencies() is False,
    'Extractor dependencies not satisfied (!)'
)
assert not UNMET_DEPENDENCIES[0], (
    'Expected extractor to not have any dependencies (always satisfied)'
)


@skipIf(*UNMET_DEPENDENCIES)
class TestFiletagsExtractor(CaseExtractorBasics, TestCase):
    EXTRACTOR_CLASS = FiletagsExtractor
    EXTRACTOR_NAME = 'FiletagsExtractor'


@skipIf(*UNMET_DEPENDENCIES)
class TestFiletagsExtractorOutputTestFileA(CaseExtractorOutput, TestCase):
    EXTRACTOR_CLASS = FiletagsExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile('2017-09-12T224820 filetags-style name -- tag2 a tag1.txt')
    EXPECTED_FIELD_TYPE_VALUE = [
        ('datetime', datetime, uu.str_to_datetime('2017-09-12 224820')),
        ('description', str, 'filetags-style name'),
        ('tags', list, ['a', 'tag1', 'tag2']),
        ('extension', str, 'txt'),
        ('follows_filetags_convention', bool, True)
    ]


@skipIf(*UNMET_DEPENDENCIES)
class TestFiletagsExtractorOutputTestFileB(CaseExtractorOutput, TestCase):
    EXTRACTOR_CLASS = FiletagsExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile('empty')
    EXPECTED_FIELD_TYPE_VALUE = [
        ('description', str, 'empty'),
        ('tags', list, []),
        ('extension', str, ''),
        ('follows_filetags_convention', bool, False)
    ]


class TestPartitionBasename(TestCase):
    def setUp(self):
        self.maxDiff = None
        Expect = namedtuple('Expect', 'timestamp description tags extension')

        self.testdata_expected = [
            (b'2010-01-31_161251.jpg',
             Expect(timestamp='2010-01-31_161251',
                    description='',
                    tags=[],
                    extension='jpg')),

            (b'2016-08-01_104304_p.n.edu oyepa - Linux tag fs -- wk pim.html',
             Expect(timestamp='2016-08-01_104304',
                    description='p.n.edu oyepa - Linux tag fs',
                    tags=['wk', 'pim'],
                    extension='html')),

            (b'2016-07-30T175241 Tablet krita_x86_xp_2.8.1.1 -- projects.png',
             Expect(timestamp='2016-07-30T175241',
                    description='Tablet krita_x86_xp_2.8.1.1',
                    tags=['projects'],
                    extension='png')),

            (b'2016-08-05_18-46-34 Working on PLL-monstret -- projects frfx.png',
             Expect(timestamp='2016-08-05_18-46-34',
                    description='Working on PLL-monstret',
                    tags=['projects', 'frfx'],
                    extension='png')),

            (b'20160722 Descriptive name -- firsttag tagtwo.txt',
             Expect(timestamp='20160722',
                    description='Descriptive name',
                    tags=['firsttag', 'tagtwo'],
                    extension='txt')),

            (b'.tar.gz name -- gz firsttag 2ndtag.tar.gz',
             Expect(timestamp=None,
                    description='.tar.gz name',
                    tags=['gz', 'firsttag', '2ndtag'],
                    extension='tar.gz')),

            (b'.tar name -- gz firsttag 2ndtag.tar.gz',
             Expect(timestamp=None,
                    description='.tar name',
                    tags=['gz', 'firsttag', '2ndtag'],
                    extension='tar.gz')),

            (b'.name -- tar firsttag 2ndtag.tar.gz',
             Expect(timestamp=None,
                    description='.name',
                    tags=['tar', 'firsttag', '2ndtag'],
                    extension='tar.gz')),

            (b'.name -- firsttag 2ndtag.tar.gz',
             Expect(timestamp=None,
                    description='.name',
                    tags=['firsttag', '2ndtag'],
                    extension='tar.gz')),

            (b'.name -- firsttag 2ndtag.jpg',
             Expect(timestamp=None,
                    description='.name',
                    tags=['firsttag', '2ndtag'],
                    extension='jpg')),

            (b'.name.tar.gz',
             Expect(timestamp=None,
                    description='.name',
                    tags=[],
                    extension='tar.gz')),

            (b'.name.jpg',
             Expect(timestamp=None,
                    description='.name',
                    tags=[],
                    extension='jpg')),

            (b'.name',
             Expect(timestamp=None,
                    description='.name',
                    tags=[],
                    extension='')),

            (b'19920722 --Descriptive-- name -- firsttag tagtwo.txt',
             Expect(timestamp='19920722',
                    description='--Descriptive-- name',
                    tags=['firsttag', 'tagtwo'],
                    extension='txt')),

            (b'19990212 Descriptive name -- firsttag tagtwo.txt',
             Expect(timestamp='19990212',
                    description='Descriptive name',
                    tags=['firsttag', 'tagtwo'],
                    extension='txt')),

            (b'20160722 Descriptive name.txt',
             Expect(timestamp='20160722',
                    description='Descriptive name',
                    tags=[],
                    extension='txt')),

            (b'2017-09-29_06-04-15 Running autonameow on a lot of files with empty caches -- dev projects.png',
             Expect(timestamp='2017-09-29_06-04-15',
                    description='Running autonameow on a lot of files with empty caches',
                    tags=['dev', 'projects'],
                    extension='png')),

            (b'2017-09-01T215342 People make people UML reflexive assocation -- 1dv607 lnu screenshot macbookpro.png',
             Expect(timestamp='2017-09-01T215342',
                    description='People make people UML reflexive assocation',
                    tags=['1dv607', 'lnu', 'screenshot', 'macbookpro'],
                    extension='png')),

            (b'2017-09-12T224820 filetags-style name -- tag2 a tag1.txt',
             Expect(timestamp='2017-09-12T224820',
                    description='filetags-style name',
                    tags=['tag2', 'a', 'tag1'],
                    extension='txt')),

            # Extra spaces after the last tag
            (b'2017-11-16T001411 Windows 10 VM PowerShell -- dev screenshot skylake .png',
             Expect(timestamp='2017-11-16T001411',
                    description='Windows 10 VM PowerShell',
                    tags=['dev', 'screenshot', 'skylake'],
                    extension='png')),

            # Extra spaces after the last tag
            (b'2017-11-16T001411 Windows 10 VM PowerShell -- dev screenshot skylake  .png',
             Expect(timestamp='2017-11-16T001411',
                    description='Windows 10 VM PowerShell',
                    tags=['dev', 'screenshot', 'skylake'],
                    extension='png')),

            # Extra spaces between tag separator and first tag
            (b'2017-11-16T001411 Windows 10 VM PowerShell --  dev screenshot skylake.png',
             Expect(timestamp='2017-11-16T001411',
                    description='Windows 10 VM PowerShell',
                    tags=['dev', 'screenshot', 'skylake'],
                    extension='png')),

            # Extra spaces between tag separator and first tag and after last tag
            (b'2017-11-16T001411 Windows 10 VM PowerShell --  dev screenshot skylake .png',
             Expect(timestamp='2017-11-16T001411',
                    description='Windows 10 VM PowerShell',
                    tags=['dev', 'screenshot', 'skylake'],
                    extension='png')),

            # Extra spaces between tags
            (b'2017-11-16T001411 Windows 10 VM PowerShell -- dev  screenshot skylake.png',
             Expect(timestamp='2017-11-16T001411',
                    description='Windows 10 VM PowerShell',
                    tags=['dev', 'screenshot', 'skylake'],
                    extension='png')),

            # Extra spaces between tag separator and first tag and between tags
            (b'2017-11-16T001411 Windows 10 VM PowerShell --  dev  screenshot skylake.png',
             Expect(timestamp='2017-11-16T001411',
                    description='Windows 10 VM PowerShell',
                    tags=['dev', 'screenshot', 'skylake'],
                    extension='png')),

            # Extra spaces between tag separator tag and after last tag
            (b'2017-11-16T001411 Windows 10 VM PowerShell --  dev  screenshot skylake .png',
             Expect(timestamp='2017-11-16T001411',
                    description='Windows 10 VM PowerShell',
                    tags=['dev', 'screenshot', 'skylake'],
                    extension='png')),

            (b'Advanced Data Science and Machine Learning for Cats - Paws-on Machine Learning.djvu',
             Expect(timestamp=None,
                    description='Advanced Data Science and Machine Learning for Cats - Paws-on Machine Learning',
                    tags=[],
                    extension='djvu')),
        ]

    def test_partitions_basenames(self):
        for test_data, expected in self.testdata_expected:
            actual = partition_basename(test_data)
            self.assertEqual(expected, actual)


class TestFollowsFiletagsConvention(TestCase):
    # TODO: Clean up this mess!
    def _assert(self, expect, given):
        assert isinstance(expect, bool)
        empty = {'datetime': '',
                 'description': '',
                 'tags': [],
                 'extension': ''}
        empty.update(given)
        parts = FiletagsParts(empty['datetime'], empty['description'], empty['tags'], empty['extension'])
        actual = follows_filetags_convention(parts)
        self.assertEqual(expect, actual)

    def test_filetags_name_with_all_parts(self):
        self._assert(True, given={'datetime': '2018-02-11',
                                  'description': 'foo',
                                  'tags': ['a', 'b'],
                                  'extension': 'txt'})

    def test_filetags_name_with_datetime_description_tags(self):
        self._assert(True, given={'datetime': '2018-02-11',
                                  'description': 'foo',
                                  'tags': ['a', 'b']})

    def test_filetags_name_with_datetime_description_extension(self):
        self._assert(False, given={'datetime': '2018-02-11',
                                   'description': 'foo',
                                   'extension': 'txt'})

    def test_filetags_name_with_datetime_description(self):
        self._assert(False, given={'datetime': '2018-02-11',
                                   'description': 'foo'})

    def test_filetags_name_with_datetime(self):
        self._assert(False, given={'datetime': '2018-02-11'})
