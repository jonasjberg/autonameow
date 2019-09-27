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

#   -------------------------------------------------------------------------
#   This code is based on the "beets" project.
#   File:    test/test_util.py
#   Commit:  a88682e7bbc03b94aabb3290058b8c9b8aba80e0
#   -------------------------------------------------------------------------
#
#   This file is part of beets.
#   Copyright 2016, Adrian Sampson.
#
#   Permission is hereby granted, free of charge, to any person obtaining
#   a copy of this software and associated documentation files (the
#   "Software"), to deal in the Software without restriction, including
#   without limitation the rights to use, copy, modify, merge, publish,
#   distribute, sublicense, and/or sell copies of the Software, and to
#   permit persons to whom the Software is furnished to do so, subject to
#   the following conditions:
#
#   The above copyright notice and this permission notice shall be
#   included in all copies or substantial portions of the Software.

import os
import sys
from contextlib import contextmanager
from unittest import expectedFailure, TestCase

import unit.utils as uu
from util.encoding import arg_encoding
from util.encoding import autodetect_decode
from util.encoding import detect_encoding
from util.encoding import bytestring_path
from util.encoding import convert_command_args
from util.encoding import normpath
from util.encoding import syspath


class UtilTest(TestCase):
    def test_convert_command_args_keeps_undecodeable_bytes(self):
        arg = b'\x82'  # non-ascii bytes
        cmd_args = convert_command_args([arg])

        self.assertEqual(cmd_args[0],
                         arg.decode(arg_encoding(), 'surrogateescape'))


class PathConversionTest(TestCase):
    def test_syspath_windows_format(self):
        with platform_windows():
            path = os.path.join('a', 'b', 'c')
            outpath = syspath(path)
        self.assertTrue(uu.is_internalstring(outpath))
        self.assertTrue(outpath.startswith('\\\\?\\'))

    def test_syspath_windows_format_unc_path(self):
        # The \\?\ prefix on Windows behaves differently with UNC
        # (network share) paths.
        path = '\\\\server\\share\\file.mp3'
        with platform_windows():
            outpath = syspath(path)
        self.assertTrue(uu.is_internalstring(outpath))
        self.assertEqual(outpath, '\\\\?\\UNC\\server\\share\\file.mp3')

    def test_syspath_posix_unchanged(self):
        with platform_posix():
            path = os.path.join('a', 'b', 'c')
            outpath = syspath(path)
        self.assertEqual(path, outpath)

    @staticmethod
    def _windows_bytestring_path(path):
        old_gfse = sys.getfilesystemencoding
        sys.getfilesystemencoding = lambda: 'mbcs'
        try:
            with platform_windows():
                return bytestring_path(path)
        finally:
            sys.getfilesystemencoding = old_gfse

    def test_bytestring_path_windows_encodes_utf8(self):
        path = 'caf\xe9'
        outpath = self._windows_bytestring_path(path)
        self.assertEqual(path, outpath.decode('utf-8'))

    def test_bytestring_path_windows_removes_magic_prefix(self):
        path = '\\\\?\\C:\\caf\xe9'
        outpath = self._windows_bytestring_path(path)
        self.assertEqual(outpath, 'C:\\caf\xe9'.encode('utf-8'))


class TestByteStringPathWithInvalidInput(TestCase):
    def test_bytestring_path_returns_expected_for_empty_input(self):
        self.assertEqual(bytestring_path(''), b'')


class TestNormPath(TestCase):
    def test_normpath_returns_expected_for_valid_input(self):
        self.assertNotEqual('/', normpath('/'))
        self.assertNotEqual('/tmp', normpath('/tmp/'))

    def test_normpath_raises_value_error_for_empty_input(self):
        with self.assertRaises(ValueError):
            normpath('')
            self.assertNotEqual(b'', normpath(''))


# Platform mocking.

@contextmanager
def platform_windows():
    import ntpath
    old_path = os.path
    try:
        os.path = ntpath
        yield
    finally:
        os.path = old_path


