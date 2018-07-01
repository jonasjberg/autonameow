# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg <autonameow@jonasjberg.com>
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

from collections import namedtuple
from datetime import datetime
from unittest import skipIf, TestCase
from unittest.mock import Mock

import unit.utils as uu
from extractors.filesystem.filetags import FiletagsExtractor
from extractors.filesystem.filetags import FiletagsParts
from extractors.filesystem.filetags import follows_filetags_convention
from extractors.filesystem.filetags import split_basename_prefix_into_filetags_parts
from unit.case_extractors import CaseExtractorBasics
from unit.case_extractors import CaseExtractorOutput


UNMET_DEPENDENCIES = (
    FiletagsExtractor.dependencies_satisfied() is False,
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


def _get_mock_fileobject(prefix, suffix):
    mock_fileobject = Mock()
    mock_fileobject.basename_prefix = prefix
    mock_fileobject.basename_suffix = suffix
    return mock_fileobject


@skipIf(*UNMET_DEPENDENCIES)
class TestFiletagsExtractorOutputTestFileC(CaseExtractorOutput, TestCase):
    EXTRACTOR_CLASS = FiletagsExtractor
    SOURCE_FILEOBJECT = _get_mock_fileobject(
        prefix=b'2018-06-29 kunskapsmatris sprak',
        suffix=b'xlsx'
    )
    EXPECTED_FIELD_TYPE_VALUE = [
        ('date', datetime, datetime(2018, 6, 29)),
        ('description', str, 'kunskapsmatris sprak'),
        ('tags', list, []),
        ('extension', str, 'xlsx'),
        ('follows_filetags_convention', bool, False)
    ]


@skipIf(*UNMET_DEPENDENCIES)
class TestFiletagsExtractorOutputTestFileD(CaseExtractorOutput, TestCase):
    EXTRACTOR_CLASS = FiletagsExtractor
    SOURCE_FILEOBJECT = _get_mock_fileobject(
        prefix=b'2007-04-23_12-comments',
        suffix=b'png'
    )
    EXPECTED_FIELD_TYPE_VALUE = [
        ('date', datetime, datetime(2007, 4, 23)),
        ('description', str, '_12-comments'),
        ('tags', list, []),
        ('extension', str, 'png'),
        ('follows_filetags_convention', bool, False)
    ]


class TestSplitBasenamePrefixIntoFiletagsParts(TestCase):
    def setUp(self):
        Expect = namedtuple('Expect', 'timestamp description tags')

        self.testdata_expected = [
            ('2010-01-31_161251',
             Expect(timestamp='2010-01-31_161251',
                    description=None,
                    tags=[])),

            ('2016-08-01_104304_p.n.edu oyepa - Linux tag fs -- wk pim',
             Expect(timestamp='2016-08-01_104304',
                    description='p.n.edu oyepa - Linux tag fs',
                    tags=['wk', 'pim'])),

            ('2016-07-30T175241 Tablet krita_x86_xp_2.8.1.1 -- projects',
             Expect(timestamp='2016-07-30T175241',
                    description='Tablet krita_x86_xp_2.8.1.1',
                    tags=['projects'])),

            ('2016-08-05_18-46-34 Working on PLL-monstret -- projects frfx',
             Expect(timestamp='2016-08-05_18-46-34',
                    description='Working on PLL-monstret',
                    tags=['projects', 'frfx'])),

            ('20160722 Descriptive name -- firsttag tagtwo',
             Expect(timestamp='20160722',
                    description='Descriptive name',
                    tags=['firsttag', 'tagtwo'])),

            ('.tar.gz name -- gz firsttag 2ndtag',
             Expect(timestamp=None,
                    description='.tar.gz name',
                    tags=['gz', 'firsttag', '2ndtag'])),

            ('.tar name -- gz firsttag 2ndtag',
             Expect(timestamp=None,
                    description='.tar name',
                    tags=['gz', 'firsttag', '2ndtag'])),

            ('.name -- tar firsttag 2ndtag',
             Expect(timestamp=None,
                    description='.name',
                    tags=['tar', 'firsttag', '2ndtag'])),

            ('.name -- firsttag 2ndtag',
             Expect(timestamp=None,
                    description='.name',
                    tags=['firsttag', '2ndtag'])),

            ('.name -- firsttag 2ndtag',
             Expect(timestamp=None,
                    description='.name',
                    tags=['firsttag', '2ndtag'])),

            ('.name',
             Expect(timestamp=None,
                    description='.name',
                    tags=[])),

            ('19920722 --Descriptive-- name -- firsttag tagtwo',
             Expect(timestamp='19920722',
                    description='--Descriptive-- name',
                    tags=['firsttag', 'tagtwo'])),

            ('19990212 Descriptive name -- firsttag tagtwo',
             Expect(timestamp='19990212',
                    description='Descriptive name',
                    tags=['firsttag', 'tagtwo'])),

            ('20160722 Descriptive name',
             Expect(timestamp='20160722',
                    description='Descriptive name',
                    tags=[])),

            ('2017-09-29_06-04-15 Running autonameow on a lot of files with empty caches -- dev projects',
             Expect(timestamp='2017-09-29_06-04-15',
                    description='Running autonameow on a lot of files with empty caches',
                    tags=['dev', 'projects'])),

            ('2017-09-01T215342 People make people UML reflexive assocation -- 1dv607 lnu screenshot macbookpro',
             Expect(timestamp='2017-09-01T215342',
                    description='People make people UML reflexive assocation',
                    tags=['1dv607', 'lnu', 'screenshot', 'macbookpro'])),

            ('2017-09-12T224820 filetags-style name -- tag2 a tag1',
             Expect(timestamp='2017-09-12T224820',
                    description='filetags-style name',
                    tags=['tag2', 'a', 'tag1'])),

            # Extra spaces after the last tag
            ('2017-11-16T001411 Windows 10 VM PowerShell -- dev screenshot skylake ',
             Expect(timestamp='2017-11-16T001411',
                    description='Windows 10 VM PowerShell',
                    tags=['dev', 'screenshot', 'skylake'])),

            # Extra spaces after the last tag
            ('2017-11-16T001411 Windows 10 VM PowerShell -- dev screenshot skylake  ',
             Expect(timestamp='2017-11-16T001411',
                    description='Windows 10 VM PowerShell',
                    tags=['dev', 'screenshot', 'skylake'])),

            # Extra spaces between tag separator and first tag
            ('2017-11-16T001411 Windows 10 VM PowerShell --  dev screenshot skylake',
             Expect(timestamp='2017-11-16T001411',
                    description='Windows 10 VM PowerShell',
                    tags=['dev', 'screenshot', 'skylake'])),

            # Extra spaces between tag separator and first tag and after last tag
            ('2017-11-16T001411 Windows 10 VM PowerShell --  dev screenshot skylake ',
             Expect(timestamp='2017-11-16T001411',
                    description='Windows 10 VM PowerShell',
                    tags=['dev', 'screenshot', 'skylake'])),

            # Extra spaces between tags
            ('2017-11-16T001411 Windows 10 VM PowerShell -- dev  screenshot skylake',
             Expect(timestamp='2017-11-16T001411',
                    description='Windows 10 VM PowerShell',
                    tags=['dev', 'screenshot', 'skylake'])),

            # Extra spaces between tag separator and first tag and between tags
            ('2017-11-16T001411 Windows 10 VM PowerShell --  dev  screenshot skylake',
             Expect(timestamp='2017-11-16T001411',
                    description='Windows 10 VM PowerShell',
                    tags=['dev', 'screenshot', 'skylake'])),

            # Extra spaces between tag separator tag and after last tag
            ('2017-11-16T001411 Windows 10 VM PowerShell --  dev  screenshot skylake ',
             Expect(timestamp='2017-11-16T001411',
                    description='Windows 10 VM PowerShell',
                    tags=['dev', 'screenshot', 'skylake'])),

            ('Advanced Data Science and Machine Learning for Cats - Paws-on Machine Learning',
             Expect(timestamp=None,
                    description='Advanced Data Science and Machine Learning for Cats - Paws-on Machine Learning',
                    tags=[])),

            ('2018-06-29 kunskapsmatris sprak',
             Expect(timestamp='2018-06-29',
                    description='kunskapsmatris sprak',
                    tags=[])),
        ]

    def test_splits_basename_prefixes_into_filetags_parts(self):
        for given_basename_prefix, expected in self.testdata_expected:
            with self.subTest():
                actual = split_basename_prefix_into_filetags_parts(
                    given_basename_prefix,
                    sep_between_tags=' ',
                    sep_tags_start=' -- '
                )
                self.assertEqual(expected, actual)


class TestFollowsFiletagsConvention(TestCase):
    def _assert(self, expect, **kwargs):
        assert isinstance(expect, bool)
        filetags_parts = FiletagsParts(
            timestamp=kwargs.get('timestamp', ''),
            description=kwargs.get('description', ''),
            tags=kwargs.get('tags', []),
        )
        actual = follows_filetags_convention(filetags_parts)
        self.assertEqual(expect, actual)

    def test_filetags_name_with_all_parts(self):
        self._assert(True, timestamp='2018-02-11',
                           description='foo',
                           tags=['a', 'b'])

    def test_filetags_name_with_timestamp_description_tags(self):
        self._assert(True, timestamp='2018-02-11',
                           description='foo',
                           tags=['a', 'b'])

    def test_filetags_name_with_timestamp_description_extension(self):
        self._assert(False, timestamp='2018-02-11',
                            description='foo')
        self._assert(False, timestamp='2018-06-29',
                            description='kunskapsmatris sprak')

    def test_filetags_name_with_timestamp_description(self):
        self._assert(False, timestamp='2018-02-11',
                            description='foo')

    def test_filetags_name_with_timestamp(self):
        self._assert(False, timestamp='2018-02-11')
