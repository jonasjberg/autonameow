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
from datetime import datetime
from unittest import TestCase

from analyzers.analyze_filename import (
    FilenameAnalyzer,
    FilenameTokenizer,
    SubstringFinder,
    _find_edition,
    likely_extension
)
from core.namebuilder import fields
import unit_utils as uu


def get_filename_analyzer(fileobject):
    return FilenameAnalyzer(fileobject,
                            add_results_callback=uu.mock_add_results_callback,
                            request_data_callback=uu.mock_request_data_callback)


class TestFilenameAnalyzerWithImageFile(TestCase):
    def setUp(self):
        self.fo = uu.get_named_fileobject('2010-01-31_161251.jpg')
        self.fna = get_filename_analyzer(self.fo)

    def test_setup(self):
        self.assertIsNotNone(self.fo)
        self.assertIsNotNone(self.fna)

    def test_get_datetime_does_not_return_none(self):
        dt_list = self.fna.get_datetime()
        self.assertIsNotNone(dt_list)

    def test_get_datetime_contains_special_case(self):
        dt_special, = filter(lambda dt: dt['source'] == 'very_special_case',
                             self.fna.get_datetime())
        self.assertIsNotNone(dt_special)

    def test_get_datetime_special_case_is_valid(self):
        dt_special, = filter(lambda dt: dt['source'] == 'very_special_case',
                             self.fna.get_datetime())

        expected = datetime.strptime('20100131 161251', '%Y%m%d %H%M%S')
        self.assertEqual(expected, dt_special.get('value'))


class TestFilenameAnalyzerWithEmptyFile(TestCase):
    def setUp(self):
        self.fo = uu.get_named_fileobject('gmail.pdf')
        self.fna = get_filename_analyzer(self.fo)

    def test_setup(self):
        self.assertIsNotNone(self.fo)
        self.assertIsNotNone(self.fna)

    def test_get_datetime_does_not_return_none(self):
        self.skipTest('TODO')
        self.assertIsNotNone(self.fna.get_datetime())

    def test_get_datetime_returns_empty_list(self):
        self.skipTest('TODO')
        self.assertEqual([], self.fna.get_datetime())


class TestLikelyExtension(TestCase):
    def setUp(self):
        Given = namedtuple('Given', 'suffix mime')
        Expect = namedtuple('Expect', 'expected')

        self.expect_testinput = [
            (Expect('txt'),
             Given(suffix='txt', mime='text/plain')),
            (Expect('sh'),
             Given(suffix='sh', mime='text/plain')),
            (Expect('sh'),
             Given(suffix='sh', mime='text/x-shellscript')),
            (Expect('sh'),
             Given(suffix='txt', mime='text/x-shellscript')),
            (Expect('pdf'),
             Given(suffix='pdf', mime='application/pdf')),
            (Expect('md'),
             Given(suffix='md', mime='text/plain')),
            (Expect('md'),
             Given(suffix='mkd', mime='text/plain')),
            (Expect('md'),
             Given(suffix='markdown', mime='text/plain')),
            (Expect('yaml'),
             Given(suffix='yaml', mime='text/plain')),
            (Expect('py'),
             Given(suffix='py', mime='text/x-shellscript')),
            (Expect('py'),
             Given(suffix='py', mime='text/x-python')),
            (Expect('py'),
             Given(suffix='', mime='text/x-python')),
        ]

    def test_returns_expected(self):
        for expect, input_args in self.expect_testinput:
            actual = likely_extension(*input_args)
            _m = 'Expected: "{!s}"  Actual: "{!s}”  ("{!s}”)'.format(
                expect.expected, actual, input_args
            )
            self.assertEqual(actual, expect.expected, _m)


