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

import os
import unittest

import unit_utils as uu

try:
    from thirdparty import epubzilla
except (ModuleNotFoundError, ImportError):
    epubzilla = None


class TestExtractTextWithEpubzilla(unittest.TestCase):
    def setUp(self):
        self.sample_file = uu.abspath_testfile('pg38145-images.epub')
        self.assertTrue(os.path.isfile(self.sample_file))

    @unittest.skipIf(epubzilla is None,
                     'Unable to import module "thirdparty.epubzilla"')
    def test_does_not_open_non_epub_files(self):
        not_epub_file = uu.abspath_testfile('gmail.pdf')
        self.assertTrue(os.path.isfile(not_epub_file))

        with self.assertRaises(Exception):
            actual = epubzilla.Epub.from_file(not_epub_file)

    @unittest.skipIf(epubzilla is None,
                     'Unable to import module "thirdparty.epubzilla"')
    def test_opens_sample_epub_file(self):
        actual = epubzilla.Epub.from_file(self.sample_file)
        self.assertIsNotNone(actual)

    @unittest.skipIf(epubzilla is None,
                     'Unable to import module "thirdparty.epubzilla"')
    def test_reads_sample_file_metadata(self):
        def _assert_metadata(key, expected):
            self.assertEqual(getattr(actual, key), expected)

        actual = epubzilla.Epub.from_file(self.sample_file)
        _assert_metadata('author', 'Friedrich Wilhelm Nietzsche')
        _assert_metadata('title',
                         'Human, All Too Human: A Book for Free Spirits')