@contextmanager
def platform_posix():
    import posixpath
    old_path = os.path
    try:
        os.path = posixpath
        yield
    finally:
        os.path = old_path


@contextmanager
def system_mock(name):
    import platform
    old_system = platform.system
    platform.system = lambda: name
    try:
        yield
    finally:
        platform.system = old_system


class TestAutodetectDecode(TestCase):
    def _assert_encodes(self, encoding, string):
        _encoded_text = string.encode(encoding)
        self.assertTrue(uu.is_internalbytestring(_encoded_text))

        actual = autodetect_decode(_encoded_text)
        self.assertEqual(string, actual)
        self.assertEqual(type(string), type(actual))

    def test_raises_exception_for_non_strings(self):
        with self.assertRaises(TypeError):
            autodetect_decode(object())

        with self.assertRaises(TypeError):
            autodetect_decode(None)

    def test_returns_expected_given_unicode(self):
        actual = autodetect_decode('foo bar')
        self.assertEqual('foo bar', actual)

    def test_returns_expected_given_ascii(self):
        self._assert_encodes('ascii', '')
        self._assert_encodes('ascii', ' ')
        self._assert_encodes('ascii', '\n')
        self._assert_encodes('ascii', '\n ')
        self._assert_encodes('ascii', ' \n ')
        self._assert_encodes('ascii', 'foo bar')
        self._assert_encodes('ascii', 'foo \n ')

    def test_returns_expected_given_ISO8859(self):
        self._assert_encodes('iso-8859-1', '')
        self._assert_encodes('iso-8859-1', ' ')
        self._assert_encodes('iso-8859-1', '\n')
        self._assert_encodes('iso-8859-1', '\n ')
        self._assert_encodes('iso-8859-1', ' \n ')
        self._assert_encodes('iso-8859-1', 'foo bar')
        self._assert_encodes('iso-8859-1', 'foo \n ')

    def test_returns_expected_given_cp1252(self):
        self._assert_encodes('cp1252', '')
        self._assert_encodes('cp1252', ' ')
        self._assert_encodes('cp1252', '\n')
        self._assert_encodes('cp1252', '\n ')
        self._assert_encodes('cp1252', ' \n ')
        self._assert_encodes('cp1252', 'foo bar')
        self._assert_encodes('cp1252', 'foo \n ')

    def test_returns_expected_given_utf8(self):
        self._assert_encodes('utf-8', '')
        self._assert_encodes('utf-8', ' ')
        self._assert_encodes('utf-8', '\n')
        self._assert_encodes('utf-8', '\n ')
        self._assert_encodes('utf-8', ' \n ')
        self._assert_encodes('utf-8', 'foo bar')
        self._assert_encodes('utf-8', 'foo \n ')


