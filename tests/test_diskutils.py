from unittest import TestCase

from util import diskutils


class TestDiskUtils(TestCase):
    def test_file_suffix_no_name(self):
        self.assertEqual(None, diskutils.file_suffix(''))
        self.assertEqual(None, diskutils.file_suffix(' '))
        self.assertEqual(None, diskutils.file_suffix(',. '))
        self.assertEqual(None, diskutils.file_suffix(' . '))
        self.assertEqual(None, diskutils.file_suffix(' . . '))

    def test_file_suffix_file_has_no_extension(self):
        self.assertEqual(None, diskutils.file_suffix('filename'))
        self.assertEqual(None, diskutils.file_suffix('file name'))
        self.assertEqual(None, diskutils.file_suffix('.hiddenfile'))
        self.assertEqual(None, diskutils.file_suffix('.hidden file'))

    def test_file_suffix_from_hidden_file(self):
        self.assertEqual(None, diskutils.file_suffix('.hiddenfile'))
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
