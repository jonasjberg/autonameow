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
    BASENAME_PROBABLE_EXT_LOOKUP,
    FilenameAnalyzer,
    FilenameTokenizer,
    likely_extension,
    _load_mimetype_extension_suffixes_map_file,
    _parse_mimetype_extension_suffixes_map_data,
    PATH_PROBABLE_EXT_LOOKUP,
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


class TestParseMimetypeExtensionSuffixesMapData(TestCase):
    def _assert_parses(self, given, expect):
        actual = _parse_mimetype_extension_suffixes_map_data(given)
        self.assertEqual(expect, actual, 'Given: "{!s}"'.format(given))

    def test_returns_empty_parsed_data_given_empty_input_data(self):
        self._assert_parses(given='', expect={})
        self._assert_parses(given=' ', expect={})
        self._assert_parses(given=' ', expect={})

    def test_returns_empty_parsed_data_given_only_comment(self):
        self._assert_parses(given='#', expect={})
        self._assert_parses(given='# ', expect={})
        self._assert_parses(given='# foo', expect={})
        self._assert_parses(
            given='''
# foo
            ''',
            expect={}
        )

    def test_parses_single_entry_with_one_ext_matching_one_ext(self):
        self._assert_parses(
            given='''
MIMETYPE application/msword
EXTENSION doc
- doc
            ''',
            expect={
                'application/msword': {
                    'doc': {'doc'}
                },
            }
        )

    def test_parses_single_entry_with_one_ext_matching_two_ext(self):
        self._assert_parses(
            given='''
MIMETYPE application/msword
EXTENSION doc
- doc
- exe
            ''',
            expect={
                'application/msword': {
                    'doc': {'doc', 'exe'}
                },
            }
        )

    def test_parses_two_entries_with_one_ext_matching_one_ext(self):
        self._assert_parses(
            given='''
MIMETYPE application/octet-stream
    EXTENSION chm
    - chm
    EXTENSION azw3
    - azw3
            ''',
            expect={
                'application/octet-stream': {
                    'chm': {'chm'},
                    'azw3': {'azw3'},
                },
            }
        )

    def test_parses_blank_values(self):
        self._assert_parses(
            given='''
MIMETYPE text/x-env
EXTENSION BLANK
- BLANK
EXTENSION sh
- sh
''',
            expect={
                'text/x-env': {
                    '': {''},
                    'sh': {'sh'}
                },
            }
        )

    def test_parses_actual_file_contents(self):
        given = '''
# Data used by filename analyzer to find a new extension from a given
# MIME-type and current extension.
#
# For instance, given this entry:
#
#     MIMETYPE application/octet-stream
#         EXTENSION BLANK
#         - BLANK
#         EXTENSION azw3
#         - azw3
#         EXTENSION bin
#         - bin
#         - binary
#
# First, the analyzed file MIME-type must be 'application/octet-stream'.
# Then, if it does not have a extension, the BLANK extension is used.
# Otherwise, if the file extension is 'azw3', 'azw3' is used.
# Alternatively, 'bin' is used if the file extension is either 'bin' or 'binary'.
# If the file extension is something else, another entry is evaluated.

MIMETYPE application/gzip
EXTENSION gz
- gz
EXTENSION tar.gz
- tar.gz
MIMETYPE application/msword
EXTENSION doc
- doc
MIMETYPE application/octet-stream
EXTENSION BLANK
- BLANK
EXTENSION azw3
- azw3
EXTENSION bin
- bin
- binary
EXTENSION chm
- chm
EXTENSION gz.sig
- gz.sig
EXTENSION hex
- hex
EXTENSION mobi
- mobi
EXTENSION pdf
- pdf
EXTENSION prc
- prc
EXTENSION scpt
- scpt
EXTENSION sig
- sig
EXTENSION sln  # Visual Studio Solution
- sln
EXTENSION tar.gz.sig
- tar.gz.sig
EXTENSION txt
- txt
MIMETYPE application/postscript
EXTENSION eps
- eps
EXTENSION ps
- ps
MIMETYPE application/vnd.ms-powerpoint
EXTENSION ppt
- ppt
MIMETYPE application/x-bzip2
EXTENSION tar.bz2
- tar.bz2
MIMETYPE application/x-gzip
EXTENSION html.gz
- htm.gz
- html
- html.gz
- htm
EXTENSION tar.gz
- tgz
- tar.gz
EXTENSION txt.gz
- txt
- txt.gz
EXTENSION txt.tar.gz
- txt.tgz
- txt.tar.gz
EXTENSION w.gz    # CWEB source code
- w.gz
MIMETYPE application/x-lzma
EXTENSION tar.lzma
- tar.lzma
MIMETYPE application/zip
EXTENSION alfredworkflow
- alfredworkflow
EXTENSION epub
- epub
EXTENSION zip
- zip
MIMETYPE audio/mpeg
EXTENSION mp3
- mp3
MIMETYPE message/rfc822
EXTENSION mhtml
- mhtml
MIMETYPE text/html
EXTENSION html
- htm.gz
- html
- html.gz
- htm
EXTENSION mhtml
- mhtml
EXTENSION txt
- txt
MIMETYPE text/plain
EXTENSION bibtex
- bibtex
EXTENSION c
- c
EXTENSION cpp
- cpp
- c++
EXTENSION css
- css
EXTENSION csv
- csv
EXTENSION gemspec
- gemspec
EXTENSION h
- h
EXTENSION html
- html
- htm
EXTENSION java
- java
EXTENSION js
- js
EXTENSION json
- json
EXTENSION key
- key
EXTENSION log
- log
EXTENSION md
- markdown
- md
- mkd
EXTENSION puml
- puml
EXTENSION py
- py
- python
EXTENSION rake
- rake
EXTENSION sh
- bash
- sh
EXTENSION spec
- spec
EXTENSION txt
- txt
- txt.gz
EXTENSION yaml
- yaml
MIMETYPE text/x-c
EXTENSION c
- txt
- c
EXTENSION h
- h
EXTENSION w
- w
MIMETYPE text/x-c++
EXTENSION cpp
- txt
- cpp
- c++
EXTENSION h
- h
MIMETYPE text/x-env
EXTENSION BLANK
- BLANK
EXTENSION sh
- sh
MIMETYPE text/x-makefile
EXTENSION BLANK
- BLANK
EXTENSION asm
- asm
MIMETYPE text/x-shellscript
EXTENSION py
- py
EXTENSION sh
- txt
- bash
- sh
MIMETYPE text/x-tex
EXTENSION log
- log
EXTENSION tex
- tex
MIMETYPE text/xml
EXTENSION cbp
- cbp
EXTENSION workspace
- workspace
MIMETYPE video/mpeg
EXTENSION VOB
- VOB
EXTENSION mpg
- mpeg
EXTENSION vob
- vob
'''
        self._assert_parses(given,
            expect={
                'application/octet-stream': {
                    # Might be corrupt files.
                    '': {''},
                    'azw3': {'azw3'},
                    'bin': {'bin', 'binary'},
                    'chm': {'chm'},
                    'gz.sig': {'gz.sig'},
                    'hex': {'hex'},
                    'mobi': {'mobi'},
                    'pdf': {'pdf'},
                    'prc': {'prc'},
                    'scpt': {'scpt'},
                    'sig': {'sig'},
                    'sln': {'sln'},  # Visual Studio Solution
                    'tar.gz.sig': {'tar.gz.sig'},
                    'txt': {'txt'}
                },
                'application/msword': {
                    'doc': {'doc'}
                },
                'application/postscript': {
                    'ps': {'ps'},
                    'eps': {'eps'},
                },
                'application/gzip': {
                    'gz': {'gz'},
                    'tar.gz': {'tar.gz'}
                },
                'application/zip': {
                    'zip': {'zip'},
                    'epub': {'epub'},
                    'alfredworkflow': {'alfredworkflow'}
                },
                'application/vnd.ms-powerpoint': {
                    'ppt': {'ppt'},
                },
                'application/x-bzip2': {
                    'tar.bz2': {'tar.bz2'},
                },
                'application/x-gzip': {
                    'html.gz': {'html', 'htm', 'htm.gz', 'html.gz'},
                    'tar.gz': {'tar.gz', 'tgz'},
                    'txt.gz': {'txt.gz', 'txt'},
                    'txt.tar.gz': {'txt.tgz', 'txt.tar.gz'},
                    'w.gz': {'w.gz'}  # CWEB source code
                },
                'application/x-lzma': {
                    'tar.lzma': {'tar.lzma'}
                },
                'audio/mpeg': {
                    'mp3': {'mp3'}
                },
                'message/rfc822': {
                    'mhtml': {'mhtml'}  # Chrome Save as "Webpage, Single File"
                },
                'text/html': {
                    'html': {'html', 'htm', 'htm.gz', 'html.gz'},  # Not actually gzipped HTML
                    'mhtml': {'mhtml'},
                    'txt': {'txt'},
                },
                'text/plain': {
                    'bibtex': {'bibtex'},
                    'c': {'c'},
                    'cpp': {'cpp', 'c++'},
                    'css': {'css'},
                    'csv': {'csv'},
                    'gemspec': {'gemspec'},
                    'h': {'h'},
                    'html': {'html', 'htm'},
                    'java': {'java'},
                    'js': {'js'},
                    'json': {'json'},
                    'key': {'key'},
                    'log': {'log'},
                    'md': {'markdown', 'md', 'mkd'},
                    'puml': {'puml'},
                    'py': {'py', 'python'},
                    'rake': {'rake'},
                    'spec': {'spec'},
                    'sh': {'bash', 'sh'},
                    'txt': {'txt', 'txt.gz'},
                    'yaml': {'yaml'},
                },
                'text/xml': {
                    'cbp': {'cbp'},
                    'workspace': {'workspace'}
                },
                'text/x-c': {
                    'c': {'c', 'txt'},
                    'h': {'h'},
                    'w': {'w'}  # CWEB source code
                },
                'text/x-c++': {
                    'cpp': {'cpp', 'c++', 'txt'},
                    'h': {'h'}
                },
                'text/x-env': {
                    '': {''},
                    'sh': {'sh'}
                },
                'text/x-makefile': {
                    '': {''},
                    'asm': {'asm'}
                },
                'text/x-shellscript': {
                    'sh': {'bash', 'sh', 'txt'},
                    'py': {'py'},
                },
                'text/x-tex': {
                    'log': {'log'},
                    'tex': {'tex'},
                },
                'video/mpeg': {
                    'VOB': {'VOB'},
                    'vob': {'vob'},
                    'mpg': {'mpeg'}
                }
            })


class TestLoadMimetypeExtensionSuffixesMapFile(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.filepath = PATH_PROBABLE_EXT_LOOKUP

    def test_constant_basename_probable_ext_lookup_is_expected_type(self):
        self.assertTrue(uu.is_internalbytestring(BASENAME_PROBABLE_EXT_LOOKUP))

    def test_constant_path_probable_ext_lookup_is_expected_type(self):
        self.assertTrue(uu.is_internalbytestring(PATH_PROBABLE_EXT_LOOKUP))

    def test_extension_suffixes_map_file_exists(self):
        self.assertTrue(uu.file_exists(self.filepath))

    def test_returns_loaded_data_as_expected_type(self):
        actual = _load_mimetype_extension_suffixes_map_file(self.filepath)
        self.assertIsInstance(actual, dict)

    def test_returns_non_empty_dict(self):
        actual = _load_mimetype_extension_suffixes_map_file(self.filepath)
        self.assertGreater(len(actual), 10)
