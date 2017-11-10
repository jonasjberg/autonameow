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

from collections import namedtuple
from unittest import TestCase

from analyzers import analyze_filetags

import unit_utils as uu


def get_filetags_analyzer(fileobject):
    return analyze_filetags.FiletagsAnalyzer(
        fileobject,
        uu.get_default_config(),
        request_data_callback=uu.mock_request_data_callback
    )


class TestFiletagsAnalyzer(TestCase):
    def setUp(self):
        self.fileobject = uu.get_named_fileobject('2010-01-31_161251.jpg')
        self.analyzer = get_filetags_analyzer(self.fileobject)

    def test_setup(self):
        self.assertIsNotNone(self.fileobject)
        self.assertIsNotNone(self.analyzer)


class TestPartitionBasename(TestCase):
    def setUp(self):
        self.maxDiff = None
        Expect = namedtuple('Expect', 'timestamp description tags extension')

        self.testdata_expected = [
            (b'2010-01-31_161251.jpg',
             Expect('2010-01-31_161251', None, [], 'jpg')),

            (b'2016-08-01_104304_p.n.edu oyepa - Linux tag fs -- wk pim.html',
             Expect('2016-08-01_104304', 'p.n.edu oyepa - Linux tag fs',
                    ['wk', 'pim'], 'html')),

            (b'2016-07-30T175241 Tablet krita_x86_xp_2.8.1.1 -- projects.png',
             Expect('2016-07-30T175241', 'Tablet krita_x86_xp_2.8.1.1',
                    ['projects'], 'png')),

            (b'2016-08-05_18-46-34 Working on PLL-monstret -- projects frfx.png',
             Expect('2016-08-05_18-46-34', 'Working on PLL-monstret',
                    ['projects', 'frfx'], 'png')),

            (b'20160722 Descriptive name -- firsttag tagtwo.txt',
             Expect('20160722', 'Descriptive name',
                    ['firsttag', 'tagtwo'], 'txt')),

            (b'.tar.gz name -- gz firsttag 2ndtag.tar.gz',
             Expect(None, '.tar.gz name',
                    ['gz', 'firsttag', '2ndtag'], 'tar.gz')),

            (b'.tar name -- gz firsttag 2ndtag.tar.gz',
             Expect(None, '.tar name',
                    ['gz', 'firsttag', '2ndtag'], 'tar.gz')),

            (b'.name -- tar firsttag 2ndtag.tar.gz',
             Expect(None, '.name', ['tar', 'firsttag', '2ndtag'], 'tar.gz')),

            (b'.name -- firsttag 2ndtag.tar.gz',
             Expect(None, '.name', ['firsttag', '2ndtag'], 'tar.gz')),

            (b'.name -- firsttag 2ndtag.jpg',
             Expect(None, '.name', ['firsttag', '2ndtag'], 'jpg')),

            (b'.name.tar.gz',
             Expect(None, '.name', [], 'tar.gz')),

            (b'.name.jpg',
             Expect(None, '.name', [], 'jpg')),

            (b'.name',
             Expect(None, '.name', [], None)),

            (b'19920722 --Descriptive-- name -- firsttag tagtwo.txt',
             Expect('19920722', '--Descriptive-- name',
                    ['firsttag', 'tagtwo'], 'txt')),

            (b'19990212 Descriptive name -- firsttag tagtwo.txt',
             Expect('19990212', 'Descriptive name',
                    ['firsttag', 'tagtwo'], 'txt')),

            (b'20160722 Descriptive name.txt',
             Expect('20160722', 'Descriptive name', [], 'txt')),

            (b'2017-09-29_06-04-15 Running autonameow on a lot of files with empty caches -- dev projects.png',
             Expect('2017-09-29_06-04-15', 'Running autonameow on a lot of files with empty caches',
                    ['dev', 'projects'], 'png')),

            (b'2017-09-01T215342 People make people UML reflexive assocation -- 1dv607 lnu screenshot macbookpro.png',
             Expect('2017-09-01T215342', 'People make people UML reflexive assocation',
                    ['1dv607', 'lnu', 'screenshot', 'macbookpro'], 'png')),
        ]

    def test_partitions_basenames(self):
        for test_data, expected in self.testdata_expected:
            actual = analyze_filetags.partition_basename(test_data)
            self.assertEqual(actual, expected)


