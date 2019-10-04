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

from unittest import skipIf, TestCase

import unit.utils as uu
from util import checksum


# NOTE(jonas): Optionally add the absolute path to some big file here.
SAMPLEFILE_REALLY_BIG_FILE = 'TODO: Insert path to huge file here'

SAMPLEFILE_EMPTY = uu.samplefile_abspath('empty')
SAMPLEFILE_EMPTY_MD5 = 'd41d8cd98f00b204e9800998ecf8427e'
SAMPLEFILE_EMPTY_SHA1 = 'da39a3ee5e6b4b0d3255bfef95601890afd80709'
SAMPLEFILE_EMPTY_SHA256 = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'

SAMPLEFILE_MAGICTXT = uu.samplefile_abspath('magic_txt.txt')
SAMPLEFILE_MAGICTXT_MD5 = 'e1cbb0c3879af8347246f12c559a86b5'
SAMPLEFILE_MAGICTXT_SHA1 = 'aa785adca3fcdfe1884ae840e13c6d294a2414e8'
SAMPLEFILE_MAGICTXT_SHA256 = 'b9e68e1bea3e5b19ca6b2f98b73a54b73daafaa250484902e09982e07a12e733'

SAMPLEFILE_MAGICPNG = uu.samplefile_abspath('magic_png.png')
SAMPLEFILE_MAGICPNG_MD5 = '995b55fce80c125771c40a42a297b4ea'
SAMPLEFILE_MAGICPNG_SHA1 = '63679a1a5a1f177effbc58cf1cd0dfabc5bd5120'
SAMPLEFILE_MAGICPNG_SHA256 = '9c138627d827a2efd5ab835098ea3363cc8e13ec6d1745b94663b41e810a6448'


REALLY_BIG_SAMPLEFILE_UNAVAILABLE = (
    not (uu.file_exists(SAMPLEFILE_REALLY_BIG_FILE)
         and uu.path_is_readable(SAMPLEFILE_REALLY_BIG_FILE)),
    'SAMPLEFILE_REALLY_BIG_FILE is not set'
)


class TestHashlibDigest(TestCase):
    def test_raises_assertion_error_given_bad_algorithm(self):
        def _aR(algorithm):
            with self.assertRaises(AssertionError):
                _ = checksum.hashlib_digest(SAMPLEFILE_MAGICTXT, algorithm)

        _aR('')
        _aR('sha529')
        _aR('mja003')

    def test_raises_filesystem_error_given_bad_file(self):
        from core.exceptions import FilesystemError

        for bad_file in [
            None,
            object(),
            '',
            b''
        ]:
            with self.assertRaises(FilesystemError):
                _ = checksum.hashlib_digest(bad_file)


class TestSha256Digest(TestCase):
    def test_returns_expected(self):
        a = checksum.sha256digest(SAMPLEFILE_MAGICTXT)
        self.assertEqual(a, SAMPLEFILE_MAGICTXT_SHA256)

        b = checksum.sha256digest(SAMPLEFILE_MAGICPNG)
        self.assertEqual(b, SAMPLEFILE_MAGICPNG_SHA256)

        c = checksum.sha256digest(SAMPLEFILE_EMPTY)
        self.assertEqual(c, SAMPLEFILE_EMPTY_SHA256)

    def test_returns_expected_type(self):
        a = checksum.sha256digest(SAMPLEFILE_MAGICTXT)
        self.assertTrue(uu.is_internalstring(a))

        b = checksum.sha256digest(SAMPLEFILE_MAGICPNG)
        self.assertTrue(uu.is_internalstring(b))

        c = checksum.sha256digest(SAMPLEFILE_EMPTY)
        self.assertTrue(uu.is_internalstring(c))

    def test_returns_unique_values(self):
        a = checksum.sha256digest(SAMPLEFILE_MAGICTXT)
        b = checksum.sha256digest(SAMPLEFILE_MAGICPNG)
        c = checksum.sha256digest(SAMPLEFILE_EMPTY)

        self.assertNotEqual(a, b)
        self.assertNotEqual(a, c)
        self.assertNotEqual(b, c)

    @skipIf(*REALLY_BIG_SAMPLEFILE_UNAVAILABLE)
    def test_big_file(self):
        a = checksum.sha256digest(SAMPLEFILE_REALLY_BIG_FILE)
        self.assertTrue(uu.is_internalstring(a))


