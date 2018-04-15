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

from util.text.patternmatching import (
    compiled_ordinal_edition_regexes,
    compiled_ordinal_regexes,
    find_and_extract_edition,
    find_publisher_in_copyright_notice
)


class TestCompiledOrdinalRegexes(TestCase):
    @classmethod
    def setUpClass(cls):
        from util import coercers
        cls.builtin_regex_type = coercers.BUILTIN_REGEX_TYPE
        cls.actual = compiled_ordinal_regexes()

    def test_returns_expected_type(self):
        self.assertIsNotNone(self.actual)
        self.assertIsInstance(self.actual, dict)

    def test_returns_compiled_regular_expressions(self):
        ordinal_one_regex = self.actual.get(1)
        self.assertIsInstance(ordinal_one_regex, self.builtin_regex_type)

        for ordinal_regex in self.actual.values():
            self.assertIsInstance(ordinal_regex, self.builtin_regex_type)

    def test_returned_regexes_matches_strings(self):
        for given in [
            '2nd', 'second', 'SECOND', 'foo 2nd bar', 'foo 2ND bar',
            '2nd ed', 'second ed', 'SECOND ED', 'foo 2nd ed bar', 'foo 2ND ED bar',
            '2nd ed.', 'second ed.', 'SECOND ED.', 'foo 2nd ed. bar', 'foo 2ND ED. bar',
            '2nd edition', 'second edition', 'SECOND EDITION', 'foo 2nd edition bar', 'foo 2ND EDITION bar',
          ]:
            with self.subTest(given=given):
                actual = self.actual.get(2).search(given)
                self.assertIsNotNone(actual)
                match = actual.group(0)
                self.assertTrue(2, match)


class TestCompiledOrdinalEditionRegexes(TestCase):
    @classmethod
    def setUpClass(cls):
        from util import coercers
        cls.builtin_regex_type = coercers.BUILTIN_REGEX_TYPE
        cls.actual = compiled_ordinal_edition_regexes()

    def test_returns_expected_type(self):
        self.assertIsNotNone(self.actual)
        self.assertIsInstance(self.actual, dict)

    def test_returns_compiled_regular_expressions(self):
        ordinal_one_regex = self.actual.get(1)
        self.assertIsInstance(ordinal_one_regex, self.builtin_regex_type)

        for ordinal_regex in self.actual.values():
            self.assertIsInstance(ordinal_regex, self.builtin_regex_type)

    def test_returned_regexes_matches_strings(self):
        for given in [
            '2nd ed', 'second ed', 'SECOND ED', 'foo 2nd ed bar', 'foo 2ND ED bar',
            '2nd ed.', 'second ed.', 'SECOND ED.', 'foo 2nd ed. bar', 'foo 2ND ED. bar',
            '2nd edition', 'second edition', 'SECOND EDITION', 'foo 2nd edition bar', 'foo 2ND EDITION bar',
          ]:
            with self.subTest(given=given):
                actual = self.actual.get(2).search(given)
                self.assertIsNotNone(actual)
                match = actual.group(0)
                self.assertTrue(2, match)


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
            self.assertEqual(given, actual_text)

    def test_raises_assertion_error_given_non_str_type(self):
        with self.assertRaises(AssertionError):
            _, _ = find_and_extract_edition(b'foo')

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
        self._check_result(given='Bar 5 ed. - Baz._', expect_edition=5, expect_text='Bar  - Baz._')
        self._check_result(given='Bar 5th ed - Baz._', expect_edition=5, expect_text='Bar  - Baz._')
        self._check_result(given='Bar 5th ed. - Baz._', expect_edition=5, expect_text='Bar  - Baz._')

    def test_finds_edition_and_returns_modified_text_given_sample_text_with_longer_matches_first(self):
        self._check_result(given='Bar 4th ed - Baz._', expect_edition=4, expect_text='Bar  - Baz._')
        self._check_result(given='Bar 5th edition - Baz._', expect_edition=5, expect_text='Bar  - Baz._')
        self._check_result(given='Bar fifth e - Baz._', expect_edition=5, expect_text='Bar  - Baz._')
        self._check_result(given='Bar fifth ed - Baz._', expect_edition=5, expect_text='Bar  - Baz._')
        self._check_result(given='Bar fifth ed. - Baz._', expect_edition=5, expect_text='Bar  - Baz._')
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

    def test_uses_biggest_matching_number_in_case_of_multiple_matches(self):
        self._check_result(given='Foobar 1st 10th Edition.pdf', expect_edition=10, expect_text='Foobar 1st .pdf')
        self._check_result(given='Foobar 1st Edition 10th Edition.pdf', expect_edition=10, expect_text='Foobar 1st Edition .pdf')
        self._check_result(given='Foobar 2nd Edition 10th Edition.pdf', expect_edition=10, expect_text='Foobar 2nd Edition .pdf')
        self._check_result(given='Foobar 10th Edition 1st Edition.pdf', expect_edition=10, expect_text='Foobar  1st Edition.pdf')
        self._check_result(given='Foobar Edition 1st 10th.pdf', expect_edition=10, expect_text='Foobar Edition 1st .pdf')
        self._check_result(given='Foobar Edition 2nd 10th.pdf', expect_edition=10, expect_text='Foobar Edition 2nd .pdf')
        self._check_result(given='Foobar 1st 10th Edition.pdf', expect_edition=10, expect_text='Foobar 1st .pdf')

    def test_does_not_use_biggest_matching_number_if_edition_is_obvious(self):
        self._check_result(given='11th Hour CISSP: Study Guide 2nd Edition', expect_edition=2, expect_text='11th Hour CISSP: Study Guide ')
        self._check_result(given='Foobar 1st Edition 10th.pdf', expect_edition=1, expect_text='Foobar  10th.pdf')
        self._check_result(given='Foobar 10th 1st Edition.pdf', expect_edition=1, expect_text='Foobar 10th .pdf')

    def test_strings_without_editions_that_has_caused_false_positives(self):
        for given in [
            'Microsoft Exchange 2010 PowerShell Cookbook: Manage and maintain your Microsoft Exchange 2010 environment with Windows PowerShell 2.0 and the Exchange Management Shell',
            # TODO: Fix false positives;
            # 'Eleventh Hour CISSP',
            # 'Head First C#'
        ]:
            self._check_result(given=given, expect_edition=None, expect_text=given)


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
