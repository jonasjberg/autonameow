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
    likely_extension
)
from core.namebuilder import fields
import unit_utils as uu


uu.init_session_repository()
uu.init_provider_registry()


def get_filename_analyzer(fileobject):
    return FilenameAnalyzer(
        fileobject,
        uu.get_default_config(),
        request_data_callback=uu.mock_request_data_callback
    )


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
        self.skipTest('TODO: Clean up old code ..')
        dt_special, = filter(lambda dt: dt['source'] == 'very_special_case',
                             self.fna.get_datetime())
        self.assertIsNotNone(dt_special)

    def test_get_datetime_special_case_is_valid(self):
        self.skipTest('TODO: Clean up old code ..')
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
            (Expect('txt'), Given(suffix='txt', mime='text/plain')),
            (Expect('sh'), Given(suffix='sh', mime='text/plain')),
            (Expect('sh'), Given(suffix='sh', mime='text/x-shellscript')),
            (Expect('sh'), Given(suffix='txt', mime='text/x-shellscript')),
            (Expect('pdf'), Given(suffix='pdf', mime='application/pdf')),
            (Expect('md'), Given(suffix='md', mime='text/plain')),
            (Expect('md'), Given(suffix='mkd', mime='text/plain')),
            (Expect('md'), Given(suffix='markdown', mime='text/plain')),
            (Expect('yaml'), Given(suffix='yaml', mime='text/plain')),
            (Expect('py'), Given(suffix='py', mime='text/x-shellscript')),
            (Expect('py'), Given(suffix='py', mime='text/x-python')),
            (Expect('py'), Given(suffix='', mime='text/x-python')),
            (Expect('chm'), Given(suffix='chm',
                                  mime='application/octet-stream')),
            (Expect('mobi'), Given(suffix='mobi',
                                   mime='application/octet-stream')),
            (Expect('azw3'), Given(suffix='azw3',
                                   mime='application/octet-stream')),
            (Expect('pdf'), Given(suffix='pdf',
                                  mime='application/octet-stream')),
        ]

    def test_returns_expected(self):
        for expect, input_args in self.expect_testinput:
            actual = likely_extension(*input_args)
            _m = 'Expected: "{!s}"  Actual: "{!s}”  ("{!s}”)'.format(
                expect.expected, actual, input_args
            )
            self.assertEqual(actual, expect.expected, _m)


class TestFileNameAnalyzerWithEbook(TestCase):
    def _mock_request_data(self, fileobject, meowuri):
        from core import types
        from core.model import ExtractedData

        if fileobject.filename == b'Charles+Darwin+-+On+the+Origin+of+Species%2C+6th+Edition.mobi':
            if meowuri == 'extractor.filesystem.xplat.basename.prefix':
                return ExtractedData(
                    coercer=types.AW_PATHCOMPONENT
                )(b'Charles+Darwin+-+On+the+Origin+of+Species%2C+6th+Edition')

    def setUp(self):
        fo = uu.fileobject_testfile(
            'Charles+Darwin+-+On+the+Origin+of+Species%2C+6th+Edition.mobi'
        )
        self.a = FilenameAnalyzer(
            fo,
            config=uu.get_default_config(),
            request_data_callback=self._mock_request_data
        )

        # TODO: This breaks due to FileObject equality check in '__hash__'
        #       includes the absolute path, which is different across platforms.
        # TODO: Pickled repository state does not work well!

        # uu.load_repository_dump(
        #     uu.abspath_testfile('repository_Darwin-mobi.state')
        # )

    def test_get_edition(self):
        actual = self.a.get_edition()
        actual = actual.value
        expected = 6
        self.assertEqual(actual, expected)

    def test_get_datetime(self):
        actual = self.a.get_datetime()
        expected = None
        self.assertEqual(actual, expected)

    def test_get_title(self):
        self.skipTest('TODO: Implement finding titles in file names ..')

        actual = self.a.get_title().value
        expected = 'On the Origin of Species'
        self.assertEqual(actual, expected)


class TestIdentifyFields(TestCase):
    def test__substrings(self):
        f = SubstringFinder()

        def _assert_splits(test_data, expected):
            actual = f.substrings(test_data)
            self.assertEqual(actual, expected)

        _assert_splits('a', ['a'])
        _assert_splits('a b', ['a', 'b'])
        _assert_splits('a b ', ['a', 'b'])
        _assert_splits(' a b ', ['a', 'b'])
        _assert_splits('a b a', ['a', 'b', 'a'])

        _assert_splits('a-b', ['a', 'b'])
        _assert_splits('a-b c', ['a-b', 'c'])
        _assert_splits('a b-c', ['a', 'b-c'])
        _assert_splits(' a-b ', ['a-b'])
        _assert_splits('a_b_a', ['a', 'b', 'a'])

        _assert_splits('TheBeatles - PaperbackWriter',
                       ['TheBeatles', '-', 'PaperbackWriter'])
        _assert_splits('TheBeatles PaperbackWriter',
                       ['TheBeatles', 'PaperbackWriter'])

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


