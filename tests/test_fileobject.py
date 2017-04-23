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

from core.fileobject import FileObject


class TestFileObjectFilenamePartitioningLongNameNoTags(TestCase):
    def setUp(self):
        self.fo = FileObject('20160722 Descriptive name.txt')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)
        self.assertEqual('20160722 Descriptive name', self.fo.fnbase)

    def test__filenamepart_ts(self):
        self.assertIsNotNone(self.fo.filenamepart_ts)
        self.assertEqual('20160722', self.fo.filenamepart_ts)

    def test__filenamepart_base(self):
        self.assertIsNotNone(self.fo.filenamepart_base)
        self.assertEqual('Descriptive name',
                         self.fo.filenamepart_base)

    def test__filenamepart_ext(self):
        self.assertIsNotNone(self.fo.filenamepart_ext)
        self.assertNotEqual(' ', self.fo.filenamepart_ext)
        self.assertNotEqual('', self.fo.filenamepart_ext)
        self.assertNotEqual('jpg', self.fo.filenamepart_ext)
        self.assertEqual('txt', self.fo.filenamepart_ext)

    def test__filenamepart_tags(self):
        self.assertEqual([], self.fo.filenamepart_tags)


class TestFileObjectFilenamePartitioningLongNameWithTags(TestCase):
    def setUp(self):
        self.fo = FileObject('19990212 Descriptive name -- firsttag tagtwo.txt')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)
        self.assertEqual('19990212 Descriptive name -- firsttag tagtwo',
                         self.fo.fnbase)

    def test__filenamepart_ts(self):
        self.assertIsNotNone(self.fo.filenamepart_ts)
        self.assertEqual('19990212', self.fo.filenamepart_ts)

    def test__filenamepart_base(self):
        self.assertIsNotNone(self.fo.filenamepart_base)
        self.assertEqual('Descriptive name', self.fo.filenamepart_base)

    def test__filenamepart_ext(self):
        self.assertIsNotNone(self.fo.filenamepart_ext)
        self.assertNotEqual(' ', self.fo.filenamepart_ext)
        self.assertNotEqual('', self.fo.filenamepart_ext)
        self.assertNotEqual('jpg', self.fo.filenamepart_ext)
        self.assertEqual('txt', self.fo.filenamepart_ext)

    def test__filenamepart_tags(self):
        self.assertIsNotNone(self.fo.filenamepart_tags)
        self.assertNotEqual(['firsttag'], self.fo.filenamepart_tags)
        self.assertNotEqual(['tagtwo'], self.fo.filenamepart_tags)
        self.assertEqual(['firsttag', 'tagtwo'], self.fo.filenamepart_tags)


class TestFileObjectFilenamePartitioningLongNameWithTagsDashesInName(TestCase):
    def setUp(self):
        self.fo = FileObject('19920722 --Descriptive-- name -- firsttag tagtwo.txt')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)
        self.assertEqual('19920722 --Descriptive-- name -- firsttag tagtwo',
                         self.fo.fnbase)

    def test__filenamepart_ts(self):
        self.assertIsNotNone(self.fo.filenamepart_ts)
        self.assertEqual('19920722', self.fo.filenamepart_ts)

    def test__filenamepart_base(self):
        self.assertIsNotNone(self.fo.filenamepart_base)
        self.assertEqual('--Descriptive-- name', self.fo.filenamepart_base)

    def test__filenamepart_ext(self):
        self.assertIsNotNone(self.fo.filenamepart_ext)
        self.assertNotEqual(' ', self.fo.filenamepart_ext)
        self.assertNotEqual('', self.fo.filenamepart_ext)
        self.assertNotEqual('jpg', self.fo.filenamepart_ext)
        self.assertEqual('txt', self.fo.filenamepart_ext)

    def test__filenamepart_tags(self):
        self.assertIsNotNone(self.fo.filenamepart_tags)
        self.assertNotEqual(['firsttag'], self.fo.filenamepart_tags)
        self.assertNotEqual(['tagtwo'], self.fo.filenamepart_tags)
        self.assertEqual(['firsttag', 'tagtwo'], self.fo.filenamepart_tags)


class TestFileObjectFilenamePartitioningHiddenFileNoExtensionNoTags(TestCase):
    def setUp(self):
        self.fo = FileObject('.name')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)
        self.assertEqual('.name', self.fo.fnbase)

    def test__filenamepart_ts(self):
        self.assertIsNone(self.fo.filenamepart_ts)

    def test__filenamepart_base(self):
        self.assertIsNotNone(self.fo.filenamepart_base)
        self.assertEqual('.name', self.fo.filenamepart_base)

    def test__filenamepart_ext(self):
        self.assertIsNone(self.fo.filenamepart_ext)

    def test__filenamepart_tags(self):
        self.assertEqual([], self.fo.filenamepart_tags)


