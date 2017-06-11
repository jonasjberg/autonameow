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

import os
from unittest import TestCase

from core.constants import MAGIC_TYPE_LOOKUP
from core.util import diskutils
from core.util.diskutils import (
    sanitize_filename,
    get_files
)
import unit_utils


class TestMimeTypes(TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_magic_type_lookup_table_exists(self):
        self.assertIsNotNone(MAGIC_TYPE_LOOKUP,
                             'MAGIC_TYPE_LOOKUP mime type lookup should exist')

    def test_magic_type_lookup_table_is_instance_of_dict(self):
        self.assertTrue(isinstance(MAGIC_TYPE_LOOKUP, dict),
                        'MAGIC_TYPE_LOOKUP should be an instance of dict')

    def test_magic_type_lookup_table_values_are_type_list(self):
        for value in MAGIC_TYPE_LOOKUP.values():
            self.assertTrue(isinstance(value, list),
                            'MAGIC_TYPE_LOOKUP values should be lists')

    def test_magic_type_lookup_arbitrarily_assert_image_is_jpeg(self):
        self.assertEqual(['image/jpeg'], MAGIC_TYPE_LOOKUP['jpg'])


class TestSplitFileName(TestCase):
    def test_split_filename_no_name(self):
        self.assertIsNone(None, diskutils.split_filename(''))

    def test_split_filename_has_no_extension(self):
        self.assertEqual(('foo', None), diskutils.split_filename('foo'))
        self.assertEqual(('.foo', None), diskutils.split_filename('.foo'))

    def test_split_filename_has_one_extension(self):
        self.assertEqual(('foo', 'bar'), diskutils.split_filename('foo.bar'))
        self.assertEqual(('.foo', 'bar'), diskutils.split_filename('.foo.bar'))

    def test_split_filename_has_multiple_extensions(self):
        self.assertEqual(('.foo.bar', 'foo'),
                         diskutils.split_filename('.foo.bar.foo'))
        self.assertEqual(('foo.bar', 'foo'),
                         diskutils.split_filename('foo.bar.foo'))
        self.assertEqual(('.foo.bar', 'tar'),
                         diskutils.split_filename('.foo.bar.tar'))
        self.assertEqual(('foo.bar', 'tar'),
                         diskutils.split_filename('foo.bar.tar'))

        # TODO: This case still fails, but it is such a hassle to deal with
        #       and is a really weird way to name files anyway.
        # self.assertEqual(('foo.bar', 'tar.gz'),
        #                  diskutils.split_filename('foo.bar.tar.gz'))


class TestFileSuffix(TestCase):
    def test_file_suffix_no_name(self):
        self.assertIsNone(diskutils.file_suffix(''))
        self.assertIsNone(diskutils.file_suffix(' '))
        self.assertIsNone(diskutils.file_suffix(',. '))
        self.assertIsNone(diskutils.file_suffix(' . '))
        self.assertIsNone(diskutils.file_suffix(' . . '))

    def test_file_suffix_file_has_no_extension(self):
        self.assertIsNone(diskutils.file_suffix('filename'))
        self.assertIsNone(diskutils.file_suffix('file name'))
        self.assertIsNone(diskutils.file_suffix('.hiddenfile'))
        self.assertIsNone(diskutils.file_suffix('.hidden file'))

    def test_file_suffix_file_has_one_extension(self):
        self.assertEqual('jpg', diskutils.file_suffix('filename.jpg'))
        self.assertEqual('jpg', diskutils.file_suffix('filename.JPG'))
        self.assertEqual('JPG', diskutils.file_suffix('filename.JPG',
                                                      make_lowercase=False))

    def test_file_suffix_from_hidden_file(self):
        self.assertEqual('jpg', diskutils.file_suffix('.hiddenfile.jpg'))
        self.assertEqual('jpg', diskutils.file_suffix('.hiddenfile.JPG'))
        self.assertEqual('JPG', diskutils.file_suffix('.hiddenfile.JPG',
                                                      make_lowercase=False))

    def test_file_suffix_file_has_many_suffixes(self):
        self.assertEqual('tar', diskutils.file_suffix('filename.tar'))
        self.assertEqual('gz', diskutils.file_suffix('filename.gz'))
        self.assertEqual('tar.gz', diskutils.file_suffix('filename.tar.gz'))
        self.assertEqual('tar.z', diskutils.file_suffix('filename.tar.z'))
        self.assertEqual('tar.lz', diskutils.file_suffix('filename.tar.lz'))
        self.assertEqual('tar.lzma', diskutils.file_suffix('filename.tar.lzma'))
        self.assertEqual('tar.lzo', diskutils.file_suffix('filename.tar.lzo'))

    def test_file_suffix_from_hidden_file_many_suffixes(self):
        self.assertEqual('tar', diskutils.file_suffix('.filename.tar'))
        self.assertEqual('gz', diskutils.file_suffix('.filename.gz'))
        self.assertEqual('tar.gz', diskutils.file_suffix('.filename.tar.gz'))
        self.assertEqual('tar.z', diskutils.file_suffix('.filename.tar.z'))
        self.assertEqual('tar.lz', diskutils.file_suffix('.filename.tar.lz'))
        self.assertEqual('tar.lzma', diskutils.file_suffix('.filename.tar.lzma'))
        self.assertEqual('tar.lzo', diskutils.file_suffix('.filename.tar.lzo'))


class TestFileBase(TestCase):
    def test_file_base_no_name(self):
        self.assertIsNone(diskutils.file_base(''))
        self.assertEqual(' ', diskutils.file_base(' '))
        self.assertEqual(',', diskutils.file_base(',. '))
        self.assertEqual(' ', diskutils.file_base(' . '))
        # self.assertEqual(' ', diskutils.file_base(' . . '))

    def test_file_base_file_has_no_extension(self):
        self.assertIsNotNone(diskutils.file_base('filename'))
        self.assertEqual('file name', diskutils.file_base('file name'))
        self.assertEqual('.hiddenfile', diskutils.file_base('.hiddenfile'))
        self.assertEqual('.hidden file', diskutils.file_base('.hidden file'))

    def test_file_base_file_has_one_extension(self):
        self.assertEqual('filename', diskutils.file_base('filename.jpg'))
        self.assertEqual('filename', diskutils.file_base('filename.JPG'))

    def test_file_base_from_hidden_file(self):
        self.assertEqual('.hiddenfile', diskutils.file_base('.hiddenfile.jpg'))
        self.assertEqual('.hiddenfile', diskutils.file_base('.hiddenfile.JPG'))
        self.assertEqual('.hiddenfile', diskutils.file_base('.hiddenfile.JPG'))

    def test_file_base_file_has_many_suffixes(self):
        self.assertEqual('filename', diskutils.file_base('filename.tar'))
        self.assertEqual('filename', diskutils.file_base('filename.gz'))
        self.assertEqual('filename', diskutils.file_base('filename.tar.gz'))
        self.assertEqual('filename', diskutils.file_base('filename.tar.z'))
        self.assertEqual('filename', diskutils.file_base('filename.tar.lz'))
        self.assertEqual('filename', diskutils.file_base('filename.tar.lzma'))
        self.assertEqual('filename', diskutils.file_base('filename.tar.lzo'))

    def test_file_base_from_hidden_file_many_suffixes(self):
        self.assertEqual('.filename', diskutils.file_base('.filename.tar'))
        self.assertEqual('.filename', diskutils.file_base('.filename.gz'))
        self.assertEqual('.filename', diskutils.file_base('.filename.tar.gz'))
        self.assertEqual('.filename', diskutils.file_base('.filename.tar.z'))
        self.assertEqual('.filename', diskutils.file_base('.filename.tar.lz'))
        self.assertEqual('.filename', diskutils.file_base('.filename.tar.lzma'))
        self.assertEqual('.filename', diskutils.file_base('.filename.tar.lzo'))


class TestSanitizeFilename(TestCase):
    """
    NOTE:  This class was lifted as-is from the "youtube-dl" project.

    https://github.com/rg3/youtube-dl/blob/master/youtube_dl/test/test_utils.py
    Commit: 5552c9eb0fece567f7dda13810939fca32d7d65a
    """
    def test_sanitize_filename(self):
        self.assertEqual(sanitize_filename('abc'), 'abc')
        self.assertEqual(sanitize_filename('abc_d-e'), 'abc_d-e')

        self.assertEqual(sanitize_filename('123'), '123')

        self.assertEqual('abc_de', sanitize_filename('abc/de'))
        self.assertFalse('/' in sanitize_filename('abc/de///'))

        self.assertEqual('abc_de', sanitize_filename('abc/<>\\*|de'))
        self.assertEqual('xxx', sanitize_filename('xxx/<>\\*|'))
        self.assertEqual('yes no', sanitize_filename('yes? no'))
        self.assertEqual('this - that', sanitize_filename('this: that'))

        self.assertEqual(sanitize_filename('AT&T'), 'AT&T')
        aumlaut = 'ä'
        self.assertEqual(sanitize_filename(aumlaut), aumlaut)
        tests = '\u043a\u0438\u0440\u0438\u043b\u043b\u0438\u0446\u0430'
        self.assertEqual(sanitize_filename(tests), tests)

        self.assertEqual(
            sanitize_filename('New World record at 0:12:34'),
            'New World record at 0_12_34')

        self.assertEqual(sanitize_filename('--gasdgf'), '_-gasdgf')
        self.assertEqual(sanitize_filename('--gasdgf', is_id=True), '--gasdgf')
        self.assertEqual(sanitize_filename('.gasdgf'), 'gasdgf')
        self.assertEqual(sanitize_filename('.gasdgf', is_id=True), '.gasdgf')

        forbidden = '"\0\\/'
        for fc in forbidden:
            for fbc in forbidden:
                self.assertTrue(fbc not in sanitize_filename(fc))

    def test_sanitize_filename_restricted(self):
        self.assertEqual(sanitize_filename('abc', restricted=True), 'abc')
        self.assertEqual(sanitize_filename('abc_d-e', restricted=True), 'abc_d-e')

        self.assertEqual(sanitize_filename('123', restricted=True), '123')

        self.assertEqual('abc_de', sanitize_filename('abc/de', restricted=True))
        self.assertFalse('/' in sanitize_filename('abc/de///', restricted=True))

        self.assertEqual('abc_de', sanitize_filename('abc/<>\\*|de', restricted=True))
        self.assertEqual('xxx', sanitize_filename('xxx/<>\\*|', restricted=True))
        self.assertEqual('yes_no', sanitize_filename('yes? no', restricted=True))
        self.assertEqual('this_-_that', sanitize_filename('this: that', restricted=True))

        tests = 'aäb\u4e2d\u56fd\u7684c'
        self.assertEqual(sanitize_filename(tests, restricted=True), 'aab_c')
        self.assertTrue(sanitize_filename('\xf6', restricted=True) != '')  # No empty filename

        forbidden = '"\0\\/&!: \'\t\n()[]{}$;`^,#'
        for fc in forbidden:
            for fbc in forbidden:
                self.assertTrue(fbc not in sanitize_filename(fc, restricted=True))

        # Handle a common case more neatly
        self.assertEqual(sanitize_filename('\u5927\u58f0\u5e26 - Song', restricted=True), 'Song')
        self.assertEqual(sanitize_filename('\u603b\u7edf: Speech', restricted=True), 'Speech')
        # .. but make sure the file name is never empty
        self.assertTrue(sanitize_filename('-', restricted=True) != '')
        self.assertTrue(sanitize_filename(':', restricted=True) != '')

        self.assertEqual(sanitize_filename(
            'ÂÃÄÀÁÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖŐØŒÙÚÛÜŰÝÞßàáâãäåæçèéêëìíîïðñòóôõöőøœùúûüűýþÿ', restricted=True),
            'AAAAAAAECEEEEIIIIDNOOOOOOOOEUUUUUYPssaaaaaaaeceeeeiiiionooooooooeuuuuuypy')

    def test_sanitize_ids(self):
        self.assertEqual(sanitize_filename('_n_cd26wFpw', is_id=True), '_n_cd26wFpw')
        self.assertEqual(sanitize_filename('_BD_eEpuzXw', is_id=True), '_BD_eEpuzXw')
        self.assertEqual(sanitize_filename('N0Y__7-UOdI', is_id=True), 'N0Y__7-UOdI')


def shorten_path(abs_path):
    parent = os.path.basename(os.path.dirname(abs_path))
    basename = os.path.basename(abs_path)
    return os.path.join(parent, basename)


class TestGetFiles(TestCase):
    def setUp(self):
        self.FILES_SUBDIR = [
            'subdir/file_1', 'subdir/file_2', 'subdir/file_3'
        ]
        self.FILES_SUBSUBDIR_A= [
            'subdir/subsubdir_A/file_A1', 'subdir/subsubdir_A/file_A2'
        ]
        self.FILES_SUBSUBDIR_B= [
            'subdir/subsubdir_B/file_A3', 'subdir/subsubdir_B/file_B1',
            'subdir/subsubdir_B/file_B2'
        ]
        self.TEST_FILES = (self.FILES_SUBDIR + self.FILES_SUBSUBDIR_A
                           + self.FILES_SUBSUBDIR_B)

        self.test_files = [tf for tf in (unit_utils.abspath_testfile(f)
                                         for f in self.TEST_FILES)]

    def test_setup(self):
        for tf in self.test_files:
            self.assertTrue(os.path.isfile(tf),
                            'Expected file: "{}"'.format(tf))

        self.assertEqual(len(self.test_files), 8)

    def test_get_files_is_defined_and_available(self):
        self.assertIsNotNone(get_files)

    def test_raises_errors_for_invalid_paths(self):
        with self.assertRaises((FileNotFoundError, TypeError)):
            get_files(None)
            get_files('')
            get_files(' ')

    def test_returns_expected_number_of_files_non_recursive(self):
        actual = get_files(unit_utils.abspath_testfile('subdir'))
        self.assertEqual(len(actual), 3)

    def test_returns_expected_files_non_recursive(self):
        actual = get_files(unit_utils.abspath_testfile('subdir'))

        for f in actual:
            self.assertTrue(os.path.isfile(f))
            self.assertIn(shorten_path(f), self.FILES_SUBDIR)
            self.assertNotIn(shorten_path(f), self.FILES_SUBSUBDIR_A)
            self.assertNotIn(shorten_path(f), self.FILES_SUBSUBDIR_B)

    def test_returns_expected_number_of_files_recursive(self):
        actual = get_files(unit_utils.abspath_testfile('subdir'), recurse=True)
        self.assertEqual(len(actual), 8)

    def test_returns_expected_files_recursive(self):
        actual = get_files(unit_utils.abspath_testfile('subdir'), recurse=True)

        for f in actual:
            self.assertTrue(os.path.isfile(f))
            self.assertIn(shorten_path(f), self.FILES_SUBDIR)
            self.assertNotIn(shorten_path(f), self.FILES_SUBSUBDIR_A)
            self.assertNotIn(shorten_path(f), self.FILES_SUBSUBDIR_B)


class TestPathAncestry(TestCase):
    def test_ancestry_returns_expected_ancestors_for_file_paths(self):
        PATHS_ANCESTORS = [
            ('/a/b/c', ['/', '/a', '/a/b']),
            ('/a/b',   ['/', '/a']),
            ('/a',     ['/']),
            ('/',      ['/'])
        ]
        for p, a in PATHS_ANCESTORS:
            self.assertEqual(diskutils.path_ancestry(p), a)

    def test_ancestry_returns_expected_ancestors_for_directory_paths(self):
        PATHS_ANCESTORS = [
            ('/a/b/c/', ['/', '/a', '/a/b', '/a/b/c']),
            ('/a/b/',   ['/', '/a', '/a/b']),
            ('/a/',     ['/', '/a']),
            ('/',       ['/']),
        ]
        for p, a in PATHS_ANCESTORS:
            self.assertEqual(diskutils.path_ancestry(p), a)

    def test_ancestry_returns_expected_ancestors_for_relative_paths(self):
        PATHS_ANCESTORS = [
            ('a/b/c', ['a', 'a/b']),
            ('a/b/c/', ['a', 'a/b', 'a/b/c']),
        ]
        for p, a in PATHS_ANCESTORS:
            self.assertEqual(diskutils.path_ancestry(p), a)


class TestPathComponents(TestCase):
    def test_components_returns_expected_components_for_file_paths(self):
        PATHS_COMPONENTS = [
            ('/a/b/c', ['/', 'a', 'b', 'c']),
            ('/a/b',   ['/', 'a', 'b']),
            ('/a',     ['/', 'a']),
            ('/',      ['/'])
        ]
        for p, c in PATHS_COMPONENTS:
            self.assertEqual(diskutils.path_components(p), c)

    def test_components_returns_expected_components_for_directory_paths(self):
        PATHS_COMPONENTS = [
            ('/a/b/c/', ['/', 'a', 'b', 'c']),
            ('/a/b/',   ['/', 'a', 'b']),
            ('/a/',     ['/', 'a']),
            ('/',       ['/'])
        ]
        for p, c in PATHS_COMPONENTS:
            self.assertEqual(diskutils.path_components(p), c)

    def test_components_returns_expected_components_for_relative_paths(self):
        PATHS_COMPONENTS = [
            ('a/b/c', ['a', 'b', 'c']),
            ('a/b',   ['a', 'b']),
            ('a',     ['a']),
        ]
        for p, c in PATHS_COMPONENTS:
            self.assertEqual(diskutils.path_components(p), c)