class TestFilenameTokenizerSeparators(TestCase):
    def _t(self, filename, separators, main_separator):
        tokenizer = FilenameTokenizer(filename)
        self.assertEqual(tokenizer.separators, separators)
        self.assertEqual(tokenizer.main_separator, main_separator)
        tokenizer = None

    def test_find_separators_all_periods(self):
        self._t(
            filename='foo.bar.1234.baz',
            separators=[('.', 3)],
            main_separator='.'
        )

    def test_find_separators_periods_and_brackets(self):
        self._t(
            filename='foo.bar.[1234].baz',
            separators=[('.', 3), ('[', 1), (']', 1)],
            main_separator='.'
        )

    def test_find_separators_underlines(self):
        self._t(
            filename='foo_bar_1234_baz',
            separators=[('_', 3)],
            main_separator='_'
        )

    def test_find_separators_dashes(self):
        self._t(
            filename='foo-bar-1234-baz',
            separators=[('-', 3)],
            main_separator='-'
        )

    def test_find_separators_spaces(self):
        self._t(
            filename='foo bar 1234 baz',
            separators=[(' ', 3)],
            main_separator=' '
        )

    def test_find_separators_underlines_and_dashes(self):
        self._t(
            filename='foo-bar_1234_baz',
            separators=[('_', 2), ('-', 1)],
            main_separator='_'
        )

    def test_find_separators_darwin(self):
        self.skipTest('TODO: Fix inconsistent test results!')
        self._t(
            filename='Charles+Darwin+-+On+the+Origin+of+Species%2C+6th+Edition.mobi',
            separators=[(' ', 9), ('-', 1), ('%', 1)],
            main_separator=' '
        )

    def test_find_separators_html_encoded(self):
        self._t(
            filename='A%20Quick%20Introduction%20to%20IFF.txt',
            separators=[(' ', 4), ('.', 1)],
            main_separator=' '
        )

    def test_find_separators_underlines_dashes(self):
        self.skipTest('TODO: Fix inconsistent test results!')
        self._t(
            filename='a-b c_d',
            separators=[(' ', 1), ('-', 1), ('_', 1)],
            main_separator=' '
        )

    def test_find_main_separator(self):
        def _aE(filename, main_separator):
            tokenizer = FilenameTokenizer(filename)
            self.assertEqual(tokenizer.main_separator, main_separator)
            tokenizer = None

        _aE('a b', ' ')
        _aE('a-b-c_d', '-')
        _aE('a-b', '-')
        _aE('a_b', '_')
        _aE('a--b', '-')
        _aE('a__b', '_')

        _aE('a b', ' ')
        _aE('shell-scripts.github', '-')
        _aE('Unison-OS-X-2.48.15.zip', '-')

        # TODO: Are we looking for field- or word-separators..? (!?)
        _aE('2012-02-18-14-18_Untitled-meeting.log', '-')

    def test_resolve_tied_counts(self):
        self.skipTest('TODO: Fix inconsistent test results!')
        assume_preferred_separator = '_'

        def _aE(filename, main_separator):
            tokenizer = FilenameTokenizer(filename)
            self.assertEqual(tokenizer.main_separator, main_separator)
            tokenizer = None

        _aE('a-b c', ' ')
        _aE('a_b c', ' ')
        _aE('-a b', ' ')
        _aE('_a b', ' ')
        _aE('a-b c_d', ' ')
        _aE('a_b c-d', ' ')
        _aE('-a b_d', ' ')
        _aE('_a b-d', ' ')

        _aE('a-b_c', assume_preferred_separator)
        _aE('a_b-c', assume_preferred_separator)
        _aE('a_-b', assume_preferred_separator)
        _aE('a-_b', assume_preferred_separator)
        _aE('a-b_c-d_e', assume_preferred_separator)
        _aE('a_b-c_d-e', assume_preferred_separator)
        _aE('a_-b-_c', assume_preferred_separator)
        _aE('a-_b_-c', assume_preferred_separator)

        _aE('a-_b', assume_preferred_separator)
        _aE('a_-b', assume_preferred_separator)

    def test_get_seps_with_tied_counts(self):
        def _aE(test_input, expect):
            actual = FilenameTokenizer.get_seps_with_tied_counts(test_input)
            self.assertEqual(actual, expect)

        _aE([('a', 2), ('b', 1)],
            expect=[])
        _aE([('a', 2), ('b', 2)],
            expect=['a', 'b'])
        _aE([('a', 2), ('b', 1), ('c', 1)],
            expect=['b', 'c'])
        _aE([('a', 2), ('b', 1), ('c', 1), ('d', 2)],
            expect=['a', 'b', 'c', 'd'])
        _aE([('a', 2), ('b', 1), ('c', 1), ('d', 1)],
            expect=['b', 'c', 'd'])


class TestFilenameTokenizerTokens(TestCase):
    def _t(self, filename, tokens):
        tokenizer = FilenameTokenizer(filename)
        self.assertEqual(tokenizer.tokens, tokens)

    def test_only_spaces(self):
        self._t(filename='foo bar 1234 baz',
                tokens=['foo', 'bar', '1234', 'baz'])

    def test_html_encoded(self):
        self._t(filename='A%20Quick%20Introduction%20to%20IFF.txt',
                tokens=['A', 'Quick', 'Introduction', 'to', 'IFF.txt'])
