# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2019 Jonas Sjöberg <autonameow@jonasjberg.com>
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

from unittest import expectedFailure, TestCase

import unit.utils as uu
from core import constants as C
from util.disk.pathstring import basename_prefix
from util.disk.pathstring import basename_suffix
from util.disk.pathstring import compare_basenames
from util.disk.pathstring import EMPTY_FILENAME_PART
from util.disk.pathstring import path_ancestry
from util.disk.pathstring import path_components
from util.disk.pathstring import split_basename


class TestSplitBasename(TestCase):
    def _assert_splits(self, expected_prefix, expected_suffix, given):
        with self.subTest(
            given=given,
            expect=(expected_prefix, expected_suffix)
        ):
            actual_prefix, actual_suffix = split_basename(given)
            self.assertEqual(expected_prefix, actual_prefix)
            self.assertEqual(expected_suffix, actual_suffix)

    def test_returns_bytestrings(self):
        actual = split_basename(b'c.d')
        for part in actual:
            self.assertTrue(uu.is_internalbytestring(part))

    def test_raises_assertion_error_given_unicode_strings(self):
        with self.assertRaises(AssertionError):
            _, _ = split_basename('a.b')

    def test_empty_filenames(self):
        self._assert_splits(EMPTY_FILENAME_PART, EMPTY_FILENAME_PART, b'')

    def test_filenames_without_any_extension(self):
        self._assert_splits(b'foo',  EMPTY_FILENAME_PART, b'foo')
        self._assert_splits(b'.foo', EMPTY_FILENAME_PART, b'.foo')

    def test_split_one_extension(self):
        self._assert_splits(b'foo',  b'bar', b'foo.bar')
        self._assert_splits(b'.foo', b'bar', b'.foo.bar')
        self._assert_splits(b'foo', b'txt', b'foo.txt')

    @expectedFailure
    def test_unhandled_case(self):
        self._assert_splits(
            b'Resuming Ancient K# and .MET Development',
            b'.zip',
            b'Resuming Ancient K# and .MET Development.zip'
        )

    def test_split_multiple_extensions(self):
        for expect_prefix, expect_suffix, given in [
            (b'.foobar', b'foo',    b'.foobar.foo'),
            (b'foobar',  b'foo',    b'foobar.foo'),
            (b'.foobar', b'tar',    b'.foobar.tar'),
            (b'foobar',  b'tar',    b'foobar.tar'),
            (b'foobar',  b'tar.gz', b'foobar.tar.gz'),

            (b'.foo.bar', b'foo',    b'.foo.bar.foo'),
            (b'foo.bar',  b'foo',    b'foo.bar.foo'),
            (b'.foo.bar', b'tar',    b'.foo.bar.tar'),
            (b'foo.bar',  b'tar',    b'foo.bar.tar'),
            (b'foo.bar',  b'tar.gz', b'foo.bar.tar.gz'),
        ]:
            self._assert_splits(expect_prefix, expect_suffix, given)

    def test_split_certain_compounded_extensions(self):
        for expect_prefix, expect_suffix, given in [
            (b'foo.bar', b'tar.7z',   b'foo.bar.tar.7z'),
            (b'foo.bar', b'tar.bz2',  b'foo.bar.tar.bz2'),
            (b'foo.bar', b'tar.gz',   b'foo.bar.tar.gz'),
            (b'foo.bar', b'tar.lz',   b'foo.bar.tar.lz'),
            (b'foo.bar', b'tar.lzma', b'foo.bar.tar.lzma'),
            (b'foo.bar', b'tar.lzo',  b'foo.bar.tar.lzo'),
            (b'foo.bar', b'tar.sig',  b'foo.bar.tar.sig'),
            (b'foo.bar', b'tar.tbz',  b'foo.bar.tar.tbz'),
            (b'foo.bar', b'tar.tbz2', b'foo.bar.tar.tbz2'),
            (b'foo.bar', b'tar.tgz',  b'foo.bar.tar.tgz'),
            (b'foo.bar', b'tar.xz',   b'foo.bar.tar.xz'),
            (b'foo.bar', b'tar.z',    b'foo.bar.tar.z'),
            (b'foo.bar', b'tar.zip',  b'foo.bar.tar.zip'),
            (b'foo.bar', b'tar.zipx', b'foo.bar.tar.zipx'),
        ]:
            self._assert_splits(expect_prefix, expect_suffix, given)