class TestFileObjectFilenamePartitioningHiddenFileNoTags(TestCase):
    def setUp(self):
        self.fo = FileObject('.name.jpg')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)
        self.assertEqual('.name', self.fo.fnbase)

    def test__filenamepart_ts(self):
        self.assertIsNone(self.fo.filenamepart_ts)

    def test__filenamepart_base(self):
        self.assertIsNotNone(self.fo.filenamepart_base)
        self.assertEqual('.name', self.fo.filenamepart_base)

    def test__filenamepart_ext(self):
        self.assertIsNotNone(self.fo.filenamepart_ext)
        self.assertNotEqual(' ', self.fo.filenamepart_ext)
        self.assertNotEqual('', self.fo.filenamepart_ext)
        self.assertNotEqual('bla', self.fo.filenamepart_ext)
        self.assertEqual('jpg', self.fo.filenamepart_ext)

    def test__filenamepart_tags(self):
        self.assertEqual([], self.fo.filenamepart_tags)


class TestFileObjectFilenamePartitioningHiddenFileCompoundSuffix(TestCase):
    def setUp(self):
        self.fo = FileObject('.name.tar.gz')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)
        # self.assertEqual('.name.tar', self.fo.basename_no_ext)

    def test__filenamepart_ts(self):
        self.assertIsNone(self.fo.filenamepart_ts)

    def test__filenamepart_base(self):
        self.assertIsNotNone(self.fo.filenamepart_base)
        self.assertEqual('.name', self.fo.filenamepart_base)

    def test__filenamepart_ext(self):
        self.assertIsNotNone(self.fo.filenamepart_ext)
        self.assertNotEqual(' ', self.fo.filenamepart_ext)
        self.assertNotEqual('', self.fo.filenamepart_ext)
        self.assertNotEqual('tar', self.fo.filenamepart_ext)
        self.assertNotEqual('gz', self.fo.filenamepart_ext)
        self.assertEqual('tar.gz', self.fo.filenamepart_ext)

    def test__filenamepart_tags(self):
        self.assertEqual([], self.fo.filenamepart_tags)


class TestFileObjectFilenamePartitioningHiddenFileWithTags(TestCase):
    def setUp(self):
        self.fo = FileObject('.name -- firsttag 2ndtag.jpg')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)
        self.assertEqual('.name -- firsttag 2ndtag', self.fo.fnbase)

    def test__filenamepart_ts(self):
        self.assertIsNone(self.fo.filenamepart_ts)

    def test__filenamepart_base(self):
        self.assertIsNotNone(self.fo.filenamepart_base)
        self.assertEqual('.name', self.fo.filenamepart_base)

    def test__filenamepart_ext(self):
        self.assertIsNotNone(self.fo.filenamepart_ext)
        self.assertNotEqual(' ', self.fo.filenamepart_ext)
        self.assertNotEqual('', self.fo.filenamepart_ext)
        self.assertNotEqual('bla', self.fo.filenamepart_ext)
        self.assertEqual('jpg', self.fo.filenamepart_ext)

    def test__filenamepart_tags(self):
        self.assertIsNotNone(self.fo.filenamepart_tags)
        self.assertNotEqual(['firsttag'], self.fo.filenamepart_tags)
        self.assertNotEqual(['2ndtag'], self.fo.filenamepart_tags)
        self.assertEqual(['firsttag', '2ndtag'], self.fo.filenamepart_tags)


class TestFileObjectFilenamePartitioningHiddenFileCompoundSuffixTags(TestCase):
    def setUp(self):
        self.fo = FileObject('.name -- firsttag 2ndtag.tar.gz')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)
        self.assertEqual('.name -- firsttag 2ndtag', self.fo.fnbase)

    def test__filenamepart_ts(self):
        self.assertIsNone(self.fo.filenamepart_ts)

    def test__filenamepart_base(self):
        self.assertIsNotNone(self.fo.filenamepart_base)
        self.assertEqual('.name', self.fo.filenamepart_base)

    def test__filenamepart_ext(self):
        self.assertIsNotNone(self.fo.filenamepart_ext)
        self.assertNotEqual(' ', self.fo.filenamepart_ext)
        self.assertNotEqual('', self.fo.filenamepart_ext)
        self.assertNotEqual('tar', self.fo.filenamepart_ext)
        self.assertNotEqual('gz', self.fo.filenamepart_ext)
        self.assertNotEqual('gz.tar', self.fo.filenamepart_ext)
        self.assertEqual('tar.gz', self.fo.filenamepart_ext)

    def test__filenamepart_tags(self):
        self.assertIsNotNone(self.fo.filenamepart_tags)
        self.assertNotEqual(['firsttag'], self.fo.filenamepart_tags)
        self.assertNotEqual(['2ndtag'], self.fo.filenamepart_tags)
        self.assertNotEqual(['tar'], self.fo.filenamepart_tags)
        self.assertNotEqual(['gz'], self.fo.filenamepart_tags)
        self.assertNotEqual(['tar.gz'], self.fo.filenamepart_tags)
        self.assertEqual(['firsttag', '2ndtag'], self.fo.filenamepart_tags)


