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

from unittest import TestCase

from core import constants as C
from core import util
from core.exceptions import EncodingBoundaryViolation
import unit_utils as uu


class TestFileTypeMagic(TestCase):
    TEST_FILES = [('magic_bmp.bmp', 'image/x-ms-bmp'),
                  ('magic_gif.gif', 'image/gif'),
                  ('magic_jpg.jpg', 'image/jpeg'),
                  ('magic_mp4.mp4', 'video/mp4'),
                  ('magic_pdf.pdf', 'application/pdf'),
                  ('magic_png.png', 'image/png'),
                  ('magic_txt',     'text/plain'),
                  ('magic_txt.md',  'text/plain'),
                  ('magic_txt.txt', 'text/plain')]

    def setUp(self):
        self.test_files = [
            (uu.abspath_testfile(basename), expect_mime)
            for basename, expect_mime in self.TEST_FILES
        ]

    def test_test_files_exist_and_are_readable(self):
        for test_file, _ in self.test_files:
            self.assertTrue(uu.file_exists(test_file))
            self.assertTrue(uu.path_is_readable(test_file))

    def test_filetype_magic(self):
        for test_file, expected_mime in self.test_files:
            actual = util.magic.filetype(test_file)
            self.assertEqual(expected_mime, actual)

    def test_filetype_magic_with_invalid_args(self):
        self.assertEqual(util.magic.filetype(None),
                         C.MAGIC_TYPE_UNKNOWN)


class TestEvalMagicGlob(TestCase):
    def _aF(self, mime_to_match, glob_list):
        actual = util.magic.eval_glob(mime_to_match, glob_list)
        self.assertTrue(isinstance(actual, bool))
        self.assertFalse(actual)

    def _aT(self, mime_to_match, glob_list):
        actual = util.magic.eval_glob(mime_to_match, glob_list)
        self.assertTrue(isinstance(actual, bool))
        self.assertTrue(actual)

    def test_eval_magic_blob_is_defined(self):
        self.assertIsNotNone(util.magic.eval_glob)

    def test_eval_magic_blob_returns_false_given_bad_arguments(self):
        self.assertIsNotNone(util.magic.eval_glob(None, None))
        self.assertFalse(util.magic.eval_glob(None, None))

    def test_eval_magic_blob_raises_exception_given_bad_arguments(self):
        def _assert_raises(error, mime_to_match, glob_list):
            with self.assertRaises(error):
                util.magic.eval_glob(mime_to_match, glob_list)

        _assert_raises(ValueError, 'image/jpeg', ['*/*/jpeg'])
        _assert_raises(ValueError, 'application', ['*/*'])
        _assert_raises(TypeError, b'application', ['*/*'])
        _assert_raises(ValueError, '1', ['*/*'])
        _assert_raises(TypeError, b'1', ['*/*'])
        _assert_raises(EncodingBoundaryViolation,
                       'image/jpeg', [b'*/jpeg'])
        _assert_raises(EncodingBoundaryViolation,
                       'image/jpeg', [b'*/jpeg', 'image/*'])

        # TODO: Raising the encoding boundary exception here isn't right!
        _assert_raises(EncodingBoundaryViolation,
                       'image/jpeg', [1])
        _assert_raises(EncodingBoundaryViolation,
                       'image/jpeg', [1, 'image/jpeg'])

        _assert_raises(ValueError, 'application', ['*a'])
        _assert_raises(ValueError, 'application', ['a*'])

    def test_eval_magic_blob_returns_false_as_expected(self):
        self._aF('image/jpeg', [])
        self._aF('image/jpeg', [''])
        self._aF('image/jpeg', ['application/pdf'])
        self._aF('image/jpeg', ['*/pdf'])
        self._aF('image/jpeg', ['application/*'])
        self._aF('image/jpeg', ['image/pdf'])
        self._aF('image/jpeg', ['image/pdf', 'application/jpeg'])
        self._aF('image/jpeg', ['image/'])
        self._aF('image/jpeg', ['/jpeg'])
        self._aF('image/jpeg', ['*/pdf', '*/png'])
        self._aF('image/jpeg', ['*/pdf', '*/png', 'application/*'])
        self._aF('image/png', ['*/pdf', '*/jpg', 'application/*'])
        self._aF('image/png', ['*/pdf', '*/jpg', 'image/jpg'])
        self._aF('application/epub+zip', ['*/jpg'])
        self._aF('application/epub+zip', ['image/*'])
        self._aF('application/epub+zip', ['image/jpeg'])
        self._aF('application/epub+zip', 'video/*')
        self._aF('application/epub+zip', ['video/*'])
        self._aF('application/epub+zip', C.MAGIC_TYPE_UNKNOWN)

    def test_eval_magic_blob_returns_true_as_expected(self):
        self._aT('image/jpeg', '*/*')
        self._aT('image/jpeg', ['*/*'])
        self._aT('image/jpeg', '*/jpeg')
        self._aT('image/jpeg', ['*/jpeg'])
        self._aT('image/jpeg', ['image/*'])
        self._aT('image/png', ['image/*'])
        self._aT('image/jpeg', ['image/jpeg'])
        self._aT('image/jpeg', ['*/*', '*/jpeg'])
        self._aT('image/jpeg', ['image/*', '*/jpeg'])
        self._aT('image/png', ['*/pdf', '*/png', 'application/*'])
        self._aT('application/epub+zip', 'application/epub+zip')
        self._aT('application/epub+zip', ['application/epub+zip'])
        self._aT('application/epub+zip', ['application/*'])
        self._aT('application/epub+zip', ['*/epub+zip'])

    def test_unknown_mime_type_evaluates_true_for_any_glob(self):
        self._aT(C.MAGIC_TYPE_UNKNOWN, '*/*')
        self._aT(C.MAGIC_TYPE_UNKNOWN, ['*/*'])
        self._aT(C.MAGIC_TYPE_UNKNOWN, ['*/*', '*/jpeg'])

    def test_unknown_mime_type_evaluates_false(self):
        self._aF(C.MAGIC_TYPE_UNKNOWN, 'image/jpeg')
        self._aF(C.MAGIC_TYPE_UNKNOWN, ['image/jpeg'])
        self._aF(C.MAGIC_TYPE_UNKNOWN, ['application/*', '*/jpeg'])