class TestBasenameSuffix(TestCase):
    def _assert_suffix(self, expected, given):
        with self.subTest(given=given, expected=EMPTY_FILENAME_PART):
            actual = basename_suffix(given)
            self.assertEqual(expected, actual)

    def _assert_no_suffix(self, given):
        with self.subTest(given=given):
            actual = basename_suffix(given)
            self.assertEqual(EMPTY_FILENAME_PART, actual)

    def test_empty_or_practically_empty_filenames(self):
        for given in [
            b'',
            b' ',
            b',. ',
            b' . ',
            b' . . ',
            b'_',
            b'__',
            b'_____',
        ]:
            self._assert_no_suffix(given)

    def test_filenames_without_any_extension(self):
        for given in [
            b'filename',
            b'file name',
            b'.hiddenfile',
            b'.hidden file',
        ]:
            self._assert_no_suffix(given)

    def test_filenames_with_one_extension(self):
        self._assert_suffix(b'jpg', b'filename.jpg')
        self._assert_suffix(b'jpg', b'filename.JPG')

    def test_filenames_with_one_extension_make_lowercase(self):
        self.assertEqual(
            b'JPG', basename_suffix(b'filename.JPG', make_lowercase=False)
        )

    def test_hidden_unix_filenames_with_leading_periods(self):
        self._assert_suffix(b'jpg', b'.hiddenfile.jpg')
        self._assert_suffix(b'jpg', b'.hiddenfile.JPG')

    def test_hidden_file_make_lowercase(self):
        self.assertEqual(
            b'JPG', basename_suffix(b'.hiddenfile.JPG', make_lowercase=False)
        )

    def test_filenames_with_many_suffixes(self):
        for expect, given in [
            (b'tar', b'filename.tar'),
            (b'gz', b'filename.gz'),
            (b'tar.gz', b'filename.tar.gz'),
            (b'tar.z', b'filename.tar.z'),
            (b'tar.lz', b'filename.tar.lz'),
            (b'tar.lzma', b'filename.tar.lzma'),
            (b'tar.lzo', b'filename.tar.lzo'),
        ]:
            self._assert_suffix(expect, given)

    def test_hidden_with_many_suffixes(self):
        for expect, given in [
            (b'tar', b'.filename.tar'),
            (b'gz', b'.filename.gz'),
            (b'tar.gz', b'.filename.tar.gz'),
            (b'tar.z', b'.filename.tar.z'),
            (b'tar.lz', b'.filename.tar.lz'),
            (b'tar.lzma', b'.filename.tar.lzma'),
            (b'tar.lzo', b'.filename.tar.lzo'),
        ]:
            self._assert_suffix(expect, given)


class TestBasenamePrefix(TestCase):
    def _assert_prefix(self, expected, given):
        with self.subTest(given=given, expected=expected):
            actual = basename_prefix(given)
            self.assertEqual(expected, actual)

    def _assert_no_prefix(self, given):
        with self.subTest(given=given):
            actual = basename_prefix(given)
            self.assertEqual(EMPTY_FILENAME_PART, actual)

    def test_empty_or_practically_empty_filenames(self):
        self._assert_no_prefix(b'')

        for expect, given in [
            (b' ', b' '),
            (b',', b',. '),
            (b' ', b' . '),
        ]:
            self._assert_prefix(expect, given)

    def test_filenames_without_any_extension(self):
        for expect, given in [
            (b'filename', b'filename'),
            (b'file name', b'file name'),
            (b'.hiddenfile', b'.hiddenfile'),
            (b'.hidden file', b'.hidden file'),
        ]:
            self._assert_prefix(expect, given)

    def test_filenames_with_one_extension(self):
        for given in [
            b'filename', b'filename.jpg',
            b'filename', b'filename.JPG',
        ]:
            self._assert_prefix(b'filename', given)

    def test_hidden_unix_filenames_with_leading_periods(self):
        for given in [
            b'.hiddenfile.jpg',
            b'.hiddenfile.JPG',
        ]:
            self._assert_prefix(b'.hiddenfile', given)

    def test_filenames_with_many_suffixes(self):
        for given in [
            b'filename.tar',
            b'filename.gz',
            b'filename.tar.gz',
            b'filename.tar.z',
            b'filename.tar.lz',
            b'filename.tar.lzma',
            b'filename.tar.lzo',
        ]:
            self._assert_prefix(b'filename', given)

    def test_hidden_with_many_suffixes(self):
        for given in [
            b'filename.tar',
            b'filename.gz',
            b'filename.tar.gz',
            b'filename.tar.z',
            b'filename.tar.lz',
            b'filename.tar.lzma',
            b'filename.tar.lzo',
        ]:
            self._assert_prefix(b'filename', given)


