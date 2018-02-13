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
from unittest.mock import (
    Mock,
    patch
)

import unit.utils as uu
from analyzers.analyze_filename import (
    FilenameAnalyzer,
    FilenameTokenizer,
    likely_extension,
    SubstringFinder
)
from core.namebuilder import fields
from core.types import NullMIMEType


uu.init_session_repository()


class TestFieldGetterMethods(TestCase):
    def setUp(self):
        mock_config = Mock()
        mock_config.get.return_value = {
            'candidates': {
                'ProjectGutenberg': [
                    # NOTE: None is only ok if 'find_publisher()' is mocked!
                    None
                    # re.compile('Project Gutenberg', re.IGNORECASE)
                ]
            }
        }

        self.fna = FilenameAnalyzer(None, mock_config, None)

    def test__get_edition_returns_expected_given_basename_with_edition(self):
        self.fna._basename_prefix = 'foo 2nd Edition bar'
        actual = self.fna._get_edition()
        self.assertEqual(2, actual)

    def test__get_edition_returns_expected_given_basename_without_edition(self):
        self.fna._basename_prefix = 'foo'
        actual = self.fna._get_edition()
        self.assertIsNone(actual)

    @patch('analyzers.analyze_filename.find_publisher')
    def test__get_publisher_returns_expected_given_basename_with_publisher(
            self, mock_find_publisher
    ):
        mock_find_publisher.return_value = 'Foo Pub'
        self.fna._basename_prefix = 'x'
        actual = self.fna._get_publisher()
        self.assertEqual('Foo Pub', actual)

    @patch('analyzers.analyze_filename.find_publisher')
    def test__get_publisher_returns_expected_given_basename_without_publisher(
            self, mock_find_publisher
    ):
        mock_find_publisher.return_value = None
        self.fna._basename_prefix = 'x'
        actual = self.fna._get_publisher()
        self.assertIsNone(actual)

    def __assert_extension(self, expected):
        actual = self.fna._get_extension()
        self.assertEqual(expected, actual)

    def test__get_extension_returns_expected_given_mime_type_and_suffix(self):
        self.fna._file_mimetype = 'image/jpeg'
        self.fna._basename_suffix = 'jpg'
        self.__assert_extension('jpg')

    def test__get_extension_returns_expected_given_mime_type_empty_suffix(self):
        self.fna._file_mimetype = 'image/jpeg'
        self.fna._basename_suffix = ''
        self.__assert_extension('jpg')

    def test__get_extension_returns_expected_given_mime_type_none_suffix(self):
        self.fna._file_mimetype = 'image/jpeg'
        self.fna._basename_suffix = None
        self.__assert_extension('jpg')

    def test__get_extension_returns_expected_given_suffix_null_mime_type(self):
        self.fna._file_mimetype = NullMIMEType()
        self.fna._basename_suffix = 'jpg'
        self.__assert_extension('jpg')

    def test__get_extension_returns_expected_given_empty_suffix_null_mime(self):
        self.fna._file_mimetype = NullMIMEType()
        self.fna._basename_suffix = ''
        self.__assert_extension('')

    def test__get_extension_returns_none_given_none_suffix_null_mime(self):
        self.fna._file_mimetype = NullMIMEType()
        self.fna._basename_suffix = None
        self.__assert_extension(None)