class TestFileObjectFilenamePartitioningDifficultCombination(TestCase):
    def setUp(self):
        self.fo = FileObject('.name -- tar firsttag 2ndtag.tar.gz')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)
        self.assertEqual('.name -- tar firsttag 2ndtag', self.fo.fnbase)

    def test__filenamepart_ts(self):
        self.assertIsNone(self.fo.filenamepart_ts)

    def test__filenamepart_base(self):
        self.assertIsNotNone(self.fo.filenamepart_base)
        self.assertEqual('.name', self.fo.filenamepart_base)

    def test__filenamepart_ext(self):
        self.assertIsNotNone(self.fo.filenamepart_ext)
        self.assertNotEqual(' ', self.fo.filenamepart_ext)
        self.assertNotEqual('', self.fo.filenamepart_ext)
        self.assertNotEqual('tar', self.fo.filenamepart_ext)
        self.assertNotEqual('gz', self.fo.filenamepart_ext)
        self.assertNotEqual('gz.tar', self.fo.filenamepart_ext)
        self.assertEqual('tar.gz', self.fo.filenamepart_ext)

    def test__filenamepart_tags(self):
        self.assertIsNotNone(self.fo.filenamepart_tags)
        self.assertNotEqual(['firsttag'], self.fo.filenamepart_tags)
        self.assertNotEqual(['2ndtag'], self.fo.filenamepart_tags)
        self.assertNotEqual(['tar'], self.fo.filenamepart_tags)
        self.assertNotEqual(['gz'], self.fo.filenamepart_tags)
        self.assertNotEqual(['tar.gz'], self.fo.filenamepart_tags)
        self.assertEqual(['tar', 'firsttag', '2ndtag'],
                         self.fo.filenamepart_tags)


class TestFileObjectFilenamePartitioningAnotherDifficultCombination(TestCase):
    def setUp(self):
        self.fo = FileObject('.tar name -- gz firsttag 2ndtag.tar.gz')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)
        self.assertEqual('.tar name -- gz firsttag 2ndtag', self.fo.fnbase)

    def test__filenamepart_ts(self):
        self.assertIsNone(self.fo.filenamepart_ts)

    def test__filenamepart_base(self):
        self.assertIsNotNone(self.fo.filenamepart_base)
        self.assertEqual('.tar name', self.fo.filenamepart_base)

    def test__filenamepart_ext(self):
        self.assertIsNotNone(self.fo.filenamepart_ext)
        self.assertNotEqual(' ', self.fo.filenamepart_ext)
        self.assertNotEqual('', self.fo.filenamepart_ext)
        self.assertNotEqual('tar', self.fo.filenamepart_ext)
        self.assertNotEqual('gz', self.fo.filenamepart_ext)
        self.assertNotEqual('gz.tar', self.fo.filenamepart_ext)
        self.assertEqual('tar.gz', self.fo.filenamepart_ext)

    def test__filenamepart_tags(self):
        self.assertIsNotNone(self.fo.filenamepart_tags)
        self.assertNotEqual(['firsttag'], self.fo.filenamepart_tags)
        self.assertNotEqual(['2ndtag'], self.fo.filenamepart_tags)
        self.assertNotEqual(['tar'], self.fo.filenamepart_tags)
        self.assertNotEqual(['gz'], self.fo.filenamepart_tags)
        self.assertNotEqual(['tar.gz'], self.fo.filenamepart_tags)
        self.assertEqual(['gz', 'firsttag', '2ndtag'],
                         self.fo.filenamepart_tags)