class TestSha1Digest(TestCase):
    def test_returns_expected(self):
        a = checksum.sha1digest(SAMPLEFILE_MAGICTXT)
        self.assertEqual(a, SAMPLEFILE_MAGICTXT_SHA1)

        b = checksum.sha1digest(SAMPLEFILE_MAGICPNG)
        self.assertEqual(b, SAMPLEFILE_MAGICPNG_SHA1)

        c = checksum.sha1digest(SAMPLEFILE_EMPTY)
        self.assertEqual(c, SAMPLEFILE_EMPTY_SHA1)

    def test_returns_expected_type(self):
        a = checksum.sha1digest(SAMPLEFILE_MAGICTXT)
        self.assertTrue(uu.is_internalstring(a))

        b = checksum.sha1digest(SAMPLEFILE_MAGICPNG)
        self.assertTrue(uu.is_internalstring(b))

        c = checksum.sha1digest(SAMPLEFILE_EMPTY)
        self.assertTrue(uu.is_internalstring(c))

    def test_returns_unique_values(self):
        a = checksum.sha1digest(SAMPLEFILE_MAGICTXT)
        b = checksum.sha1digest(SAMPLEFILE_MAGICPNG)
        c = checksum.sha1digest(SAMPLEFILE_EMPTY)

        self.assertNotEqual(a, b)
        self.assertNotEqual(a, c)
        self.assertNotEqual(b, c)

    @skipIf(*REALLY_BIG_SAMPLEFILE_UNAVAILABLE)
    def test_big_file(self):
        a = checksum.sha1digest(SAMPLEFILE_REALLY_BIG_FILE)
        self.assertTrue(uu.is_internalstring(a))


class TestMD5Digest(TestCase):
    def test_returns_expected(self):
        a = checksum.md5digest(SAMPLEFILE_MAGICTXT)
        self.assertEqual(a, SAMPLEFILE_MAGICTXT_MD5)

        b = checksum.md5digest(SAMPLEFILE_MAGICPNG)
        self.assertEqual(b, SAMPLEFILE_MAGICPNG_MD5)

        c = checksum.md5digest(SAMPLEFILE_EMPTY)
        self.assertEqual(c, SAMPLEFILE_EMPTY_MD5)

    def test_returns_expected_type(self):
        a = checksum.md5digest(SAMPLEFILE_MAGICTXT)
        self.assertTrue(uu.is_internalstring(a))

        b = checksum.md5digest(SAMPLEFILE_MAGICPNG)
        self.assertTrue(uu.is_internalstring(b))

        c = checksum.md5digest(SAMPLEFILE_EMPTY)
        self.assertTrue(uu.is_internalstring(c))

    def test_returns_unique_values(self):
        a = checksum.md5digest(SAMPLEFILE_MAGICTXT)
        b = checksum.md5digest(SAMPLEFILE_MAGICPNG)
        c = checksum.md5digest(SAMPLEFILE_EMPTY)

        self.assertNotEqual(a, b)
        self.assertNotEqual(a, c)
        self.assertNotEqual(b, c)

    @skipIf(*REALLY_BIG_SAMPLEFILE_UNAVAILABLE)
    def test_big_file(self):
        a = checksum.md5digest(SAMPLEFILE_REALLY_BIG_FILE)
        self.assertTrue(uu.is_internalstring(a))


class TestPartialSha256Digest(TestCase):
    def test_returns_expected(self):
        a = checksum.partial_sha256digest(SAMPLEFILE_MAGICTXT)
        self.assertEqual(a, SAMPLEFILE_MAGICTXT_SHA256)

        b = checksum.partial_sha256digest(SAMPLEFILE_MAGICPNG)
        self.assertEqual(b, SAMPLEFILE_MAGICPNG_SHA256)

        c = checksum.partial_sha256digest(SAMPLEFILE_EMPTY)
        self.assertEqual(c, SAMPLEFILE_EMPTY_SHA256)

    def test_returns_expected_type(self):
        a = checksum.partial_sha256digest(SAMPLEFILE_MAGICTXT)
        self.assertTrue(uu.is_internalstring(a))

        b = checksum.partial_sha256digest(SAMPLEFILE_MAGICPNG)
        self.assertTrue(uu.is_internalstring(b))

        c = checksum.partial_sha256digest(SAMPLEFILE_EMPTY)
        self.assertTrue(uu.is_internalstring(c))

    def test_returns_unique_values(self):
        a = checksum.partial_sha256digest(SAMPLEFILE_MAGICTXT)
        b = checksum.partial_sha256digest(SAMPLEFILE_MAGICPNG)
        c = checksum.partial_sha256digest(SAMPLEFILE_EMPTY)

        self.assertNotEqual(a, b)
        self.assertNotEqual(a, c)
        self.assertNotEqual(b, c)

    @skipIf(*REALLY_BIG_SAMPLEFILE_UNAVAILABLE)
    def test_big_file(self):
        a = checksum.partial_sha256digest(SAMPLEFILE_REALLY_BIG_FILE)
        self.assertTrue(uu.is_internalstring(a))


