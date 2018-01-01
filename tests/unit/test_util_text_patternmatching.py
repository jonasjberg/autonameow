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

from core import types
from util.text.patternmatching import (
    compiled_ordinal_regexes,
    find_edition,
    find_publisher_in_copyright_notice
)


class TestCompiledOrdinalRegexes(TestCase):
    def setUp(self):
        self.actual = compiled_ordinal_regexes()

    def test_returns_expected_type(self):
        self.assertIsNotNone(self.actual)
        self.assertIsInstance(self.actual, dict)

    def test_returns_compiled_regular_expressions(self):
        re_one = self.actual.get(1)
        self.assertIsInstance(re_one, types.BUILTIN_REGEX_TYPE)

        for _pattern in self.actual.values():
            self.assertIsInstance(_pattern, types.BUILTIN_REGEX_TYPE)

    def test_returned_regexes_matches_strings(self):
        def _aM(test_input):
            match = self.actual.get(2).search(test_input)
            actual = match.group(0)
            expected = 2
            self.assertTrue(actual, expected)

        _aM('2nd')
        _aM('second')
        _aM('SECOND')
        _aM('foo 2nd bar')
        _aM('foo 2ND bar')


class TestFindEdition(TestCase):
    # TODO: [TD0118] Improve robustness and refactor finding editions in text.
    def test_returns_expected_edition(self):
        def _aE(test_input, expected):
            self.assertEqual(find_edition(test_input), expected)

        _aE('1st', 1)
        _aE('2nd', 2)
        _aE('3rd', 3)
        _aE('4th', 4)
        _aE('5th', 5)
        _aE('6th', 6)
        _aE('1 1st', 1)
        _aE('1 2nd', 2)
        _aE('1 3rd', 3)
        _aE('1 4th', 4)
        _aE('1 5th', 5)
        _aE('1 6th', 6)
        _aE('1 1st 2', 1)
        _aE('1 2nd 2', 2)
        _aE('1 3rd 2', 3)
        _aE('1 4th 2', 4)
        _aE('1 5th 2', 5)
        _aE('1 6th 2', 6)
        _aE('Foo, Bar - Baz._5th', 5)
        _aE('Foo,Bar-_Baz_-_3ed_2002', 3)
        _aE('Foo,Bar-_Baz_-_4ed_2003', 4)
        _aE('Embedded_Systems_6th_.2011', 6)
        _aE('Networking_4th', 4)
        _aE('Foo 2E - Bar B. 2001', 2)
        _aE('Third Edition', 3)
        _aE('Bar 5e - Baz._', 5)
        _aE('Bar 5 e - Baz._', 5)
        _aE('Bar 5ed - Baz._', 5)
        _aE('Bar 5 ed - Baz._', 5)
        _aE('Bar 5th - Baz._', 5)
        _aE('Bar 5th ed - Baz._', 5)
        _aE('Bar 5th edition - Baz._', 5)
        _aE('Bar fifth e - Baz._', 5)
        _aE('Bar fifth ed - Baz._', 5)
        _aE('Bar fifth edition - Baz._', 5)
        _aE('Foobar 1st Edition.pdf', 1)
        _aE('Foobar 10th Edition.pdf', 10)
        _aE('Foobar 11th Edition.pdf', 11)
        _aE('Foobar 25th Edition.pdf', 25)
        _aE('Foobar 30th Edition.pdf', 30)
        _aE('Foobar 1st 10th Edition.pdf', 10)
        _aE('Foobar 10th 1st Edition.pdf', 10)
        _aE('Foobar 1st Edition 10th Edition.pdf', 10)
        _aE('Foobar 10th Edition 1st Edition.pdf', 10)
        _aE('Foobar Edition 1st 10th.pdf', 10)
        _aE('Foobar 1st Edition 10th.pdf', 10)
        _aE('Foobar 1st 10th Edition.pdf', 10)

    def test_returns_none_for_unavailable_editions(self):
        def _aN(test_input):
            actual = find_edition(test_input)
            self.assertIsNone(actual)

        _aN('Foo, Bar - Baz._')
        _aN('Foo, Bar 5 - Baz._')
        _aN('Foo, Bar 5s - Baz._')
        _aN('Foo 7 Entities')
        _aN('7 Entities')
        _aN('7')


class TestFindPublisherInCopyrightNotice(TestCase):
    def test_returns_expected_publisher(self):
        def _aE(test_input, expected):
            actual = find_publisher_in_copyright_notice(test_input)
            self.assertEqual(actual, expected)

        _aE('Copyright © Excellent Media P.C., 2017', 'Excellent Media P.C.')
        _aE('Copyright (c) Excellent Media P.C., 2017', 'Excellent Media P.C.')

        _aE('Copyright © 2017 Excellent Media P.C.', 'Excellent Media P.C.')
        _aE('Copyright (c) 2017 Excellent Media P.C.', 'Excellent Media P.C.')
        _aE('Copyright © 2016 Catckt', 'Catckt')
        _aE('Copyright (c) 2016 Catckt', 'Catckt')
        _aE('Copyright (C) 2016 Catckt', 'Catckt')
        _aE('Copyright(c)2016 Catckt', 'Catckt')
        _aE('Copyright(C)2016 Catckt', 'Catckt')
        _aE('Copyright © 2016 Catckt Publishing', 'Catckt Publishing')
        _aE('Copyright (c) 2016 Catckt Publishing', 'Catckt Publishing')
        _aE('Copyright (C) 2016 Catckt Publishing', 'Catckt Publishing')
        _aE('Copyright(c)2016 Catckt Publishing', 'Catckt Publishing')
        _aE('Copyright(C)2016 Catckt Publishing', 'Catckt Publishing')
        _aE('Copyright © 2011-2012 Bmf Btpveis', 'Bmf Btpveis')
        _aE('Copyright (C) 2011-2012 Bmf Btpveis', 'Bmf Btpveis')

        _aE('(C) Copyright 1985-2001 Gibson Corp.', 'Gibson Corp.')

        # Works:
        # 'Copyright (c) 2000 2015 Kibble'

        # NOGO:
        # 'Copyright (c) 2000  2015  Kibble '

        _aE('Copyright (c) 2000 2015 Kibble', 'Kibble')
        _aE('Copyright (c) 2000-2015  Kibble ', 'Kibble')
        _aE('Copyright (c) 2000, 2015  Kibble', 'Kibble')
        # _aE('Copyright (c) 2000, 2015, Kibble and/or its affiliates.', 'Kibble')

    def test_returns_none_for_unavailable_publishers(self):
        def _aN(test_input):
            actual = find_publisher_in_copyright_notice(test_input)
            self.assertIsNone(actual)

        _aN('Foo Bar')
        _aN('copyright reserved above, no part of this publication')
        _aN('permission of the copyright owner.')
        _aN('is common practice to put any licensing or copyright information in a comment at the')
        _aN('107 or 108 of the 1976 United States Copyright Act, without either the prior written permission of the Publisher, or')
        _aN('America. Except as permitted under the Copyright Act of 1976, no part of this publication may be')
