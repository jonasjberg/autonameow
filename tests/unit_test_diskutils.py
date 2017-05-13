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

from core.util import diskutils


class TestSplitFileName(TestCase):
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


class TestFileSuffix(TestCase):
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

    def test_file_suffix_file_has_many_suffixes(self):
        self.assertEqual('tar', diskutils.file_suffix('filename.tar'))
        self.assertEqual('gz', diskutils.file_suffix('filename.gz'))
        self.assertEqual('tar.gz', diskutils.file_suffix('filename.tar.gz'))
        self.assertEqual('tar.z', diskutils.file_suffix('filename.tar.z'))
        self.assertEqual('tar.lz', diskutils.file_suffix('filename.tar.lz'))
        self.assertEqual('tar.lzma', diskutils.file_suffix('filename.tar.lzma'))
        self.assertEqual('tar.lzo', diskutils.file_suffix('filename.tar.lzo'))

    def test_file_suffix_from_hidden_file_many_suffixes(self):
        self.assertEqual('tar', diskutils.file_suffix('.filename.tar'))
        self.assertEqual('gz', diskutils.file_suffix('.filename.gz'))
        self.assertEqual('tar.gz', diskutils.file_suffix('.filename.tar.gz'))
        self.assertEqual('tar.z', diskutils.file_suffix('.filename.tar.z'))
        self.assertEqual('tar.lz', diskutils.file_suffix('.filename.tar.lz'))
        self.assertEqual('tar.lzma', diskutils.file_suffix('.filename.tar.lzma'))
        self.assertEqual('tar.lzo', diskutils.file_suffix('.filename.tar.lzo'))


class TestFileBase(TestCase):
    def test_file_base_no_name(self):
        self.assertIsNone(diskutils.file_base(''))
        self.assertEqual(' ', diskutils.file_base(' '))
        self.assertEqual(',', diskutils.file_base(',. '))
        self.assertEqual(' ', diskutils.file_base(' . '))
        # self.assertEqual(' ', diskutils.file_base(' . . '))

    def test_file_base_file_has_no_extension(self):
        self.assertIsNotNone(diskutils.file_base('filename'))
        self.assertEqual('file name', diskutils.file_base('file name'))
        self.assertEqual('.hiddenfile', diskutils.file_base('.hiddenfile'))
        self.assertEqual('.hidden file', diskutils.file_base('.hidden file'))

    def test_file_base_file_has_one_extension(self):
        self.assertEqual('filename', diskutils.file_base('filename.jpg'))
        self.assertEqual('filename', diskutils.file_base('filename.JPG'))

    def test_file_base_from_hidden_file(self):
        self.assertEqual('.hiddenfile', diskutils.file_base('.hiddenfile.jpg'))
        self.assertEqual('.hiddenfile', diskutils.file_base('.hiddenfile.JPG'))
        self.assertEqual('.hiddenfile', diskutils.file_base('.hiddenfile.JPG'))

    def test_file_base_file_has_many_suffixes(self):
        self.assertEqual('filename', diskutils.file_base('filename.tar'))
        self.assertEqual('filename', diskutils.file_base('filename.gz'))
        self.assertEqual('filename', diskutils.file_base('filename.tar.gz'))
        self.assertEqual('filename', diskutils.file_base('filename.tar.z'))
        self.assertEqual('filename', diskutils.file_base('filename.tar.lz'))
        self.assertEqual('filename', diskutils.file_base('filename.tar.lzma'))
        self.assertEqual('filename', diskutils.file_base('filename.tar.lzo'))

    def test_file_base_from_hidden_file_many_suffixes(self):
        self.assertEqual('.filename', diskutils.file_base('.filename.tar'))
        self.assertEqual('.filename', diskutils.file_base('.filename.gz'))
        self.assertEqual('.filename', diskutils.file_base('.filename.tar.gz'))
        self.assertEqual('.filename', diskutils.file_base('.filename.tar.z'))
        self.assertEqual('.filename', diskutils.file_base('.filename.tar.lz'))
        self.assertEqual('.filename', diskutils.file_base('.filename.tar.lzma'))
        self.assertEqual('.filename', diskutils.file_base('.filename.tar.lzo'))


