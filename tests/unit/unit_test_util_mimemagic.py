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

from core import types
from core.exceptions import EncodingBoundaryViolation
import unit.unit_utils as uu
from util import mimemagic


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
            actual = mimemagic.filetype(test_file)
            self.assertEqual(expected_mime, actual)

    def test_filetype_magic_with_invalid_args(self):
        actual = mimemagic.filetype(None)
        self.assertEqual(actual, types.NULL_AW_MIMETYPE)
        self.assertFalse(actual)


class TestEvalMagicGlob(TestCase):
    def _aF(self, mime_to_match, glob_list):
        actual = mimemagic.eval_glob(mime_to_match, glob_list)
        self.assertTrue(isinstance(actual, bool))
        self.assertFalse(actual)

    def _aT(self, mime_to_match, glob_list):
        actual = mimemagic.eval_glob(mime_to_match, glob_list)
        self.assertTrue(isinstance(actual, bool))
        self.assertTrue(actual)

    def test_eval_magic_blob_returns_false_given_bad_arguments(self):
        self.assertIsNotNone(mimemagic.eval_glob(None, None))
        self.assertFalse(mimemagic.eval_glob(None, None))

    def test_eval_magic_blob_raises_exception_given_bad_arguments(self):
        def _assert_raises(error, mime_to_match, glob_list):
            with self.assertRaises(error):
                mimemagic.eval_glob(mime_to_match, glob_list)

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
        self._aF('application/epub+zip', str(types.NULL_AW_MIMETYPE))
        self._aF('application/epub+zip', types.NULL_AW_MIMETYPE)

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
        self._aT(types.NULL_AW_MIMETYPE, '*/*')

    def test_unknown_mime_type_evaluates_true_for_any_glob(self):
        self._aT(types.NULL_AW_MIMETYPE, '*/*')
        self._aT(types.NULL_AW_MIMETYPE, ['*/*'])
        self._aT(types.NULL_AW_MIMETYPE, ['*/*', '*/jpeg'])

    def test_unknown_mime_type_evaluates_false(self):
        self._aF(types.NULL_AW_MIMETYPE, 'image/jpeg')
        self._aF(types.NULL_AW_MIMETYPE, ['image/jpeg'])
        self._aF(types.NULL_AW_MIMETYPE, ['application/*', '*/jpeg'])
        self._aF(None, 'image/jpeg')


class TestMimeExtensionMapper(TestCase):
    def setUp(self):
        self.m = mimemagic.MimeExtensionMapper()

    def _assert_returns_mimes(self, extension, expected):
        _actual_mimes = self.m.get_candidate_mimetypes(extension)
        self.assertTrue(isinstance(_actual_mimes, list))
        for expected_mime in expected:
            self.assertIn(expected_mime, _actual_mimes)

        self.assertEqual(len(expected), len(_actual_mimes))

    def _assert_returns_exts(self, mimetype, expected):
        _actual_exts = self.m.get_candidate_extensions(mimetype)
        self.assertTrue(isinstance(_actual_exts, list))
        for expected_ext in expected:
            self.assertIn(expected_ext, _actual_exts)

        self.assertEqual(len(expected), len(_actual_exts))

    def test_initially_empty(self):
        _mimes = self.m.get_candidate_mimetypes('rtf')
        self.assertEqual(_mimes, [])
        _exts = self.m.get_candidate_extensions('application/rtf')
        self.assertEqual(_exts, [])

    def test_add_extension_for_mime(self):
        self.m.add_mapping('application/rtf', 'rtf')

        _mimes = self.m.get_candidate_mimetypes('rtf')
        self.assertIn('application/rtf', _mimes)

        _exts = self.m.get_candidate_extensions('application/rtf')
        self.assertIn('rtf', _exts)

    def test_add_mime_for_extension(self):
        self.m.add_mapping('application/rtf', 'rtf')
        self._assert_returns_mimes('rtf', ['application/rtf'])
        self._assert_returns_exts('application/rtf', ['rtf'])

        self.m.add_mapping('text/rtf', 'rtf')
        self._assert_returns_mimes('rtf', ['application/rtf', 'text/rtf'])
        self._assert_returns_exts('application/rtf', ['rtf'])
        self._assert_returns_exts('text/rtf', ['rtf'])

    def test_get_candidate_mimetypes(self):
        self.m.add_mapping('text/x-shellscript', 'sh')
        self.m.add_mapping('text/x-sh', 'sh')
        self.m.add_mapping('text/shellscript', 'sh')

        self._assert_returns_mimes(
            'sh',
            ['text/shellscript', 'text/x-sh', 'text/x-shellscript']
        )

    def test_get_candidate_extensions(self):
        self.m.add_mapping('application/gzip', 'gz')
        self.m.add_mapping('application/gzip', 'tar.gz')

        self._assert_returns_exts('application/gzip', ['gz', 'tar.gz'])

    def test_get_preferred_extension(self):
        self.m.add_mapping('foo/bar', 'foo')
        self.m.add_mapping('foo/bar', 'foobar')

        self._assert_returns_exts('foo/bar', ['foo', 'foobar'])

        self.m.add_preferred_extension('foo/bar', 'baz')
        self._assert_returns_exts('foo/bar', ['baz', 'foo', 'foobar'])
        _preferred = self.m.get_extension('foo/bar')
        self.assertEqual(_preferred, 'baz')

    def test_get_extension(self):
        self.m.add_mapping('application/gzip', 'gz')
        self.m.add_mapping('application/gzip', 'tar.gz')

        _extension = self.m.get_extension('application/gzip')
        self.assertEqual(_extension, 'gz')


class TestMimemagicGetExtension(TestCase):
    def test_get_image_jpeg(self):
        self.assertEqual(mimemagic.get_extension('image/jpeg'), 'jpg')


class TestMimemagicGetMimetype(TestCase):
    def test_get_image_jpeg(self):
        self.assertEqual(mimemagic.get_mimetype('jpg'), 'image/jpeg')
        self.assertEqual(mimemagic.get_mimetype('jpeg'), 'image/jpeg')
