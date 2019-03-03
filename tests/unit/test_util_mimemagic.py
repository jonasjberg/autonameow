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

from unittest import TestCase

import unit.utils as uu
from util import coercers
from util.mimemagic import eval_glob
from util.mimemagic import file_mimetype
from util.mimemagic import get_extension
from util.mimemagic import get_mimetype
from util.mimemagic import MimeExtensionMapper


class TestFileMimetype(TestCase):
    TESTFILE_BASENAME_EXPECTED_MIMETYPE = [
        ('magic_bmp.bmp', 'image/x-ms-bmp'),
        ('magic_gif.gif', 'image/gif'),
        ('magic_jpg.jpg', 'image/jpeg'),
        ('magic_mp4.mp4', 'video/mp4'),
        ('magic_pdf.pdf', 'application/pdf'),
        ('magic_png.png', 'image/png'),
        ('magic_txt',     'text/plain'),
        ('magic_txt.md',  'text/plain'),
        ('magic_txt.txt', 'text/plain')
    ]

    @classmethod
    def setUpClass(cls):
        cls.null_mimetype = coercers.NULL_AW_MIMETYPE
        cls.FILEPATH_EXPECTED = [
            (uu.abspath_testfile(basename), mimetype)
            for basename, mimetype in cls.TESTFILE_BASENAME_EXPECTED_MIMETYPE
        ]

    def test_test_files_exist_and_are_readable(self):
        for filepath, _ in self.FILEPATH_EXPECTED:
            self.assertTrue(uu.file_exists(filepath))
            self.assertTrue(uu.path_is_readable(filepath))

    def test_sanity_check_that_expected_mime_types_contain_a_slash(self):
        for _, expected_mime in self.FILEPATH_EXPECTED:
            self.assertIn('/', expected_mime)

    def test_file_mimetype_returns_expected_mime_types_given_test_files(self):
        for filepath, expected_mime in self.FILEPATH_EXPECTED:
            actual = file_mimetype(filepath)
            self.assertEqual(expected_mime, actual)

    def test_file_mimetype_returns_expected_null_mime_type_given_bad_args(self):
        for invalid_filepath in [
            None,
            '',
            b''
        ]:
            actual = file_mimetype(invalid_filepath)
            self.assertEqual(self.null_mimetype, actual)
            self.assertFalse(actual)