class TestLikelyExtension(TestCase):
    @classmethod
    def setUpClass(cls):
        Given = namedtuple('Given', 'suffix mime')
        Expect = namedtuple('Expect', 'expected')

        cls.expect_testinput = [
            (Expect(''),
             Given(suffix='', mime='application/octet-stream')),
            (Expect('7z'),
             Given(suffix='7z', mime='application/x-7z-compressed')),
            (Expect('alfredworkflow'),
             Given(suffix='alfredworkflow', mime='application/zip')),
            (Expect('azw3'),
             Given(suffix='azw3', mime='application/octet-stream')),
            (Expect('bibtex'),
             Given(suffix='bibtex', mime='text/plain')),
            (Expect('bin'),
             Given(suffix='bin', mime='application/octet-stream')),
            (Expect('bz2'),
             Given(suffix='bz2', mime='application/x-bzip2')),
            (Expect('chm'),
             Given(suffix='chm', mime='application/octet-stream')),

            (Expect('c'),
             Given(suffix='c', mime='text/x-c')),
            (Expect('c'),
             Given(suffix='txt', mime='text/x-c')),
            (Expect('c'),
             Given(suffix='c', mime='text/plain')),
            (Expect('cpp'),
             Given(suffix='cpp', mime='text/x-c++')),
            (Expect('cpp'),
             Given(suffix='cpp', mime='text/plain')),
            (Expect('cpp'),
             Given(suffix='c++', mime='text/x-c++')),
            (Expect('cpp'),
             Given(suffix='c++', mime='text/plain')),

            (Expect('doc'),
             Given(suffix='doc', mime='application/msword')),
            (Expect('eps'),
             Given(suffix='eps', mime='application/postscript')),
            (Expect('hex'),
             Given(suffix='hex', mime='application/octet-stream')),

            (Expect('html'),
             Given(suffix='htm.gz', mime='text/html')),
            (Expect('html'),
             Given(suffix='html.gz', mime='text/html')),
            (Expect('html.gz'),
             Given(suffix='htm.gz', mime='application/x-gzip')),
            (Expect('html.gz'),
             Given(suffix='html.gz', mime='application/x-gzip')),
            (Expect('html.gz'),
             Given(suffix='htm', mime='application/x-gzip')),
            (Expect('html.gz'),
             Given(suffix='html', mime='application/x-gzip')),

            (Expect('log'),
             Given(suffix='log', mime='text/x-tex')),
            (Expect('log'),
             Given(suffix='log', mime='text/plain')),

            (Expect('mid'),
             Given(suffix='mid', mime='audio/midi')),
            (Expect('md'),
             Given(suffix='md', mime='text/plain')),
            (Expect('md'),
             Given(suffix='mkd', mime='text/plain')),
            (Expect('md'),
             Given(suffix='markdown', mime='text/plain')),
            (Expect('mobi'),
             Given(suffix='mobi', mime='application/octet-stream')),
            (Expect('pdf'),
             Given(suffix='pdf', mime='application/pdf')),
            (Expect('pdf'),
             Given(suffix='pdf', mime='application/octet-stream')),
            (Expect('ps'),
             Given(suffix='ps', mime='application/postscript')),
            (Expect('py'),
             Given(suffix='py', mime='text/x-shellscript')),
            (Expect('py'),
             Given(suffix='py', mime='text/x-python')),
            (Expect('py'),
             Given(suffix='', mime='text/x-python')),
            (Expect('scpt'),
             Given(suffix='scpt', mime='application/octet-stream')),
            (Expect('sh'),
             Given(suffix='sh', mime='text/plain')),
            (Expect('sh'),
             Given(suffix='sh', mime='text/x-shellscript')),
            (Expect('sh'),
             Given(suffix='txt', mime='text/x-shellscript')),
            (Expect('sh'),
             Given(suffix='sh', mime='text/x-env')),

            # Visual Studio Solution
            (Expect('sln'),
             Given(suffix='sln', mime='application/octet-stream')),

            (Expect('tar.bz2'),
             Given(suffix='tar.bz2', mime='application/x-bzip2')),
            (Expect('tar.gz'),
             Given(suffix='tgz', mime='application/x-gzip')),
            (Expect('tar.gz'),
             Given(suffix='tar.gz', mime='application/x-gzip')),
            (Expect('tar.gz.sig'),
             Given(suffix='tar.gz.sig', mime='application/octet-stream')),

            (Expect('tex'),
             Given(suffix='tex', mime='text/x-tex')),
            (Expect('tex'),
             Given(suffix='tex', mime='application/x-tex')),

            (Expect('txt'),
             Given(suffix='txt', mime='text/plain')),
            (Expect('txt'),
             Given(suffix='txt.gz', mime='text/plain')),
            (Expect('txt'),
             Given(suffix='txt', mime='application/octet-stream')),

            (Expect('txt.gz'),
             Given(suffix='txt.gz', mime='application/x-gzip')),
            (Expect('txt.gz'),
             Given(suffix='txt', mime='application/x-gzip')),
            (Expect('txt.tar.gz'),
             Given(suffix='txt.tar.gz', mime='application/x-gzip')),
            (Expect('txt.tar.gz'),
             Given(suffix='txt.tgz', mime='application/x-gzip')),

            (Expect('w'),
             Given(suffix='w', mime='text/x-c')),
            (Expect('workspace'),
             Given(suffix='workspace', mime='text/xml')),
            (Expect('yaml'),
             Given(suffix='yaml', mime='text/plain')),

            (Expect('zip'),
             Given(suffix='zip', mime='application/zip')),
            (Expect('zip'),
             Given(suffix='zip', mime='application/x-zip')),

            # Chrome Save as "Webpage, Single File"
            (Expect('mhtml'),
             Given(suffix='mhtml', mime='message/rfc822')),
        ]

    def test_returns_expected(self):
        for expect, input_args in self.expect_testinput:
            actual = likely_extension(*input_args)
            _m = 'Expected: "{!s}"  Actual: "{!s}”  ("{!s}”)'.format(
                expect.expected, actual, input_args
            )
            self.assertEqual(expect.expected, actual, _m)


class TestIdentifyFields(TestCase):
    def test__substrings(self):
        f = SubstringFinder()

        def _assert_splits(test_data, expected):
            actual = f.substrings(test_data)
            self.assertEqual(expected, actual)

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

        self.assertIsInstance(actual.get(fields.Creator), list)
        self.assertEqual('TheBeatles', actual.get(fields.Creator)[0])
        self.assertEqual('PaperbackWriter', actual.get(fields.Creator)[1])
        self.assertNotIn('.flac', actual.get(fields.Creator))
        self.assertNotIn('flac', actual.get(fields.Creator))
        self.assertNotIn('-', actual.get(fields.Creator))

        self.assertIsInstance(actual.get(fields.Title), list)
        self.assertEqual('PaperbackWriter', actual.get(fields.Title)[0])
        self.assertEqual('TheBeatles', actual.get(fields.Title)[1])
        self.assertNotIn('.flac', actual.get(fields.Title))
        self.assertNotIn('flac', actual.get(fields.Title))
        self.assertNotIn('-', actual.get(fields.Title))

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
        self.assertEqual(separators, tokenizer.separators)
        self.assertEqual(main_separator, tokenizer.main_separator)
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
            self.assertEqual(main_separator, tokenizer.main_separator)
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
            self.assertEqual(main_separator, tokenizer.main_separator)
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
            self.assertEqual(expect, actual)

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
        self.assertEqual(tokens, tokenizer.tokens)

    def test_only_spaces(self):
        self._t(filename='foo bar 1234 baz',
                tokens=['foo', 'bar', '1234', 'baz'])

    def test_html_encoded(self):
        self._t(filename='A%20Quick%20Introduction%20to%20IFF.txt',
                tokens=['A', 'Quick', 'Introduction', 'to', 'IFF.txt'])
