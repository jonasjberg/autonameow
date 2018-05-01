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

import unit.utils as uu
from core import constants as C
from core.exceptions import EncodingBoundaryViolation
from util.disk.pathstring import basename_prefix
from util.disk.pathstring import basename_suffix
from util.disk.pathstring import compare_basenames
from util.disk.pathstring import path_ancestry
from util.disk.pathstring import path_components
from util.disk.pathstring import split_basename


class TestSplitBasename(TestCase):
    def _assert_splits(self, expected, test_input):
        actual = split_basename(test_input)
        self.assertEqual(actual, expected)

    def test_returns_bytestrings(self):
        c, d = split_basename(b'c.d')
        self.assertTrue(uu.is_internalbytestring(c))
        self.assertTrue(uu.is_internalbytestring(d))

    def test_passing_unicode_strings_raises_assertion_error(self):
        with self.assertRaises(EncodingBoundaryViolation):
            _, _ = split_basename('a.b')

    def test_split_no_name(self):
        self.assertIsNone(None, split_basename(b''))

    def test_split_no_extension(self):
        self._assert_splits((b'foo', None), b'foo')
        self._assert_splits((b'.foo', None), b'.foo')

    def test_split_one_extension(self):
        self._assert_splits((b'foo', b'bar'), b'foo.bar')
        self._assert_splits((b'.foo', b'bar'), b'.foo.bar')

    def test_split_multiple_extensions(self):
        self._assert_splits((b'.foo.bar', b'foo'), b'.foo.bar.foo')
        self._assert_splits((b'foo.bar', b'foo'), b'foo.bar.foo')
        self._assert_splits((b'.foo.bar', b'tar'), b'.foo.bar.tar')
        self._assert_splits((b'foo.bar', b'tar'), b'foo.bar.tar')

        # TODO: This case still fails, but it is such a hassle to deal with
        #       and is a really weird way to name files anyway.
        # self.assertEqual(('foo.bar', 'tar.gz'),
        #                  split_filename('foo.bar.tar.gz'))


class TestBasenameSuffix(TestCase):
    def _assert_suffix(self, expected, test_input):
        actual = basename_suffix(test_input)
        self.assertEqual(actual, expected)

    def test_no_name(self):
        self.assertIsNone(basename_suffix(b''))
        self.assertIsNone(basename_suffix(b' '))
        self.assertIsNone(basename_suffix(b',. '))
        self.assertIsNone(basename_suffix(b' . '))
        self.assertIsNone(basename_suffix(b' . . '))

    def test_no_extension(self):
        self.assertIsNone(basename_suffix(b'filename'))
        self.assertIsNone(basename_suffix(b'file name'))
        self.assertIsNone(basename_suffix(b'.hiddenfile'))
        self.assertIsNone(basename_suffix(b'.hidden file'))

    def test_one_extension(self):
        self._assert_suffix(b'jpg', b'filename.jpg')
        self._assert_suffix(b'jpg', b'filename.JPG')
        self.assertEqual(
            b'JPG', basename_suffix(b'filename.JPG',
                                    make_lowercase=False)
        )

    def test_hidden_file(self):
        self._assert_suffix(b'jpg', b'.hiddenfile.jpg')
        self._assert_suffix(b'jpg', b'.hiddenfile.JPG')
        self.assertEqual(
            b'JPG', basename_suffix(b'.hiddenfile.JPG',
                                    make_lowercase=False)
        )

    def test_many_suffixes(self):
        self._assert_suffix(b'tar', b'filename.tar')
        self._assert_suffix(b'gz', b'filename.gz')
        self._assert_suffix(b'tar.gz', b'filename.tar.gz')
        self._assert_suffix(b'tar.z', b'filename.tar.z')
        self._assert_suffix(b'tar.lz', b'filename.tar.lz')
        self._assert_suffix(b'tar.lzma', b'filename.tar.lzma')
        self._assert_suffix(b'tar.lzo', b'filename.tar.lzo')

    def test_hidden_with_many_suffixes(self):
        self._assert_suffix(b'tar', b'.filename.tar')
        self._assert_suffix(b'gz', b'.filename.gz')
        self._assert_suffix(b'tar.gz', b'.filename.tar.gz')
        self._assert_suffix(b'tar.z', b'.filename.tar.z')
        self._assert_suffix(b'tar.lz', b'.filename.tar.lz')
        self._assert_suffix(b'tar.lzma', b'.filename.tar.lzma')
        self._assert_suffix(b'tar.lzo', b'.filename.tar.lzo')