class TestEvalMagicGlob(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.null_mimetype = coercers.NULL_AW_MIMETYPE

    def _aF(self, mime_to_match, glob_list):
        actual = eval_glob(mime_to_match, glob_list)
        self.assertIsInstance(actual, bool)
        self.assertFalse(actual)

    def _aT(self, mime_to_match, glob_list):
        actual = eval_glob(mime_to_match, glob_list)
        self.assertIsInstance(actual, bool)
        self.assertTrue(actual)

    def test_eval_magic_blob_returns_false_given_bad_arguments(self):
        self.assertIsNotNone(eval_glob(None, None))
        self.assertFalse(eval_glob(None, None))

    def test_eval_magic_blob_raises_exception_given_bad_arguments(self):
        def _assert_raises(error, mime_to_match, glob_list):
            with self.assertRaises(error):
                eval_glob(mime_to_match, glob_list)

        _assert_raises(ValueError, 'image/jpeg', ['*/*/jpeg'])
        _assert_raises(ValueError, 'application', ['*/*'])
        _assert_raises(TypeError, b'application', ['*/*'])
        _assert_raises(ValueError, '1', ['*/*'])
        _assert_raises(TypeError, b'1', ['*/*'])
        _assert_raises(AssertionError,
                       'image/jpeg', [b'*/jpeg'])
        _assert_raises(AssertionError,
                       'image/jpeg', [b'*/jpeg', 'image/*'])

        # TODO: Raising the encoding boundary exception here isn't right!
        _assert_raises(AssertionError,
                       'image/jpeg', [1])
        _assert_raises(AssertionError,
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
        self._aF('application/epub+zip', str(self.null_mimetype))
        self._aF('application/epub+zip', self.null_mimetype)

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
        self._aT(self.null_mimetype, '*/*')

    def test_unknown_mime_type_evaluates_true_for_any_glob(self):
        self._aT(self.null_mimetype, '*/*')
        self._aT(self.null_mimetype, ['*/*'])
        self._aT(self.null_mimetype, ['*/*', '*/jpeg'])

    def test_unknown_mime_type_evaluates_false(self):
        self._aF(self.null_mimetype, 'image/jpeg')
        self._aF(self.null_mimetype, ['image/jpeg'])
        self._aF(self.null_mimetype, ['application/*', '*/jpeg'])
        self._aF(None, 'image/jpeg')


class TestMimeExtensionMapper(TestCase):
    def setUp(self):
        self.m = MimeExtensionMapper()

    def _assert_returns_candidate_mimes(self, given, expect):
        _actual = self.m.get_candidate_mimetypes(given)

        self.assertIsInstance(_actual, list)
        for expected_mime in expect:
            self.assertIn(expected_mime, _actual)

        self.assertEqual(len(expect), len(_actual))

    def _assert_returns_candidate_extensions(self, given, expect):
        _actual = self.m.get_candidate_extensions(given)

        self.assertIsInstance(_actual, list)
        for expected_ext in expect:
            self.assertIn(expected_ext, _actual)

        self.assertEqual(len(expect), len(_actual))

    def test_initially_empty(self):
        _mimes = self.m.get_candidate_mimetypes('rtf')
        expected = list()
        self.assertEqual(expected, _mimes)
        _exts = self.m.get_candidate_extensions('application/rtf')
        self.assertEqual(expected, _exts)

    def test_add_extension_for_mime(self):
        self.m.add_mapping('application/rtf', 'rtf')

        _mimes = self.m.get_candidate_mimetypes('rtf')
        self.assertIn('application/rtf', _mimes)

        _exts = self.m.get_candidate_extensions('application/rtf')
        self.assertIn('rtf', _exts)

    def test_add_mime_for_extension(self):
        self.m.add_mapping('application/rtf', 'rtf')
        self._assert_returns_candidate_mimes(
            given='rtf',
            expect=['application/rtf']
        )
        self._assert_returns_candidate_extensions(
            given='application/rtf',
            expect=['rtf']
        )

        self.m.add_mapping('text/rtf', 'rtf')
        self._assert_returns_candidate_mimes(
            given='rtf',
            expect=['application/rtf', 'text/rtf']
        )
        self._assert_returns_candidate_extensions(
            given='application/rtf',
            expect=['rtf']
        )
        self._assert_returns_candidate_extensions(
            given='text/rtf',
            expect=['rtf']
        )

    def test_get_candidate_mimetypes(self):
        self.m.add_mapping('text/x-shellscript', 'sh')
        self.m.add_mapping('text/x-sh', 'sh')
        self.m.add_mapping('text/shellscript', 'sh')
        self._assert_returns_candidate_mimes(
            given='sh',
            expect=['text/shellscript', 'text/x-sh', 'text/x-shellscript']
        )

    def test_get_candidate_mimetypes_for_empty_extension(self):
        self._assert_returns_candidate_mimes(
            given='',
            expect=[]
        )
        self.m.add_mapping('inode/x-empty', '')
        self._assert_returns_candidate_mimes(
            given='',
            expect=['inode/x-empty']
        )

    def test_get_candidate_extensions(self):
        self.m.add_mapping('application/gzip', 'gz')
        self.m.add_mapping('application/gzip', 'tar.gz')

        self._assert_returns_candidate_extensions(
            given='application/gzip',
            expect=['gz', 'tar.gz']
        )

    def test_get_preferred_extension(self):
        self.m.add_mapping('foo/bar', 'foo')
        self.m.add_mapping('foo/bar', 'foobar')

        self._assert_returns_candidate_extensions(
            given='foo/bar',
            expect=['foo', 'foobar']
        )

        self.m.add_preferred_extension('foo/bar', 'baz')
        self._assert_returns_candidate_extensions(
            given='foo/bar',
            expect=['baz', 'foo', 'foobar']
        )
        _preferred = self.m.get_extension('foo/bar')
        self.assertEqual('baz', _preferred)

    def test_get_extension(self):
        self.m.add_mapping('application/gzip', 'gz')
        self.m.add_mapping('application/gzip', 'tar.gz')

        _extension = self.m.get_extension('application/gzip')
        self.assertEqual('gz', _extension)


class TestMimemagicGetExtension(TestCase):
    def _assert_returns_extension(self, expect, given):
        actual = get_extension(given)
        self.assertEqual(expect, actual)

    def test_maps_mime_type_image_jpeg_to_extension_jpg(self):
        self._assert_returns_extension('jpg', given='image/jpeg')

    def test_maps_mime_type_image_png_to_extension_png(self):
        self._assert_returns_extension('png', given='image/png')

    def test_maps_mime_type_text_x_sh_and_x_shellscript_to_extension_sh(self):
        self._assert_returns_extension('sh', given='text/x-shellscript')
        self._assert_returns_extension('sh', given='text/x-sh')

    def test_maps_mime_type_application_x_iso9660_image_to_extension_dmg(self):
        self._assert_returns_extension('dmg', given='application/x-iso9660-image')

    def test_maps_opendocument_mime_types_to_expected_extensions(self):
        self._assert_returns_extension('odp', given='application/vnd.oasis.opendocument.presentation')
        self._assert_returns_extension('ods', given='application/vnd.oasis.opendocument.spreadsheet')
        self._assert_returns_extension('odt', given='application/vnd.oasis.opendocument.text')
        self._assert_returns_extension('xlsx', given='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    def test_maps_photoshop_mime_types_to_expected_extensions(self):
        self._assert_returns_extension('psd', given='image/vnd.adobe.photoshop')

    def test_maps_mime_type_application_x_dvi_to_extension_dvi(self):
        self._assert_returns_extension('dvi', given='application/x-dvi')

    def test_maps_mime_type_application_vnd_ms_excel_to_extension_xls(self):
        self._assert_returns_extension('xls', given='application/vnd.ms-excel')

    def test_maps_mime_type_application_x_dosexec_to_extension_exe(self):
        self._assert_returns_extension('exe', given='application/x-dosexec')

    def test_maps_mime_type_application_vnd_debian_binary_package_to_extension_deb(self):
        self._assert_returns_extension('deb', given='application/vnd.debian.binary-package')

    def test_maps_mime_type_mime_type_video_x_ms_asf_to_extension_wma(self):
        self._assert_returns_extension('wma', given='video/x-ms-asf')

    def test_maps_mime_type_audio_x_wav_to_extension_wav(self):
        self._assert_returns_extension('wav', given='audio/x-wav')

    def test_maps_mime_type_application_x_mobipocket_ebook_to_extension_azw3(self):
        self._assert_returns_extension('azw3', given='application/x-mobipocket-ebook')

    def test_maps_mime_type_video_ogg_to_extension_ogv(self):
        self._assert_returns_extension('ogv', given='video/ogg')

    def test_maps_mime_type_video_x_ogg_to_extension_ogv(self):
        self._assert_returns_extension('ogv', given='video/x-ogg')


class TestMimemagicGetMimetype(TestCase):
    def _assert_returns_mime(self, expect, given):
        actual = get_mimetype(given)
        self.assertEqual(expect, actual)

    def test_unknown_mime_type(self):
        unknown_mimetype = coercers.NULL_AW_MIMETYPE
        for invalid_extension in [None, '', ' ', '  ', 'me0ww']:
            self._assert_returns_mime(unknown_mimetype, given=invalid_extension)

    def test_maps_extensions_jpg_and_jpeg_to_mime_type_image_jpeg(self):
        self._assert_returns_mime('image/jpeg', given='jpg')
        self._assert_returns_mime('image/jpeg', given='jpeg')

    def test_maps_extension_png_to_mime_type_image_png(self):
        self._assert_returns_mime('image/png', given='png')

    def test_maps_extensions_sh_and_bash_to_mime_type_text_x_shellscript(self):
        self._assert_returns_mime('text/x-shellscript', given='sh')
        self._assert_returns_mime('text/x-shellscript', given='bash')

    def test_maps_extension_java_to_mime_type_text_x_java(self):
        self._assert_returns_mime('text/x-java', given='java')

    def test_maps_extension_dmg_to_mime_type_application_x_iso9660_image(self):
        self._assert_returns_mime('application/x-iso9660-image', given='dmg')

    def test_maps_extensions_opendocument_mime_types(self):
        self._assert_returns_mime('application/vnd.oasis.opendocument.presentation', given='odp')
        self._assert_returns_mime('application/vnd.oasis.opendocument.spreadsheet', given='ods')
        self._assert_returns_mime('application/vnd.oasis.opendocument.text', given='odt')
        self._assert_returns_mime('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', given='xlsx')

    def test_maps_extensions_photoshop_mime_types(self):
        self._assert_returns_mime('image/vnd.adobe.photoshop', given='psd')

    def test_maps_extension_dvi_to_mime_type_application_x_dvi(self):
        self._assert_returns_mime('application/x-dvi', given='dvi')

    def test_maps_extensions_microsoft_office_mime_types(self):
        self._assert_returns_mime('application/vnd.ms-excel', given='xls')

    def test_maps_extension_deb_to_mime_type_application_vnd_debian_binary_package(self):
        self._assert_returns_mime('application/vnd.debian.binary-package', 'deb')

    def test_maps_extension_wma_to_mime_type_video_x_ms_asf(self):
        self._assert_returns_mime('video/x-ms-asf', 'wma')

    def test_maps_extension_wav_to_mime_type_audio_x_wav(self):
        self._assert_returns_mime('audio/x-wav', 'wav')

    def test_maps_extension_azw3_to_mime_type_application_x_mobipocket_ebook(self):
        self._assert_returns_mime('application/x-mobipocket-ebook', 'azw3')

    def test_maps_extension_ogv_to_mime_type_video_ogg(self):
        self._assert_returns_mime('video/ogg', 'ogv')

    def test_maps_extension_ogv_to_mime_type_video_x_ogg(self):
        self._assert_returns_mime('video/x-ogg', 'ogv')
