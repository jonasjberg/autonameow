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
import unittest
from contextlib import contextmanager

from util import encoding as enc
import unit_utils as uu


class UtilTest(unittest.TestCase):
    def test_convert_command_args_keeps_undecodeable_bytes(self):
        arg = b'\x82'  # non-ascii bytes
        cmd_args = enc.convert_command_args([arg])

        self.assertEqual(cmd_args[0],
                         arg.decode(enc.arg_encoding(), 'surrogateescape'))


class PathConversionTest(uu.TestCase):
    def test_syspath_windows_format(self):
        with platform_windows():
            path = os.path.join('a', 'b', 'c')
            outpath = enc.syspath(path)
        self.assertTrue(uu.is_internalstring(outpath))
        self.assertTrue(outpath.startswith('\\\\?\\'))

    def test_syspath_windows_format_unc_path(self):
        # The \\?\ prefix on Windows behaves differently with UNC
        # (network share) paths.
        path = '\\\\server\\share\\file.mp3'
        with platform_windows():
            outpath = enc.syspath(path)
        self.assertTrue(uu.is_internalstring(outpath))
        self.assertEqual(outpath, '\\\\?\\UNC\\server\\share\\file.mp3')

    def test_syspath_posix_unchanged(self):
        with platform_posix():
            path = os.path.join('a', 'b', 'c')
            outpath = enc.syspath(path)
        self.assertEqual(path, outpath)

    def _windows_bytestring_path(self, path):
        old_gfse = sys.getfilesystemencoding
        sys.getfilesystemencoding = lambda: 'mbcs'
        try:
            with platform_windows():
                return enc.bytestring_path(path)
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


class TestByteStringPathWithInvalidInput(uu.TestCase):
    def test_bytestring_path_returns_expected_for_empty_input(self):
        self.assertEqual(b'', enc.bytestring_path(''))


class TestNormPath(uu.TestCase):
    def test_normpath_returns_expected_for_valid_input(self):
        self.assertNotEqual('/', enc.normpath('/'))
        self.assertNotEqual('/tmp', enc.normpath('/tmp/'))

    def test_normpath_raises_value_error_for_empty_input(self):
        with self.assertRaises(ValueError):
            enc.normpath('')
            self.assertNotEqual(b'', enc.normpath(''))


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

