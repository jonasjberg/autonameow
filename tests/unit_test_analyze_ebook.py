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

import unittest

from analyzers import analyze_ebook
from analyzers.analyze_ebook import extract_isbns_from_text

import unit_utils as uu

try:
    import isbnlib
except (ModuleNotFoundError, ImportError):
    isbnlib = None


def get_ebook_analyzer(file_object):
    return analyze_ebook.EbookAnalyzer(
        file_object,
        add_results_callback=uu.mock_add_results_callback,
        request_data_callback=uu.mock_request_data_callback
    )


@unittest.skipIf(isbnlib is None, 'Failed to import required module "isbnlib"')
class TestEbookAnalyzer(unittest.TestCase):
    def setUp(self):
        self.file_object = uu.get_named_file_object('2010-01-31_161251.jpg')
        self.analyzer = get_ebook_analyzer(self.file_object)

    def test_setup(self):
        self.assertIsNotNone(self.file_object)
        self.assertIsNotNone(self.analyzer)


class TestExtractIsbnsFromText(unittest.TestCase):
    def test_returns_expected_type(self):
        text = 'fooo1-56592-306-5baar'
        actual = extract_isbns_from_text(text)
        self.assertTrue(isinstance(actual, list))

    def test_returns_expected_given_text_without_isbns(self):
        text = 'fooo'
        actual = extract_isbns_from_text(text)
        self.assertEqual(len(actual), 0)

    def test_returns_expected_given_only_isbn(self):
        text = '1-56592-306-5'
        actual = extract_isbns_from_text(text)
        self.assertEqual(len(actual), 1)
        self.assertIn('1565923065', actual)

    def test_returns_expected_given_text_with_isbn(self):
        text = '''
Practical C Programming, 3rd Edition  
By Steve Oualline 
3rd Edition August 1997 
ISBN: 1-56592-306-5 
This new edition of "Practical C Programming" teaches users not only the mechanics or
programming, but also how to create programs that are easy to read, maintain, and
debug. It features more extensive examples and an introduction to graphical
development environments. Programs conform to ANSI C.
'''
        actual = extract_isbns_from_text(text)
        self.assertEqual(len(actual), 1)
        self.assertIn('1565923065', actual)

    def test_returns_expected_given_text_with_duplicate_isbn(self):
        text = '''
Practical C Programming, 3rd Edition
By Steve Oualline
3rd Edition August 1997
ISBN: 1-56592-306-5
This new edition of "Practical C Programming" teaches users not only the mechanics or
programming, but also how to create programs that are easy to read, maintain, and
debug. It features more extensive examples and an introduction to graphical
development environments. Programs conform to ANSI C.
ISBN: 1-56592-306-5
'''
        actual = extract_isbns_from_text(text)
        self.assertEqual(len(actual), 2)
        self.assertIn('1565923065', actual)