class TestDetectEncoding(TestCase):
    def test_detects_ascii(self):
        sample = uu.abspath_testfile('magic_txt.txt')
        self.assertTrue(uu.file_exists(sample))
        actual = detect_encoding(sample)
        self.assertEqual(actual, 'ascii')

    @expectedFailure
    def test_detects_utf8(self):
        sample = uu.abspath_testfile('README.txt')
        self.assertTrue(uu.file_exists(sample))
        actual = detect_encoding(sample)
        self.assertEqual('utf-8', actual)

    def test_detects_encodings(self):
        testfile_encoding = get_sample_text_files(prefix='text_git_')
        self.assertGreater(len(testfile_encoding), 0)
        self.assertTrue(uu.file_exists(f) for f, _ in testfile_encoding)
        self.assertTrue(uu.is_internalstring(e)
                        for _, e in testfile_encoding)

        for testfile, expected_encoding in testfile_encoding:
            actual = detect_encoding(testfile).lower()

            # Two of the sample files are utf-8, remove trailing "_n".
            if expected_encoding in ('utf-8_1', 'utf-8_2'):
                expected_encoding = 'utf-8'

            if actual == 'windows-1252' and expected_encoding == 'utf16':
                # TODO: TODO: Improve auto-detecting encodings ..
                continue
            if actual == 'koi8-r' and expected_encoding == 'iso88591':
                # TODO: TODO: Improve auto-detecting encodings ..
                continue
            if actual == 'iso-8859-1' and expected_encoding == 'utf16':
                # TODO: TODO: Improve auto-detecting encodings ..
                continue

            self.assertEqual(actual, expected_encoding)

    @expectedFailure
    def test_returns_none_for_non_text_files(self):
        for test_file in ['magic_jpg.jpg', 'magic_png.png']:
            sample = uu.abspath_testfile(test_file)
            self.assertTrue(uu.file_exists(sample))
            actual = detect_encoding(sample)
            self.assertIsNone(actual)

    def test_returns_none_for_empty_files(self):
        sample = uu.abspath_testfile('empty')
        self.assertTrue(uu.file_exists(sample))
        actual = detect_encoding(sample)
        self.assertIsNone(actual)

    def test_returns_none_for_non_existing_files(self):
        sample = '/tmp/this_isnt_a_file_right_or_huh'
        self.assertFalse(uu.file_exists(sample))
        actual = detect_encoding(sample)
        self.assertIsNone(actual)


def get_sample_text_files(prefix, suffix='.txt'):
    """
    Returns:  A list of tuples; ('absolute_path', 'expected_encoding')
    """
    _sample_files = [
        f for f in uu.all_samplefiles()
        if os.path.basename(f).startswith(prefix)
        and os.path.basename(f).endswith(suffix)
    ]
    samplefile_expectedencoding = [
        (f, os.path.basename(f).replace(prefix, '').replace(suffix, ''))
        for f in _sample_files
    ]
    return samplefile_expectedencoding


class TestDetectsEncodingFromAlphaNumerics(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.testfile_encoding = get_sample_text_files(prefix='text_alnum_')

    def test_prerequisites(self):
        self.assertGreaterEqual(len(self.testfile_encoding), 0)
        self.assertTrue(uu.file_exists(f) for f, _ in self.testfile_encoding)
        self.assertTrue(uu.is_internalstring(e)
                        for _, e in self.testfile_encoding)

    @expectedFailure
    def test_detects_encodings(self):
        # TODO: Improve auto-detecting encodings ..')
        for testfile, expected_encoding in self.testfile_encoding:
            if expected_encoding == 'cp1252':
                # TODO: Improve encoding detection! (or not, for these samples)
                continue

            actual = detect_encoding(testfile)
            self.assertEqual(actual, expected_encoding)


class TestDetectsEncodingFromSampleText(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.testfile_encoding = get_sample_text_files(prefix='text_sample_')

    def test_prerequisites(self):
        self.assertGreater(len(self.testfile_encoding), 0)
        self.assertTrue(uu.file_exists(f) for f, _ in self.testfile_encoding)
        self.assertTrue(uu.is_internalstring(e,)
                        for _, e in self.testfile_encoding)

    def test_detects_encodings(self):
        for testfile, expected_encoding in self.testfile_encoding:
            actual = detect_encoding(testfile).lower()

            if actual == 'iso-8859-1' and expected_encoding == 'cp1252':
                # TODO: TODO: Improve auto-detecting encodings ..
                continue
            if (actual == 'iso-8859-2'
                    and expected_encoding in ('iso-8859-1', 'cp437', 'cp1252',
                                              'cp858', 'macroman')):
                # TODO: TODO: Improve auto-detecting encodings ..
                continue
            if (actual == 'windows-1252'
                    and expected_encoding in ('cp858', 'cp437', 'macroman')):
                # TODO: TODO: Improve auto-detecting encodings ..
                continue

            if actual == 'utf-16le' and expected_encoding == 'utf-16':
                # TODO: TODO: Improve auto-detecting encodings ..
                continue

            self.assertEqual(actual, expected_encoding)