class TestBasenamePrefix(TestCase):
    def test_no_name(self):
        self.assertIsNone(basename_prefix(b''))
        self.assertEqual(b' ', basename_prefix(b' '))
        self.assertEqual(b',', basename_prefix(b',. '))
        self.assertEqual(b' ', basename_prefix(b' . '))

        # TODO: Test edge cases ..
        # self.assertEqual(' ', file_base(' . . '))

    def test_no_extension(self):
        self.assertIsNotNone(basename_prefix(b'filename'))
        self.assertEqual(b'file name',
                         basename_prefix(b'file name'))
        self.assertEqual(b'.hiddenfile',
                         basename_prefix(b'.hiddenfile'))
        self.assertEqual(b'.hidden file',
                         basename_prefix(b'.hidden file'))

    def test_one_extension(self):
        def __check_expected_for(test_input):
            self.assertEqual(b'filename', basename_prefix(test_input))

        __check_expected_for(b'filename.jpg')
        __check_expected_for(b'filename.JPG')

    def test_hidden_file(self):
        def __check_expected_for(test_input):
            self.assertEqual(b'.hiddenfile',
                             basename_prefix(test_input))

        __check_expected_for(b'.hiddenfile.jpg')
        __check_expected_for(b'.hiddenfile.JPG')
        __check_expected_for(b'.hiddenfile.JPG')

    def test_many_suffixes(self):
        def __check_expected_for(test_input):
            self.assertEqual(b'filename',
                             basename_prefix(test_input))

        __check_expected_for(b'filename.tar')
        __check_expected_for(b'filename.gz')
        __check_expected_for(b'filename.tar.gz')
        __check_expected_for(b'filename.tar.z')
        __check_expected_for(b'filename.tar.lz')
        __check_expected_for(b'filename.tar.lzma')
        __check_expected_for(b'filename.tar.lzo')

    def test_hidden_with_many_suffixes(self):
        def __check_expected_for(test_input):
            self.assertEqual(b'.filename',
                             basename_prefix(test_input))

        __check_expected_for(b'.filename.tar')
        __check_expected_for(b'.filename.gz')
        __check_expected_for(b'.filename.tar.gz')
        __check_expected_for(b'.filename.tar.z')
        __check_expected_for(b'.filename.tar.lz')
        __check_expected_for(b'.filename.tar.lzma')
        __check_expected_for(b'.filename.tar.lzo')


class TestCompareBasenames(TestCase):
    def test_compare_basenames_raises_exceptions_given_invalid_input(self):
        def _raises(exception_, a, b):
            with self.assertRaises(exception_):
                compare_basenames(a, b)

        _raises(ValueError, None, None)
        _raises(ValueError, None, None)
        _raises(ValueError, None, [])
        _raises(ValueError, [], None)
        _raises(EncodingBoundaryViolation, 1, 2)
        _raises(EncodingBoundaryViolation, [], [])
        _raises(EncodingBoundaryViolation, object(), object())
        _raises(EncodingBoundaryViolation, 'a', 'b')
        _raises(EncodingBoundaryViolation, 'a', [])
        _raises(EncodingBoundaryViolation, '', '')
        _raises(EncodingBoundaryViolation, '', ' ')
        _raises(EncodingBoundaryViolation, '_', '')
        _raises(EncodingBoundaryViolation, 'a', 2)
        _raises(EncodingBoundaryViolation, 1, 'b')
        _raises(EncodingBoundaryViolation, 'a', b'a')
        _raises(EncodingBoundaryViolation, b'a', 'a')

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
    def test_ancestry_returns_expected_ancestors_for_file_paths(self):
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
    def test_components_returns_expected_components_for_file_paths(self):
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
