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
    find_and_extract_edition,
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


class TestFindAndExtractEdition(TestCase):
    def test_returns_expected_given_text_without_editions(self):
        for given in [
            None,
            '',
            ' ',
            'foo',
            'foo bar'
        ]:
            actual_edition, actual_text = find_and_extract_edition(given)
            self.assertIsNone(actual_edition)
            self.assertIsNone(actual_text)

    def _check_result(self, given, expect_edition, expect_text):
        actual_edition, actual_text = find_and_extract_edition(given)
        self.assertEqual(expect_edition, actual_edition)
        self.assertEqual(expect_text, actual_text)

    def test_finds_edition_and_returns_empty_string_when_string_is_only_edition(self):
        self._check_result(given='1st', expect_edition=1, expect_text='')
        self._check_result(given='2nd', expect_edition=2, expect_text='')
        self._check_result(given='3rd', expect_edition=3, expect_text='')
        self._check_result(given='4th', expect_edition=4, expect_text='')
        self._check_result(given='5th', expect_edition=5, expect_text='')
        self._check_result(given='6th', expect_edition=6, expect_text='')
        self._check_result(given='7th', expect_edition=7, expect_text='')
        self._check_result(given='8th', expect_edition=8, expect_text='')
        self._check_result(given='9th', expect_edition=9, expect_text='')
        self._check_result(given='10th', expect_edition=10, expect_text='')

    def test_finds_edition_and_returns_remaining_string_with_single_digit(self):
        self._check_result(given='1 1st', expect_edition=1, expect_text='1 ')
        self._check_result(given='1 2nd', expect_edition=2, expect_text='1 ')
        self._check_result(given='1 3rd', expect_edition=3, expect_text='1 ')
        self._check_result(given='1 4th', expect_edition=4, expect_text='1 ')
        self._check_result(given='1 5th', expect_edition=5, expect_text='1 ')
        self._check_result(given='1 6th', expect_edition=6, expect_text='1 ')
        self._check_result(given='1 7th', expect_edition=7, expect_text='1 ')
        self._check_result(given='1 8th', expect_edition=8, expect_text='1 ')
        self._check_result(given='1 9th', expect_edition=9, expect_text='1 ')
        self._check_result(given='1 10th', expect_edition=10, expect_text='1 ')

    def test_finds_edition_and_returns_remaining_surrounding_strings(self):
        self._check_result(given='foo 1st bar', expect_edition=1, expect_text='foo  bar')
        self._check_result(given='foo 2nd bar', expect_edition=2, expect_text='foo  bar')
        self._check_result(given='foo 3rd bar', expect_edition=3, expect_text='foo  bar')
        self._check_result(given='foo 4th bar', expect_edition=4, expect_text='foo  bar')
        self._check_result(given='foo 5th bar', expect_edition=5, expect_text='foo  bar')
        self._check_result(given='foo 6th bar', expect_edition=6, expect_text='foo  bar')
        self._check_result(given='foo 7th bar', expect_edition=7, expect_text='foo  bar')
        self._check_result(given='foo 8th bar', expect_edition=8, expect_text='foo  bar')
        self._check_result(given='foo 9th bar', expect_edition=9, expect_text='foo  bar')
        self._check_result(given='foo 10th bar', expect_edition=10, expect_text='foo  bar')
        self._check_result(given='Foobar 1st Edition pdf', expect_edition=1, expect_text='Foobar  pdf')
        self._check_result(given='Foobar 10th Edition pdf', expect_edition=10, expect_text='Foobar  pdf')
        self._check_result(given='Foobar 11th Edition pdf', expect_edition=11, expect_text='Foobar  pdf')
        self._check_result(given='Foobar 25th Edition pdf', expect_edition=25, expect_text='Foobar  pdf')
        self._check_result(given='Foobar 30th Edition pdf', expect_edition=30, expect_text='Foobar  pdf')

    def test_finds_edition_and_returns_modified_text(self):
        self._check_result(given='Foo, Bar - Baz._5th', expect_edition=5, expect_text='Foo, Bar - Baz._')
        self._check_result(given='Foo,Bar-_Baz_-_3ed_2002', expect_edition=3, expect_text='Foo,Bar-_Baz_-__2002')
        self._check_result(given='Foo,Bar-_Baz_-_3ed 2002', expect_edition=3, expect_text='Foo,Bar-_Baz_-_ 2002')
        self._check_result(given='Foo,Bar-_Baz_-_4ed_2003', expect_edition=4, expect_text='Foo,Bar-_Baz_-__2003')
        self._check_result(given='Blah Framework Second Edition', expect_edition=2, expect_text='Blah Framework ')

    def test_finds_edition_and_returns_modified_text_given_sample_text(self):
        self._check_result(given='Embedded_Systems_6th_.2011', expect_edition=6, expect_text='Embedded_Systems__.2011')
        self._check_result(given='Networking_4th', expect_edition=4, expect_text='Networking_')
        self._check_result(given='Bar 5e - Baz._', expect_edition=5, expect_text='Bar  - Baz._')
        self._check_result(given='Bar 5th - Baz._', expect_edition=5, expect_text='Bar  - Baz._')
        self._check_result(given='Bar 5ed - Baz._', expect_edition=5, expect_text='Bar  - Baz._')
        self._check_result(given='Bar 5 ed - Baz._', expect_edition=5, expect_text='Bar  - Baz._')
        self._check_result(given='Bar 5th - Baz._', expect_edition=5, expect_text='Bar  - Baz._')

        # TODO: Sort matches by length.
        # self._check_result(given='Bar 4th ed - Baz._', expect_edition=4, expect_text='Bar  - Baz._')
        # self._check_result(given='Bar 5th edition - Baz._', expect_edition=5, expect_text='Bar  - Baz._')
        # self._check_result(given='Bar fifth e - Baz._', expect_edition=5, expect_text='Bar  - Baz._')
        # self._check_result(given='Bar fifth ed - Baz._', expect_edition=5, expect_text='Bar  - Baz._')

        self._check_result(given='Bar fifth edition - Baz._', expect_edition=5, expect_text='Bar  - Baz._')

    def test_finds_edition_and_returns_modified_text_with_only_literal_edition(self):
        self._check_result(given='1st Edition', expect_edition=1, expect_text='')
        self._check_result(given='First Edition', expect_edition=1, expect_text='')
        self._check_result(given='2nd Edition', expect_edition=2, expect_text='')
        self._check_result(given='Second Edition', expect_edition=2, expect_text='')
        self._check_result(given='3rd Edition', expect_edition=3, expect_text='')
        self._check_result(given='Third Edition', expect_edition=3, expect_text='')
        self._check_result(given='4th Edition', expect_edition=4, expect_text='')
        self._check_result(given='Fourth Edition', expect_edition=4, expect_text='')
        self._check_result(given='5th Edition', expect_edition=5, expect_text='')
        self._check_result(given='Fifth Edition', expect_edition=5, expect_text='')
        self._check_result(given='6th Edition', expect_edition=6, expect_text='')
        self._check_result(given='Sixth Edition', expect_edition=6, expect_text='')
        self._check_result(given='7th Edition', expect_edition=7, expect_text='')
        self._check_result(given='Seventh Edition', expect_edition=7, expect_text='')
        self._check_result(given='8th Edition', expect_edition=8, expect_text='')
        self._check_result(given='Eighth Edition', expect_edition=8, expect_text='')

    def test_use_biggest_matching_number(self):
        self._check_result(given='Foobar 1st 10th Edition.pdf', expect_edition=10, expect_text='Foobar 1st .pdf')

        # TODO: Remove extra removing of any trailing '[eE]dition' ..
        # self._check_result(given='Foobar 10th 1st Edition.pdf', expect_edition=10, expect_text='Foobar  1st Edition.pdf')
        # self._check_result(given='Foobar 1st Edition 10th Edition.pdf', expect_edition=10, expect_text='Foobar 1st Edition.pdf')
        # self._check_result(given='Foobar 10th Edition 1st Edition.pdf', expect_edition=10, expect_text='Foobar 1st Edition.pdf')
        # self._check_result(given='Foobar Edition 1st 10th.pdf', expect_edition=10, expect_text='Foobar Edition 1st.pdf')

        self._check_result(given='Foobar 1st Edition 10th.pdf', expect_edition=10, expect_text='Foobar 1st .pdf')
        self._check_result(given='Foobar 1st 10th Edition.pdf', expect_edition=10, expect_text='Foobar 1st .pdf')


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