class TestCompareBasenames(TestCase):
    def test_raises_exception_given_invalid_input(self):
        for a, b in [
            (None, None),
            (None, None),
            (None, []),
            ([], None),
            (1, 2),
            ([], []),
            (object(), object()),
            ('a', 'b'),
            ('a', []),
            ('', ''),
            ('', ' '),
            ('_', ''),
            ('a', 2),
            (1, 'b'),
            ('a', b'a'),
            (b'a', 'a'),
        ]:
            with self.assertRaises(AssertionError):
                compare_basenames(a, b)

    def test_comparing_equal_basenames_returns_true(self):
        def _assert_true(first, second):
            actual = compare_basenames(first, second)
            self.assertTrue(actual)
            self.assertIsInstance(actual, bool)

        _assert_true(b'', b'')
        _assert_true(b' ', b' ')
        _assert_true(b'a', b'a')
        _assert_true(b'foo', b'foo')
        _assert_true(b'_', b'_')
        _assert_true('å'.encode(C.DEFAULT_ENCODING),
                     'å'.encode(C.DEFAULT_ENCODING))
        _assert_true('ö'.encode(C.DEFAULT_ENCODING),
                     'ö'.encode(C.DEFAULT_ENCODING))
        _assert_true('A_ö'.encode(C.DEFAULT_ENCODING),
                     'A_ö'.encode(C.DEFAULT_ENCODING))
        _assert_true(b'__', b'__')

    def test_comparing_unequal_basenames_returns_false(self):
        def _assert_false(first, second):
            actual = compare_basenames(first, second)
            self.assertFalse(actual)
            self.assertIsInstance(actual, bool)

        _assert_false(b' ', b'y')
        _assert_false(b'x', b'y')
        _assert_false(b'foo_', b'foo')
        _assert_false('ä'.encode(C.DEFAULT_ENCODING), b'a')
        _assert_false('Ä'.encode(C.DEFAULT_ENCODING), b'A')
        _assert_false('Ä'.encode(C.DEFAULT_ENCODING),
                      'A'.encode(C.DEFAULT_ENCODING))

        # Looks identical but the second string contains character '\xc2\xa0'
        # between the last timestamp digit and 'W' instead of a simple space.
        _assert_false(
            '2017-08-14T015051 Working on autonameow -- dev projects.png'.encode(C.DEFAULT_ENCODING),
            '2017-08-14T015051 Working on autonameow -- dev projects.png'.encode(C.DEFAULT_ENCODING)
        )


class TestPathAncestry(TestCase):
    def test_ancestry_returns_expected_ancestors_for_filepaths(self):
        PATHS_ANCESTORS = [
            ('/a/b/c', ['/', '/a', '/a/b']),
            ('/a/b',   ['/', '/a']),
            ('/a',     ['/']),
            ('/',      ['/'])
        ]
        for p, a in PATHS_ANCESTORS:
            self.assertEqual(path_ancestry(p), a)

    def test_ancestry_returns_expected_ancestors_for_directory_paths(self):
        PATHS_ANCESTORS = [
            ('/a/b/c/', ['/', '/a', '/a/b', '/a/b/c']),
            ('/a/b/',   ['/', '/a', '/a/b']),
            ('/a/',     ['/', '/a']),
            ('/',       ['/']),
        ]
        for p, a in PATHS_ANCESTORS:
            self.assertEqual(path_ancestry(p), a)

    def test_ancestry_returns_expected_ancestors_for_relative_paths(self):
        PATHS_ANCESTORS = [
            ('a/b/c', ['a', 'a/b']),
            ('a/b/c/', ['a', 'a/b', 'a/b/c']),
        ]
        for p, a in PATHS_ANCESTORS:
            self.assertEqual(path_ancestry(p), a)


class TestPathComponents(TestCase):
    def test_components_returns_expected_components_for_filepaths(self):
        PATHS_COMPONENTS = [
            ('/a/b/c', ['/', 'a', 'b', 'c']),
            ('/a/b',   ['/', 'a', 'b']),
            ('/a',     ['/', 'a']),
            ('/',      ['/'])
        ]
        for p, c in PATHS_COMPONENTS:
            self.assertEqual(path_components(p), c)

    def test_components_returns_expected_components_for_directory_paths(self):
        PATHS_COMPONENTS = [
            ('/a/b/c/', ['/', 'a', 'b', 'c']),
            ('/a/b/',   ['/', 'a', 'b']),
            ('/a/',     ['/', 'a']),
            ('/',       ['/'])
        ]
        for p, c in PATHS_COMPONENTS:
            self.assertEqual(path_components(p), c)

    def test_components_returns_expected_components_for_relative_paths(self):
        PATHS_COMPONENTS = [
            ('a/b/c', ['a', 'b', 'c']),
            ('a/b',   ['a', 'b']),
            ('a',     ['a']),
        ]
        for p, c in PATHS_COMPONENTS:
            self.assertEqual(path_components(p), c)