class TestPartialSha1Digest(TestCase):
    def test_returns_expected(self):
        a = checksum.partial_sha1digest(SAMPLEFILE_MAGICTXT)
        self.assertEqual(a, SAMPLEFILE_MAGICTXT_SHA1)

        b = checksum.partial_sha1digest(SAMPLEFILE_MAGICPNG)
        self.assertEqual(b, SAMPLEFILE_MAGICPNG_SHA1)

        c = checksum.partial_sha1digest(SAMPLEFILE_EMPTY)
        self.assertEqual(c, SAMPLEFILE_EMPTY_SHA1)

    def test_returns_expected_type(self):
        a = checksum.partial_sha1digest(SAMPLEFILE_MAGICTXT)
        self.assertTrue(uu.is_internalstring(a))

        b = checksum.partial_sha1digest(SAMPLEFILE_MAGICPNG)
        self.assertTrue(uu.is_internalstring(b))

        c = checksum.partial_sha1digest(SAMPLEFILE_EMPTY)
        self.assertTrue(uu.is_internalstring(c))

    def test_returns_unique_values(self):
        a = checksum.partial_sha1digest(SAMPLEFILE_MAGICTXT)
        b = checksum.partial_sha1digest(SAMPLEFILE_MAGICPNG)
        c = checksum.partial_sha1digest(SAMPLEFILE_EMPTY)

        self.assertNotEqual(a, b)
        self.assertNotEqual(a, c)
        self.assertNotEqual(b, c)

    @skipIf(*REALLY_BIG_SAMPLEFILE_UNAVAILABLE)
    def test_big_file(self):
        a = checksum.partial_sha1digest(SAMPLEFILE_REALLY_BIG_FILE)
        self.assertTrue(uu.is_internalstring(a))


class TestPartialMD5Digest(TestCase):
    def test_returns_expected(self):
        a = checksum.partial_md5digest(SAMPLEFILE_MAGICTXT)
        self.assertEqual(a, SAMPLEFILE_MAGICTXT_MD5)

        b = checksum.partial_md5digest(SAMPLEFILE_MAGICPNG)
        self.assertEqual(b, SAMPLEFILE_MAGICPNG_MD5)

        c = checksum.partial_md5digest(SAMPLEFILE_EMPTY)
        self.assertEqual(c, SAMPLEFILE_EMPTY_MD5)

    def test_returns_expected_type(self):
        a = checksum.partial_md5digest(SAMPLEFILE_MAGICTXT)
        self.assertTrue(uu.is_internalstring(a))

        b = checksum.partial_md5digest(SAMPLEFILE_MAGICPNG)
        self.assertTrue(uu.is_internalstring(b))

        c = checksum.partial_md5digest(SAMPLEFILE_EMPTY)
        self.assertTrue(uu.is_internalstring(c))

    def test_returns_unique_values(self):
        a = checksum.partial_md5digest(SAMPLEFILE_MAGICTXT)
        b = checksum.partial_md5digest(SAMPLEFILE_MAGICPNG)
        c = checksum.partial_md5digest(SAMPLEFILE_EMPTY)

        self.assertNotEqual(a, b)
        self.assertNotEqual(a, c)
        self.assertNotEqual(b, c)

    @skipIf(*REALLY_BIG_SAMPLEFILE_UNAVAILABLE)
    def test_big_file(self):
        a = checksum.partial_md5digest(SAMPLEFILE_REALLY_BIG_FILE)
        self.assertTrue(uu.is_internalstring(a))
