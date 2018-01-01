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
from unittest import TestCase
from unittest.mock import Mock

import unit.utils as uu
from analyzers.analyze_filetags import (
    FiletagsAnalyzer,
    partition_basename
)


def get_filetags_analyzer(fileobject):
    mock_config = Mock()

    return FiletagsAnalyzer(
        fileobject,
        mock_config,
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
             Expect(timestamp='2010-01-31_161251',
                    description=None,
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
                    extension=None)),

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

            (b'2017-11-16T001411 Windows 10 VM PowerShell -- dev screenshot skylake .png',
             Expect(timestamp='2017-11-16T001411',
                    description='Windows 10 VM PowerShell',
                    tags=['dev', 'screenshot', 'skylake'],
                    extension='png')),

            (b'2017-11-16T001411 Windows 10 VM PowerShell -- dev screenshot skylake  .png',
             Expect(timestamp='2017-11-16T001411',
                    description='Windows 10 VM PowerShell',
                    tags=['dev', 'screenshot', 'skylake'],
                    extension='png')),

            (b'2017-11-16T001411 Windows 10 VM PowerShell --  dev screenshot skylake.png',
             Expect(timestamp='2017-11-16T001411',
                    description='Windows 10 VM PowerShell',
                    tags=['dev', 'screenshot', 'skylake'],
                    extension='png')),

            (b'2017-11-16T001411 Windows 10 VM PowerShell --  dev screenshot skylake .png',
             Expect(timestamp='2017-11-16T001411',
                    description='Windows 10 VM PowerShell',
                    tags=['dev', 'screenshot', 'skylake'],
                    extension='png')),

            (b'2017-11-16T001411 Windows 10 VM PowerShell -- dev  screenshot skylake.png',
             Expect(timestamp='2017-11-16T001411',
                    description='Windows 10 VM PowerShell',
                    tags=['dev', 'screenshot', 'skylake'],
                    extension='png')),

            (b'2017-11-16T001411 Windows 10 VM PowerShell --  dev  screenshot skylake.png',
             Expect(timestamp='2017-11-16T001411',
                    description='Windows 10 VM PowerShell',
                    tags=['dev', 'screenshot', 'skylake'],
                    extension='png')),

            (b'2017-11-16T001411 Windows 10 VM PowerShell --  dev  screenshot skylake .png',
             Expect(timestamp='2017-11-16T001411',
                    description='Windows 10 VM PowerShell',
                    tags=['dev', 'screenshot', 'skylake'],
                    extension='png')),
        ]

    def test_partitions_basenames(self):
        for test_data, expected in self.testdata_expected:
            actual = partition_basename(test_data)
            self.assertEqual(expected, actual)


