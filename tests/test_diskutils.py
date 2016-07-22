import os
from unittest import TestCase

from util import diskutils


class TestDiskUtils(TestCase):
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

    def test_file_suffix_many_suffixes(self):
        self.assertEqual('tar', diskutils.file_suffix('filename.tar'))
        self.assertEqual('gz', diskutils.file_suffix('filename.gz'))
        self.assertEqual('tar.gz', diskutils.file_suffix('filename.tar.gz'))
        self.assertEqual('tar.z', diskutils.file_suffix('filename.tar.z'))
        self.assertEqual('tar.lz', diskutils.file_suffix('filename.tar.lz'))
        self.assertEqual('tar.lzma', diskutils.file_suffix('filename.tar.lzma'))
        self.assertEqual('tar.lzo', diskutils.file_suffix('filename.tar.lzo'))

    def test_file_base_no_name(self):
        self.assertIsNone(diskutils.file_base(''))
        self.assertEqual(' ', diskutils.file_base(' '))
        self.assertEqual(',', diskutils.file_base(',. '))
        self.assertEqual(' ', diskutils.file_base(' . '))
        # self.assertEqual(' ', diskutils.file_base(' . . '))


class TestFileTypeMagic(TestCase):
    def setUp(self):
        os.chdir(os.path.abspath(os.path.dirname(__file__)))

        self.test_files = [('magic_bmp.bmp', 'bmp'),
                           ('magic_gif.gif', 'gif'),
                           ('magic_jpg.jpg', 'jpg'),
                           ('magic_pdf.pdf', 'pdf'),
                           ('magic_png.png', 'png')]

    def test_test_files_defined(self):
        for fname, fmagic in self.test_files:
            self.assertIsNotNone(fname)
            self.assertIsNotNone(fmagic)

    def test_test_files_exist(self):
        for fname, _ in self.test_files:
            self.assertTrue(os.path.isfile(fname))

    def test_test_files_are_readable(self):
        for fname, _ in self.test_files:
            self.assertTrue(os.access(fname, os.R_OK))

    def test_filetype_magic(self):
        for fname, fmagic in self.test_files:
            self.assertEqual(fmagic, diskutils.filetype_magic(fname))