class TestFindEdition(TestCase):
    def test_returns_expected_edition(self):
        self.skipTest('TODO')

        self.assertEqual(_find_edition('Foo, Bar - Baz._5th'), 5)
        self.assertEqual(_find_edition('Foo,Bar-_Baz_-_3ed_2002'), 3)
        self.assertEqual(_find_edition('Foo,Bar-_Baz_-_4ed_2003'), 4)
        self.assertEqual(_find_edition('Embedded_Systems_6th_.2011'), 6)
        self.assertEqual(_find_edition('Networking_4th'), 4)
        self.assertEqual(_find_edition('Foo 2E - Bar B. 2001'), 2)

    def test_returns_none_for_unavailable_editions(self):
        self.skipTest('TODO')

        self.assertIsNone(_find_edition('Foo, Bar - Baz._'))
        self.assertIsNone(_find_edition('Foo, Bar 5 - Baz._'))


class TestIdentifyFields(TestCase):
    def test__substrings(self):
        f = SubstringFinder()

        def _assert_splits(test_data, expected):
            actual = f._substrings(test_data)
            self.assertEqual(actual, expected)

        _assert_splits('a', ['a'])
        _assert_splits('a b', ['a', 'b'])
        _assert_splits('a b ', ['a', 'b'])
        _assert_splits(' a b ', ['a', 'b'])
        _assert_splits('a b a', ['a', 'b', 'a'])

    def test_identifies_fields(self):
        self.skipTest('TODO: ..')

        test_input = 'TheBeatles - PaperbackWriter.flac'

        f = SubstringFinder()
        # f.add_context('TheBeatles - ItsGettingBetter.flac')
        actual = f.identify_fields(test_input, [fields.Creator, fields.Title])

        self.assertTrue(isinstance(actual.get(fields.Creator), list))
        self.assertEqual(actual.get(fields.Creator)[0], 'TheBeatles')
        self.assertEqual(actual.get(fields.Creator)[1], 'PaperbackWriter')
        self.assertNotIn(actual.get(fields.Creator), '.flac')
        self.assertNotIn(actual.get(fields.Creator), 'flac')
        self.assertNotIn(actual.get(fields.Creator), '-')

        self.assertTrue(isinstance(actual.get(fields.Title), list))
        self.assertEqual(actual.get(fields.Title)[0], 'PaperbackWriter')
        self.assertEqual(actual.get(fields.Title)[1], 'TheBeatles')
        self.assertNotIn(actual.get(fields.Title), '.flac')
        self.assertNotIn(actual.get(fields.Title), 'flac')
        self.assertNotIn(actual.get(fields.Title), '-')

    def test_uses_constraints(self):
        pass
        # add_constraint(fields.Author, matches=r'[\w]+')
        # add_constraint(fields.Title, matches=r'[\w]+')
        # result = identify_fields(string, [fields.Creator, fields.Title])

        # assert result[fields.Author] == ['The Beatles', 'Paperback Writer',
        #                                   'flac']
        # assert result[fields.Title] == ['Paperback Writer', 'The Beatles',
        #                                 'flac']


class TestFilenameTokenizer(TestCase):
    def _t(self, filename, expected):
        self.tokenizer = FilenameTokenizer(filename)
        actual = self.tokenizer.separators
        self.assertEqual(actual, expected)

    def test_find_separators_all_periods(self):
        self._t(
            filename='foo.bar.1234.baz',
            expected=[('.', 3)]
        )

    def test_find_separators_periods_and_brackets(self):
        self._t(
            filename='foo.bar.[1234].baz',
            expected=[('.', 3), ('[', 1), (']', 1)]
        )

    def test_find_separators_underlines(self):
        self._t(
            filename='foo_bar_1234_baz',
            expected=[('_', 3)]
        )

    def test_find_separators_dashes(self):
        self._t(
            filename='foo-bar-1234-baz',
            expected=[('-', 3)]
        )

    def test_find_separators_underlines_and_dashes(self):
        self._t(
            filename='foo-bar_1234_baz',
            expected=[('_', 2), ('-', 1)]
        )
