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

try:
    import isbnlib
except ImportError:
    isbnlib = None

from analyzers import analyze_ebook
from analyzers.analyze_ebook import (
    extract_isbns_from_text,
    find_ebook_isbns_in_text,
    validate_isbn,
    filter_isbns,
    ISBNMetadata,
    remove_ignored_textlines
)
import unit_utils as uu


def get_ebook_analyzer(fileobject):
    return analyze_ebook.EbookAnalyzer(
        fileobject,
        uu.get_default_config(),
        request_data_callback=uu.mock_request_data_callback
    )


@unittest.skipIf(isbnlib is None, 'Failed to import required module "isbnlib"')
class TestEbookAnalyzer(unittest.TestCase):
    def setUp(self):
        self.fileobject = uu.get_named_fileobject('2010-01-31_161251.jpg')
        self.analyzer = get_ebook_analyzer(self.fileobject)

    def test_setup(self):
        self.assertIsNotNone(self.fileobject)
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


class TestValidateISBN(unittest.TestCase):
    def test_returns_valid_isbn_numbers(self):
        sample_isbn = '1565923065'
        self.assertEqual(validate_isbn(sample_isbn), sample_isbn)

    def test_returns_non_for_invalid_isbn_numbers(self):
        sample_invalid_isbns = [
            None,
            '',
            ' ',
            '123',
            '1234567890'
        ]
        for sample_isbn in sample_invalid_isbns:
            self.assertIsNone(validate_isbn(sample_isbn))


class TestFilterISBN(unittest.TestCase):
    def test_returns_valid_isbn_numbers(self):
        sample_isbn = ['1565923065']
        self.assertEqual(filter_isbns(sample_isbn), sample_isbn)

    def test_returns_non_for_invalid_isbn_numbers(self):
        sample_invalid_isbns = [
            None,
            [None],
            [''],
            ['1111111111'],
            ['9999999999'],
        ]
        for sample_isbn in sample_invalid_isbns:
            self.assertEqual(filter_isbns(sample_isbn), [])


class TestRemoveIgnoredTextLines(unittest.TestCase):
    def test_removes_lines_as_expected(self):
        input_text = '''Foo Bar: A Modern Approach
This page intentionally left blank
Foo Bar'''
        expect_text = '''Foo Bar: A Modern Approach
Foo Bar'''

        actual = remove_ignored_textlines(input_text)
        self.assertEqual(actual, expect_text)


