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
from unittest import TestCase
from unittest.mock import Mock, patch

import unit.utils as uu
from analyzers.analyze_filename import BASENAME_PROBABLE_EXT_LOOKUP
from analyzers.analyze_filename import FilenameAnalyzer
from analyzers.analyze_filename import likely_extension
from analyzers.analyze_filename import PATH_PROBABLE_EXT_LOOKUP
from analyzers.analyze_filename import _parse_mimetype_extension_suffixes_map_data
from analyzers.analyze_filename import _read_probable_extension_config_file


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

    @classmethod
    def setUpClass(cls):
        from util.coercers import NULL_AW_MIMETYPE
        cls.null_mimetype = NULL_AW_MIMETYPE

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
        self.fna._file_mimetype = self.null_mimetype
        self.fna._basename_suffix = 'jpg'
        self.__assert_extension('jpg')

    def test__get_extension_returns_expected_given_empty_suffix_null_mime(self):
        self.fna._file_mimetype = self.null_mimetype
        self.fna._basename_suffix = ''
        self.__assert_extension('')

    def test__get_extension_returns_none_given_none_suffix_null_mime(self):
        self.fna._file_mimetype = self.null_mimetype
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

            (Expect('azw'),
             Given(suffix='azw', mime='application/octet-stream')),
            (Expect('azw3'),
             Given(suffix='azw3', mime='application/octet-stream')),
            (Expect('azw3'),
             Given(suffix='azw3', mime='application/x-mobipocket-ebook')),
            (Expect('azw4'),
             Given(suffix='azw4', mime='application/octet-stream')),
            (Expect('azw4'),
             Given(suffix='azw4', mime='application/x-mobipocket-ebook')),

            (Expect('bin'),
             Given(suffix='bin', mime='application/octet-stream')),
            (Expect('bz2'),
             Given(suffix='bz2', mime='application/x-bzip2')),
            (Expect('chm'),
             Given(suffix='chm', mime='application/octet-stream')),

            # TeX/LaTeX
            (Expect('aux'),
             Given(suffix='aux', mime='text/plain')),
            (Expect('bibtex'),
             Given(suffix='bibtex', mime='text/plain')),
            (Expect('bib'),
             Given(suffix='bib', mime='text/plain')),
            (Expect('bbl'),
             Given(suffix='bbl', mime='text/plain')),
            (Expect('bcf'),
             Given(suffix='bcf', mime='text/xml')),
            (Expect('blg'),
             Given(suffix='blg', mime='text/plain')),
            (Expect('dvi'),
             Given(suffix='dvi', mime='application/x-dvi')),
            (Expect('fdb_latexmk'),
             Given(suffix='fdb_latexmk', mime='text/plain')),
            (Expect('fls'),
             Given(suffix='fls', mime='text/plain')),
            (Expect('out'),
             Given(suffix='out', mime='inode/x-empty')),
            (Expect('log'),
             Given(suffix='log', mime='text/x-tex')),

            (Expect(''),
             Given(suffix='', mime='text/plain')),

            (Expect('c'),
             Given(suffix='c', mime='text/x-c')),
            (Expect('c'),
             Given(suffix='txt', mime='text/x-c')),
            (Expect('c'),
             Given(suffix='c', mime='text/plain')),
            (Expect('c'),
             Given(suffix='c', mime='application/octet-stream')),
            (Expect('conf'),
             Given(suffix='conf', mime='text/plain')),
            (Expect('cpp'),
             Given(suffix='cpp', mime='text/x-c++')),
            (Expect('cpp'),
             Given(suffix='cpp', mime='text/plain')),
            (Expect('cpp'),
             Given(suffix='c++', mime='text/x-c++')),
            (Expect('cpp'),
             Given(suffix='c++', mime='text/plain')),
            (Expect('h'),
             Given(suffix='h', mime='text/x-c')),
            (Expect('h'),
             Given(suffix='h', mime='application/octet-stream')),

            # Incorrectly identified CSS
            (Expect('css'),
             Given(suffix='css', mime='text/x-asm')),

            # Microsoft Office
            (Expect('doc'),
             Given(suffix='doc', mime='application/msword')),
            (Expect('doc'),
             Given(suffix='', mime='application/msword')),
            (Expect('xls'),
             Given(suffix='xls', mime='application/vnd.ms-excel')),
            (Expect('xls'),
             Given(suffix='', mime='application/vnd.ms-excel')),
            (Expect('xlsx'),
             Given(suffix='xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')),
            (Expect('xlsx'),
             Given(suffix='', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')),

            (Expect('eps'),
             Given(suffix='eps', mime='application/postscript')),
            (Expect('hex'),
             Given(suffix='hex', mime='application/octet-stream')),

            (Expect('dll'),
             Given(suffix='dll', mime='application/x-dosexec')),
            (Expect('exe'),
             Given(suffix='exe', mime='application/x-dosexec')),
            (Expect('exe'),
             Given(suffix='', mime='application/x-dosexec')),
            (Expect('pyd'),
             Given(suffix='pyd', mime='application/x-dosexec')),

            (Expect('html'),
             Given(suffix='htm', mime='text/xml')),
            (Expect('html'),
             Given(suffix='html', mime='text/xml')),
            (Expect('html'),
             Given(suffix='htm.gz', mime='text/html')),
            (Expect('html.1'),
             Given(suffix='html.1', mime='text/html')),
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

            # Incorrectly identified JavaScript
            (Expect('js'),
             Given(suffix='js', mime='text/html')),

            (Expect('log'),
             Given(suffix='log', mime='text/plain')),
            (Expect('log'),
             Given(suffix='log', mime='application/octet-stream')),

            # OpenOffice/LibreOffice
            (Expect('odp'),
             Given(suffix='odp', mime='application/vnd.oasis.opendocument.presentation')),
            (Expect('odp'),
             Given(suffix='', mime='application/vnd.oasis.opendocument.presentation')),
            (Expect('ods'),
             Given(suffix='ods', mime='application/vnd.oasis.opendocument.spreadsheet')),
            (Expect('ods'),
             Given(suffix='', mime='application/vnd.oasis.opendocument.spreadsheet')),
            (Expect('odt'),
             Given(suffix='odt', mime='application/vnd.oasis.opendocument.text')),
            (Expect('odt'),
             Given(suffix='', mime='application/vnd.oasis.opendocument.text')),

            (Expect('deb'),
             Given(suffix='deb', mime='application/vnd.debian.binary-package')),

            (Expect('lc'),
             Given(suffix='lc', mime='text/plain')),

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

            # Might be corrupt or misidentified mp4
            (Expect('mp4'),
             Given(suffix='mp4', mime='application/octet-stream')),

            # National Instruments Multisim
            (Expect('ms10'),
             Given(suffix='ms10', mime='application/octet-stream')),
            (Expect('ms10 (Security copy)'),
             Given(suffix='ms10 (Security copy)', mime='application/octet-stream')),
            (Expect('ms10 (Security copy)'),
             Given(suffix='ms10-(Security-copy)', mime='application/octet-stream')),
            (Expect('ms12'),
             Given(suffix='ms12', mime='application/octet-stream')),
            (Expect('ms12 (Security copy)'),
             Given(suffix='ms12 (Security copy)', mime='application/octet-stream')),
            (Expect('ms12 (Security copy)'),
             Given(suffix='ms12-(Security-copy)', mime='application/octet-stream')),

            # Texas Instruments calculator firmware
            (Expect('89u'),
             Given(suffix='89u', mime='application/octet-stream')),
            (Expect('rom'),
             Given(suffix='ROM', mime='application/octet-stream')),
            (Expect('rom'),
             Given(suffix='rom', mime='application/octet-stream')),

            (Expect('pdf'),
             Given(suffix='pdf', mime='application/pdf')),
            (Expect('pdf'),
             Given(suffix='pdf', mime='application/octet-stream')),
            (Expect('ps'),
             Given(suffix='ps', mime='application/postscript')),

            (Expect('bat'),
             Given(suffix='bat', mime='text/x-msdos-batch')),
            (Expect('bat'),
             Given(suffix='', mime='text/x-msdos-batch')),

            (Expect('egg'),
             Given(suffix='egg', mime='text/x-shellscript')),

            (Expect('py'),
             Given(suffix='py', mime='text/x-shellscript')),
            (Expect('py'),
             Given(suffix='py', mime='text/x-python')),
            (Expect('py'),
             Given(suffix='', mime='text/x-python')),

            (Expect('sh'),
             Given(suffix='sh', mime='text/plain')),
            (Expect('sh'),
             Given(suffix='sh', mime='text/x-shellscript')),
            (Expect('sh'),
             Given(suffix='txt', mime='text/x-shellscript')),
            (Expect('sh'),
             Given(suffix='sh', mime='text/x-env')),

            (Expect('scpt'),
             Given(suffix='scpt', mime='application/octet-stream')),

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

            (Expect('ps1'),
             Given(suffix='ps1', mime='text/plain')),

            # "Easy Install" package listing ('easy-install.pth')
            (Expect('pth'),
             Given(suffix='pth', mime='text/plain')),

            (Expect('rst'),
             Given(suffix='rst', mime='text/plain')),
            (Expect('rst'),
             Given(suffix='rst', mime='text/html')),
            (Expect('rst'),
             Given(suffix='rst', mime='text/x-python')),

            (Expect('tcl'),
             Given(suffix='tcl', mime='text/plain')),

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

            (Expect('xml'),
             Given(suffix='xml', mime='text/plain')),

            (Expect('zip'),
             Given(suffix='zip', mime='application/zip')),
            (Expect('zip'),
             Given(suffix='zip', mime='application/x-zip')),

            # Chrome Save as "Webpage, Single File"
            (Expect('mhtml'),
             Given(suffix='mhtml', mime='message/rfc822')),

            # Apple disk image
            (Expect('dmg'),
             Given(suffix='dmg', mime='application/x-iso9660-image')),
            (Expect('dmg'),
             Given(suffix='dmg', mime='application/x-bzip2')),
            (Expect('dmg'),
             Given(suffix='dmg', mime='application/octet-stream')),

            # Apple metadata
            (Expect('AAE'),
             Given(suffix='AAE', mime='application/xml')),
            (Expect('aae'),
             Given(suffix='aae', mime='application/xml')),

            # Adobe
            (Expect('psd'),
             Given(suffix='psd', mime='image/vnd.adobe.photoshop')),

            # MacOS system report
            (Expect('spx'),
             Given(suffix='spx', mime='text/xml')),

            # Microsoft paper specification file
            (Expect('xps'),
             Given(suffix='xps', mime='application/octet-stream')),

            # Safari saved webpage
            (Expect('webarchive'),
             Given(suffix='webarchive', mime='application/octet-stream')),

            # Audio
            (Expect('mp3'),
             Given(suffix='mp3', mime='application/octet-stream')),
            (Expect('mp3'),
             Given(suffix='mp3', mime='audio/mpeg')),
            (Expect('wav'),
             Given(suffix='wav', mime='audio/x-wav')),
            (Expect('wav'),
             Given(suffix='', mime='audio/x-wav')),
            (Expect('wma'),
             Given(suffix='wma', mime='video/x-ms-asf')),
        ]

    def test_returns_expected(self):
        for expect, input_args in self.expect_testinput:
            actual = likely_extension(*input_args)
            _m = 'Expected: "{!s}"  Actual: "{!s}”  ("{!s}”)'.format(
                expect.expected, actual, input_args
            )
            self.assertEqual(expect.expected, actual, _m)


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

# Not indented ..
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
MIMETYPE application/x-lzma # Not indented ..
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
        self._assert_parses(given, expect={
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
        actual = _read_probable_extension_config_file(self.filepath)
        self.assertIsInstance(actual, dict)

    def test_returns_non_empty_dict(self):
        actual = _read_probable_extension_config_file(self.filepath)
        self.assertGreater(len(actual), 10)