class TestFileObjectFilenamePartitioningEvenMoreDifficultCombination(TestCase):
    def setUp(self):
        self.fo = FileObject('.tar.gz name -- gz firsttag 2ndtag.tar.gz')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)
        self.assertEqual('.tar.gz name -- gz firsttag 2ndtag', self.fo.fnbase)

    def test__filenamepart_ts(self):
        self.assertIsNone(self.fo.filenamepart_ts)

    def test__filenamepart_base(self):
        self.assertIsNotNone(self.fo.filenamepart_base)
        self.assertEqual('.tar.gz name', self.fo.filenamepart_base)

    def test__filenamepart_ext(self):
        self.assertIsNotNone(self.fo.filenamepart_ext)
        self.assertNotEqual(' ', self.fo.filenamepart_ext)
        self.assertNotEqual('', self.fo.filenamepart_ext)
        self.assertNotEqual('tar', self.fo.filenamepart_ext)
        self.assertNotEqual('gz', self.fo.filenamepart_ext)
        self.assertNotEqual('gz.tar', self.fo.filenamepart_ext)
        self.assertEqual('tar.gz', self.fo.filenamepart_ext)

    def test__filenamepart_tags(self):
        self.assertIsNotNone(self.fo.filenamepart_tags)
        self.assertNotEqual(['firsttag'], self.fo.filenamepart_tags)
        self.assertNotEqual(['2ndtag'], self.fo.filenamepart_tags)
        self.assertNotEqual(['tar'], self.fo.filenamepart_tags)
        self.assertNotEqual(['gz'], self.fo.filenamepart_tags)
        self.assertNotEqual(['tar.gz'], self.fo.filenamepart_tags)
        self.assertEqual(['gz', 'firsttag', '2ndtag'],
                         self.fo.filenamepart_tags)


class TestFileObjectFilenamePartitioningReturnValueType(TestCase):
    def setUp(self):
        self.fo = FileObject('20160722 Descriptive name -- firsttag tagtwo.txt')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)
        self.assertEqual('20160722 Descriptive name -- firsttag tagtwo',
                         self.fo.fnbase)

    def test__filenamepart_ts_returns_string_or_none(self):
        self.assertIs(str, type(self.fo.filenamepart_ts))

    def test__filenamepart_base_returns_string_or_none(self):
        self.assertIs(str, type(self.fo.filenamepart_base))

    def test__filenamepart_ext_returns_string_or_none(self):
        self.assertIs(str, type(self.fo.filenamepart_ext))

    def test__filenamepart_tags_returns_list_of_string_or_empty_list(self):
        self.assertIs(list, type(self.fo.filenamepart_tags))


class TestFileObjectFilenamePartitioningReturnValueTypeNoTags(TestCase):
    def setUp(self):
        self.fo = FileObject('20160722 Descriptive name.txt')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)
        self.assertEqual('20160722 Descriptive name', self.fo.fnbase)

    def test__filenamepart_ts_returns_string_or_none(self):
        self.assertIs(str, type(self.fo.filenamepart_ts))

    def test__filenamepart_base_returns_string_or_none(self):
        self.assertIs(str, type(self.fo.filenamepart_base))

    def test__filenamepart_ext_returns_string_or_none(self):
        self.assertIs(str, type(self.fo.filenamepart_ext))

    def test__filenamepart_tags_returns_list_of_string_or_empty_list(self):
        self.assertIs(list, type(self.fo.filenamepart_tags))
        self.assertEqual([], self.fo.filenamepart_tags)


class TestFileObjectFilenamePartitioningReturnValueTypeNoTagsNoExt(TestCase):
    def setUp(self):
        self.fo = FileObject('20160722 Descriptive name')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)
        self.assertEqual('20160722 Descriptive name', self.fo.fnbase)

    def test__filenamepart_ts_returns_string_or_none(self):
        self.assertIs(str, type(self.fo.filenamepart_ts))

    def test__filenamepart_base_returns_string_or_none(self):
        self.assertIs(str, type(self.fo.filenamepart_base))

    def test__filenamepart_ext_returns_string_or_none(self):
        self.assertIsNot(str, type(self.fo.filenamepart_ext))
        self.assertIsNone(self.fo.filenamepart_ext)

    def test__filenamepart_tags_returns_list_of_string_or_empty_list(self):
        self.assertIs(list, type(self.fo.filenamepart_tags))
        self.assertEqual([], self.fo.filenamepart_tags)


class TestFileObjectFilenamePartitioningWithActualFilename(TestCase):
    def setUp(self):
        self.fo = FileObject('2016-08-05_18-46-34 Working on PLL-monstret -- projects frfx.png')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)

    def test_filenamepart_ts(self):
        self.assertEqual('2016-08-05_18-46-34', self.fo.filenamepart_ts)

    def test_filenamepart_base(self):
        self.assertEqual('Working on PLL-monstret', self.fo.filenamepart_base)

    def test_filenamepart_ext(self):
        self.assertEqual('png', self.fo.filenamepart_ext)

    def test_filenamepart_tags(self):
        self.assertEqual(['projects', 'frfx'], self.fo.filenamepart_tags)