class TestISBNMetadata(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

        self.m1 = {
            'title': 'AI Algorithms, Data Structures, And Idioms In Prolog, Lisp, And Java',
            'authors': ['George F. Luger', 'William A. Stubblefield'],
            'publisher': 'Pearson Addison-Wesley',
            'year': '2009',
            'language': 'eng',
            'isbn10': '0136070477',
            'isbn13': '9780136070474'
        }

        self.m2 = {
            'title': 'AI Algorithms, Data Structures, And Idioms In Prolog, Lisp, And Java',
            'authors': ['George F. Luger', 'William A. Stubblefield'],
            'publisher': 'Pearson Addison-Wesley',
            'year': '2009',
            'language': 'eng',
            'isbn13': '9780136070474'
        }
        self.m3 = {
            'title': None,
            'authors': [],
            'publisher': None,
            'year': None,
            'language': None,
            'isbn13': '9780136070474'
        }

        self.m4 = {
            'isbn10': '0136070477',
        }

        # e-ISBN
        self.m5 = {
            'title': 'Computational Intelligence Methods And Techniques',
            'authors': ['Leszek Rutkowski'],
            'publisher': 'Springer',
            'year': '2008',
            'language': 'eng',
            'isbn10': '3540762884',
            'isbn13': '9783540762881'
        }

        # ISBN
        self.m6 = {
            'title': 'Computational Intelligence: Methods And Techniques',
            'authors': ['Leszek Rutkowski'],
            'publisher': 'Springer',
            'year': '2008',
            'language': 'eng',
            'isbn10': '3540762876',
            'isbn13': '9783540762874'
        }

    def test_isbn_metadata_from_args(self):
        isbn_metadata = ISBNMetadata(**self.m1)
        self.assertEqual(isbn_metadata.title, 'AI Algorithms, Data Structures, And Idioms In Prolog, Lisp, And Java')
        self.assertEqual(isbn_metadata.authors, ['George F. Luger', 'William A. Stubblefield'])
        self.assertEqual(isbn_metadata.year, '2009')
        self.assertEqual(isbn_metadata.language, 'eng')
        self.assertEqual(isbn_metadata.isbn10, '0136070477')
        self.assertEqual(isbn_metadata.isbn13, '9780136070474')

    def test_isbn_metadata_from_kwargs(self):
        isbn_metadata = ISBNMetadata(**self.m1)
        self.assertEqual(isbn_metadata.title, 'AI Algorithms, Data Structures, And Idioms In Prolog, Lisp, And Java')
        self.assertEqual(isbn_metadata.authors, ['George F. Luger', 'William A. Stubblefield'])
        self.assertEqual(isbn_metadata.year, '2009')
        self.assertEqual(isbn_metadata.language, 'eng')
        self.assertEqual(isbn_metadata.isbn10, '0136070477')
        self.assertEqual(isbn_metadata.isbn13, '9780136070474')

    def test_equality(self):
        self.assertEqual(ISBNMetadata(**self.m1), ISBNMetadata(**self.m2))

        # TODO: .. ?
        # self.assertEqual(ISBNMetadata(**self.m5), ISBNMetadata(**self.m6))

    def test_equality_2(self):
        self.skipTest('TODO: .. ?')
        m5 = ISBNMetadata(authors=['Leszek Rutkowski'],
                          language='eng',
                          publisher='Springer',
                          isbn10='3540762884',
                          isbn13='9783540762881',
                          title='Computational Intelligence Methods And Techniques',
                          year='2008')
        m6 = ISBNMetadata(authors=['Leszek Rutkowski'],
                          language='eng',
                          publisher='Springer',
                          isbn10='3540762876',
                          isbn13='9783540762874',
                          title='Computational Intelligence: Methods And Techniques',
                          year='2008')

        self.assertEqual(m5, m6)

    def test_equality_based_on_isbn_numbers(self):
        self.assertEqual(ISBNMetadata(**self.m1), ISBNMetadata(**self.m3))
        self.assertEqual(ISBNMetadata(**self.m2), ISBNMetadata(**self.m3))
        self.assertEqual(ISBNMetadata(**self.m1), ISBNMetadata(**self.m4))
        self.assertEqual(ISBNMetadata(**self.m2), ISBNMetadata(**self.m4))

    def test_adding_duplicates_to_set(self):
        metadataset = set()
        self.assertEqual(len(metadataset), 0)
        metadataset.add(ISBNMetadata(**self.m1))
        self.assertEqual(len(metadataset), 1)
        metadataset.add(ISBNMetadata(**self.m2))
        self.assertEqual(len(metadataset), 1)
        metadataset.add(ISBNMetadata(**self.m3))
        self.assertEqual(len(metadataset), 1)
        metadataset.add(ISBNMetadata(**self.m4))
        self.assertEqual(len(metadataset), 1)
        metadataset.add(ISBNMetadata(**self.m5))
        self.assertEqual(len(metadataset), 2)

        # TODO: .. ?
        # metadataset.add(ISBNMetadata(**self.m6))
        # self.assertEqual(len(metadataset), 2)

    def test_edition_in_title(self):
        self.skipTest('TODO: ..')

        m = ISBNMetadata(title='Microcontrollers, Second Edition')
        self.assertEqual(m.title, 'Microcontrollers')
        self.assertEqual(m.edition, '2')


class TestFindEbookISBNsInText(unittest.TestCase):
    def test_finds_expected(self):
        text = '''Computational Intelligence

Leszek Rutkowski

Computational Intelligence
Methods and Techniques

123

Prof. Leszek Rutkowski
Department of Computer Engineering
Technical University of Czestochowa
Armii Krajowej 36
42-200 Czestochowa
Poland
Irutko@kik.pcz.czest.pl

ISBN 978-3-540-76287-4

e-ISBN 978-3-540-76288-1

Originally published in Polish
METODY I TECHNIKI SZTUCZNEJ INTELIGENCJI
by Leszek Rutkowski, 2005 by Polish Scientific Publishers PWN
c by Wydawnictwo Naukowe PWN SA, Warszawa 2005
'''
        actual = find_ebook_isbns_in_text(text)
        self.assertIn('9783540762881', actual)