class TestFileObjectFilenamePartitioningWithActualFilename2(TestCase):
    def setUp(self):
        self.fo = FileObject('2016-07-30T175241 Drawing with Hanvon tablet in krita_x86_xp_2.8.1.1 -- projects.png')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)

    def test_filenamepart_ts(self):
        self.assertEqual('2016-07-30T175241', self.fo.filenamepart_ts)

    def test_filenamepart_base(self):
        self.assertEqual('Drawing with Hanvon tablet in krita_x86_xp_2.8.1.1',
                         self.fo.filenamepart_base)

    def test_filenamepart_ext(self):
        self.assertEqual('png', self.fo.filenamepart_ext)

    def test_filenamepart_tags(self):
        self.assertEqual(['projects'], self.fo.filenamepart_tags)


class TestFileObjectFilenamePartitioningWithActualFilename3(TestCase):
    def setUp(self):
        self.fo = FileObject('2016-08-01_104304_pages.stern.nyu.edu oyepa - Linux tagging filesystem -- workflow pim.html')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)

    def test_filenamepart_ts(self):
        self.assertEqual('2016-08-01_104304', self.fo.filenamepart_ts)

    def test_filenamepart_base(self):
        self.assertEqual('pages.stern.nyu.edu oyepa - Linux tagging filesystem',
                         self.fo.filenamepart_base)

    def test_filenamepart_ext(self):
        self.assertEqual('html', self.fo.filenamepart_ext)

    def test_filenamepart_tags(self):
        self.assertEqual(['workflow', 'pim'], self.fo.filenamepart_tags)


class TestFileObjectFilenamePartitioningWithActualFilename4(TestCase):
    def setUp(self):
        self.fo = FileObject('2010-01-31_161251.jpg')

    def test_setUp(self):
        self.assertIsNotNone(self.fo)

    def test_filenamepart_ts(self):
        self.assertEqual('2010-01-31_161251', self.fo.filenamepart_ts)

    def test_filenamepart_base(self):
        self.assertEqual('', self.fo.filenamepart_base)

    def test_filenamepart_ext(self):
        self.assertEqual('jpg', self.fo.filenamepart_ext)

    def test_filenamepart_tags(self):
        self.assertEqual([], self.fo.filenamepart_tags)


class TestFileObjectFilenameIsInFiletagsFormat(TestCase):
    """
    Tests that a FileObject filename is in the "filetags" format, I.E:

                                   .------------ FILENAME_TAG_SEPARATOR
                                  ||         .-- BETWEEN_TAG_SEPARATOR
                                  VV         V
        20160722 Descriptive name -- firsttag tagtwo.txt
        |______| |______________|    |_____________| |_|
           ts          base               tags       ext


    Cases where all the filename parts; 'ts', 'base' and 'tags' are present.
    """
    def test_has_filetags_format(self):
        self.fo = FileObject('2016-08-05_18-46-34 Working on PLL-monstret -- projects frfx.png')
        self.assertTrue(self.fo.filetags_format_filename())

    def test_has_filetags_format_no_extension(self):
        self.fo = FileObject('2016-08-05_18-46-34 Working on PLL-monstret -- projects frfx')
        self.assertTrue(self.fo.filetags_format_filename())

    def test_has_filetags_format_date_only(self):
        self.fo = FileObject('2016-08-05 Working on PLL-monstret -- projects frfx.png')
        self.assertTrue(self.fo.filetags_format_filename())


class TestFileObjectFilenameNotInFiletagsFormat(TestCase):
    """
    Tests that a FileObject filename is in the "filetags" format as per above.

    Cases where filename parts are missing.
    """
    def test_doesnt_have_filetags_format_missing_fnpart_base(self):
        self.fo = FileObject('2016-08-05_18-46-34 -- projects frfx.png')
        self.assertFalse(self.fo.filetags_format_filename())

    def test_doesnt_have_filetags_format_missing_fnpart_tags(self):
        self.fo = FileObject('2016-08-05_18-46-34 Working on PLL-monstret.png')
        self.assertFalse(self.fo.filetags_format_filename())

    def test_doesnt_have_filetags_format_missing_fnpart_ts(self):
        self.fo = FileObject('Working on PLL-monstret.png')
        self.assertFalse(self.fo.filetags_format_filename())
