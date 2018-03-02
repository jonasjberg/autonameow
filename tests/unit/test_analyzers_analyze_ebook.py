# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg
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

from unittest import (
    skipIf,
    TestCase,
)
from unittest.mock import Mock

try:
    import isbnlib
except ImportError:
    ISBNLIB_IS_NOT_AVAILABLE = True, 'Missing (failed to import) required module "isbnlib"'
else:
    ISBNLIB_IS_NOT_AVAILABLE = False, ''

import unit.utils as uu
from analyzers.analyze_ebook import (
    deduplicate_isbns,
    EbookAnalyzer,
    extract_ebook_isbns_from_text,
    extract_isbns_from_text,
    filter_isbns,
    ISBNMetadata,
    remove_ignored_textlines,
    validate_isbn
)


def get_ebook_analyzer(fileobject):
    mock_config = Mock()

    # TODO: [hack][cleanup] Does this behave as the "mocked" systems? (!)
    return EbookAnalyzer(
        fileobject,
        mock_config,
        request_data_callback=uu.mock_request_data_callback
    )


@skipIf(*ISBNLIB_IS_NOT_AVAILABLE)
class TestEbookAnalyzer(TestCase):
    def setUp(self):
        self.fileobject = uu.get_named_fileobject('2010-01-31_161251.jpg')
        self.analyzer = get_ebook_analyzer(self.fileobject)

    def test_setup(self):
        self.assertIsNotNone(self.fileobject)
        self.assertIsNotNone(self.analyzer)


@skipIf(*ISBNLIB_IS_NOT_AVAILABLE)
class TestExtractIsbnsFromText(TestCase):
    def test_returns_expected_type(self):
        text = 'fooo1-56592-306-5baar'
        actual = extract_isbns_from_text(text)
        self.assertIsInstance(actual, list)

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


@skipIf(*ISBNLIB_IS_NOT_AVAILABLE)
class TestValidateISBN(TestCase):
    def test_returns_valid_isbn_numbers(self):
        sample_isbn = '1565923065'
        self.assertEqual(validate_isbn(sample_isbn), sample_isbn)

    def test_returns_none_for_invalid_isbn_numbers(self):
        sample_invalid_isbns = [
            None,
            '',
            ' ',
            '123',
            '1234567890'
        ]
        for sample_isbn in sample_invalid_isbns:
            self.assertIsNone(validate_isbn(sample_isbn))


class TestDeduplicateIsbns(TestCase):
    def _assert_that_it(self, returns, given):
        actual = deduplicate_isbns(given)
        self.assertEqual(sorted(returns), sorted(actual))

    def test_returns_only_unique_isbns_given_duplicates(self):
        self._assert_that_it(
            returns=['9780596802295', '9780596802301'],
            given=['9780596802295', '9780596802295', '9780596802301']
        )

    def test_returns_unique_isbns_as_is(self):
        self._assert_that_it(
            returns=['9780596802295', '9780596802301'],
            given=['9780596802295', '9780596802301']
        )

    def test_returns_single_isbn_as_is(self):
        self._assert_that_it(
            returns=['9780596802301'],
            given=['9780596802301']
        )


class TestFilterISBN(TestCase):
    BLACKLISTED_ISBN_NUMBERS = ['0000000000', '1111111111', '2222222222',
                                '3333333333', '4444444444', '5555555555',
                                '6666666666', '7777777777', '8888888888',
                                '9999999999', '0123456789']

    def test_returns_valid_isbn_numbers(self):
        sample_isbn = ['1565923065']
        actual = filter_isbns(sample_isbn, self.BLACKLISTED_ISBN_NUMBERS)
        self.assertEqual(actual, sample_isbn)

    def test_returns_none_for_invalid_isbn_numbers(self):
        sample_invalid_isbns = [
            None,
            [None],
            [''],
            ['1111111111'],
            ['9999999999'],
        ]
        for sample_isbn in sample_invalid_isbns:
            actual = filter_isbns(sample_isbn, self.BLACKLISTED_ISBN_NUMBERS)
            self.assertEqual(actual, [])


class TestRemoveIgnoredTextLines(TestCase):
    def test_removes_lines_as_expected(self):
        input_text = '''Foo Bar: A Modern Approach
This page intentionally left blank
Foo Bar'''
        expect_text = '''Foo Bar: A Modern Approach
Foo Bar'''

        actual = remove_ignored_textlines(input_text)
        self.assertEqual(actual, expect_text)


@skipIf(*ISBNLIB_IS_NOT_AVAILABLE)
class TestISBNMetadata(TestCase):
    ISBN13_A = '9780136070474'
    ISBN10_A = '0136070477'

    def setUp(self):
        self.maxDiff = None

        self.m1 = {
            'title': 'AI Algorithms, Data Structures, And Idioms In Prolog, Lisp, And Java',
            'authors': ['George F. Luger', 'William A. Stubblefield'],
            'publisher': 'Pearson Addison-Wesley',
            'year': '2009',
            'language': 'eng',
            'isbn10': self.ISBN10_A,
            'isbn13': self.ISBN13_A
        }

        self.m2 = {
            'title': 'AI Algorithms, Data Structures, And Idioms In Prolog, Lisp, And Java',
            'authors': ['George F. Luger', 'William A. Stubblefield'],
            'publisher': 'Pearson Addison-Wesley',
            'year': '2009',
            'language': 'eng',
            'isbn13': self.ISBN13_A
        }
        self.m3 = {
            'title': None,
            'authors': [],
            'publisher': None,
            'year': None,
            'language': None,
            'isbn13': self.ISBN13_A
        }

        self.m4 = {
            'isbn10': self.ISBN10_A,
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

    def test_derives_isbn13_from_isbn10(self):
        actual = ISBNMetadata(isbn10=self.ISBN10_A)
        self.assertEqual(self.ISBN13_A, actual.isbn13)

    def test_derives_isbn10_from_isbn13(self):
        actual = ISBNMetadata(isbn13=self.ISBN13_A)
        self.assertEqual(self.ISBN10_A, actual.isbn10)

    def test_isbn_metadata_from_args(self):
        isbn_metadata = ISBNMetadata(**self.m1)
        self.assertEqual(isbn_metadata.title, 'AI Algorithms, Data Structures, And Idioms In Prolog, Lisp, And Java')
        self.assertEqual(isbn_metadata.authors, ['George F. Luger', 'William A. Stubblefield'])
        self.assertEqual(isbn_metadata.year, '2009')
        self.assertEqual(isbn_metadata.language, 'eng')
        self.assertEqual(isbn_metadata.isbn10, self.ISBN10_A)
        self.assertEqual(isbn_metadata.isbn13, self.ISBN13_A)

    def test_isbn_metadata_from_kwargs(self):
        isbn_metadata = ISBNMetadata(**self.m1)
        self.assertEqual(isbn_metadata.title, 'AI Algorithms, Data Structures, And Idioms In Prolog, Lisp, And Java')
        self.assertEqual(isbn_metadata.authors, ['George F. Luger', 'William A. Stubblefield'])
        self.assertEqual(isbn_metadata.year, '2009')
        self.assertEqual(isbn_metadata.language, 'eng')
        self.assertEqual(isbn_metadata.isbn10, self.ISBN10_A)
        self.assertEqual(isbn_metadata.isbn13, self.ISBN13_A)

    def test_equality(self):
        self.assertEqual(ISBNMetadata(**self.m1), ISBNMetadata(**self.m2))
        self.assertEqual(ISBNMetadata(**self.m5), ISBNMetadata(**self.m6))

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

    def test_edition_in_title(self):
        self.skipTest('TODO: ..')

        m = ISBNMetadata(title='Microcontrollers, Second Edition')
        self.assertEqual(m.title, 'Microcontrollers')
        self.assertEqual(m.edition, '2')


@skipIf(*ISBNLIB_IS_NOT_AVAILABLE)
class TestISBNMetadataEquality(TestCase):
    ISBN10_A = '3540762884'
    ISBN10_B = '3540762876'
    ISBN13_A = '9783540762881'
    ISBN13_B = '9783540762874'

    def test_all_same_except_isbn_numbers(self):
        # Case where one book has multiple ISBNs for different editions, etc.
        m1 = ISBNMetadata(
            authors=['Leszek Rutkowski'],
            language='eng',
            publisher='Springer',
            isbn10=self.ISBN10_A,
            isbn13=self.ISBN13_A,
            title='Computational Intelligence Methods And Techniques',
            year='2008'
        )
        m2 = ISBNMetadata(
            authors=['Leszek Rutkowski'],
            language='eng',
            publisher='Springer',
            isbn10=self.ISBN10_B,
            isbn13=self.ISBN13_B,
            title='Computational Intelligence: Methods And Techniques',
            year='2008'
        )
        self.assertEqual(m1, m2)

    def test_same_isbn_numbers_missing_author(self):
        m1 = ISBNMetadata(
            authors=['Leszek Rutkowski'],
            language='eng',
            publisher='Springer',
            isbn10=self.ISBN10_A,
            isbn13=self.ISBN13_A,
            title='Computational Intelligence Methods And Techniques',
            year='2008'
        )
        m2 = ISBNMetadata(
            authors=[''],
            language='eng',
            publisher='Springer',
            isbn10=self.ISBN10_A,
            isbn13=self.ISBN13_A,
            title='Computational Intelligence: Methods And Techniques',
            year='2008'
        )
        self.assertEqual(m1, m2)

    def test_same_isbn_numbers_shortened_author(self):
        m1 = ISBNMetadata(
            authors=['Leszek Rutkowski'],
            language='eng',
            publisher='Springer',
            isbn10=self.ISBN10_A,
            isbn13=self.ISBN13_A,
            title='Computational Intelligence Methods And Techniques',
            year='2008'
        )
        m2 = ISBNMetadata(
            authors=['Rutkowski L.'],
            language='eng',
            publisher='Springer',
            isbn10=self.ISBN10_A,
            isbn13=self.ISBN13_A,
            title='Computational Intelligence: Methods And Techniques',
            year='2008'
        )
        self.assertEqual(m1, m2)

    def test_same_isbn_numbers_different_author(self):
        m1 = ISBNMetadata(
            authors=['Leszek Rutkowski'],
            language='eng',
            publisher='Springer',
            isbn10=self.ISBN10_A,
            isbn13=self.ISBN13_A,
            title='Computational Intelligence Methods And Techniques',
            year='2008'
        )
        m2 = ISBNMetadata(
            authors=['Gibson Sjöberg'],
            language='eng',
            publisher='Springer',
            isbn10=self.ISBN10_A,
            isbn13=self.ISBN13_A,
            title='Computational Intelligence: Methods And Techniques',
            year='2008'
        )
        self.assertEqual(m1, m2)

    def test_same_isbn_numbers_all_other_fields_missing(self):
        m1 = ISBNMetadata(
            authors=[],
            language='',
            publisher='',
            isbn10=self.ISBN10_A,
            isbn13=self.ISBN13_A,
            title='',
            year=''
        )
        m2 = ISBNMetadata(
            authors=[],
            language='',
            publisher='',
            isbn10=self.ISBN10_A,
            isbn13=self.ISBN13_A,
            title='',
            year=''
        )
        self.assertEqual(m1, m2)

    def test_same_isbn_numbers_different_author_and_publisher(self):
        m1 = ISBNMetadata(
            authors=['Leszek Rutkowski'],
            language='eng',
            publisher='Springer',
            isbn10=self.ISBN10_A,
            isbn13=self.ISBN13_A,
            title='Computational Intelligence Methods And Techniques',
            year='2008'
        )
        m2 = ISBNMetadata(
            authors=['Gibson Sjöberg'],
            language='eng',
            publisher='CatPub',
            isbn10=self.ISBN10_B,
            isbn13=self.ISBN13_A,
            title='Computational Intelligence: Methods And Techniques',
            year='2008'
        )
        self.assertEqual(m1, m2)

    def test_different_author_publisher_isbn_numbers(self):
        m1 = ISBNMetadata(
            authors=['Leszek Rutkowski'],
            language='eng',
            publisher='Springer',
            isbn10=self.ISBN10_A,
            isbn13=self.ISBN13_A,
            title='Computational Intelligence Methods And Techniques',
            year='2008'
        )
        m2 = ISBNMetadata(
            authors=['Gibson Sjöberg'],
            language='eng',
            publisher='CatPub',
            isbn10=self.ISBN10_B,
            isbn13=self.ISBN13_B,
            title='Computational Intelligence: Methods And Techniques',
            year='2008'
        )
        self.assertNotEqual(m1, m2)

    def test_different_isbn_numbers_all_other_fields_missing(self):
        m1 = ISBNMetadata(
            authors=[],
            language='',
            publisher='',
            isbn10=self.ISBN10_A,
            isbn13=self.ISBN13_A,
            title='',
            year=''
        )
        m2 = ISBNMetadata(
            authors=[],
            language='',
            publisher='',
            isbn10=self.ISBN10_B,
            isbn13=self.ISBN13_B,
            title='',
            year=''
        )
        self.assertNotEqual(m1, m2)

    def test_comparison_of_live_isbn_metadata(self):
        m1 = ISBNMetadata(
            authors=['Zhong Li', 'Wolfgang A. Halang', 'Guanrong Chen'],
            language='eng',
            publisher='Springer',
            isbn10='3540268995',
            isbn13='9783540268994',
            title='Integration Of Fuzzy Logic And Chaos Theory',
            year='2006'
        )
        m2 = ISBNMetadata(
            authors=['Wesley Chu', 'Tsau Young Lin'],
            language='eng',
            publisher='Springer',
            isbn10='3540250573',
            isbn13='9783540250579',
            title='Foundations And Advances In Data Mining',
            year='2005'
        )
        m3 = ISBNMetadata(
            authors=['Mircea Gh. Negoita', 'Bernd Reusch'],
            language='eng',
            publisher='Springer',
            isbn10='3540250069',
            isbn13='9783540250067',
            title='Real World Applications Of Computational Intelligence',
            year='2005'
        )
        self.assertNotEqual(m1, m2)
        self.assertNotEqual(m1, m3)
        self.assertNotEqual(m2, m3)

    def test_comparison_of_metadata_with_et_al_authors_title_case_change(self):
        m1 = ISBNMetadata(
            authors=['Zhong Li', 'Wolfgang A. Halang', 'Guanrong Chen'],
            language='eng',
            publisher='Springer',
            isbn10='3540268995',
            isbn13='9783540268994',
            title='Integration Of Fuzzy Logic And Chaos Theory',
            year='2006'
        )
        m2 = ISBNMetadata(
            authors=['Zhong Li', 'et.al.'],
            language='eng',
            publisher='Springer',
            isbn10='3540268995',
            isbn13='9783540268994',
            title='Integration Of Fuzzy Logic And Chaos Theory',
            year='2006'
        )
        m3 = ISBNMetadata(
            authors=['Zhong Li', 'et.al.'],
            language='eng',
            publisher='Springer',
            isbn10='3540268995',
            isbn13='9783540268994',
            title='Integration of Fuzzy Logic and Chaos Theory',
            year='2006'
        )
        self.assertEqual(m1, m2)
        self.assertEqual(m1, m3)

    def test_comparison_of_metadata_with_different_author_ordering(self):
        m1 = ISBNMetadata(
            authors=['Zhong Li', 'Wolfgang A. Halang', 'Guanrong Chen'],
            language='eng',
            publisher='Springer',
            isbn10='3540268995',
            isbn13='9783540268994',
            title='Integration Of Fuzzy Logic And Chaos Theory',
            year='2006'
        )
        m2 = ISBNMetadata(
            authors=['Guanrong Chen', 'Wolfgang A. Halang', 'Zhong Li'],
            language='eng',
            publisher='Springer',
            isbn10='3540268995',
            isbn13='9783540268994',
            title='Integration Of Fuzzy Logic And Chaos Theory',
            year='2006'
        )
        self.assertEqual(m1, m2)

    def test_comparison_of_live_isbn_metadata_2(self):
        m0 = ISBNMetadata(
            authors=['Spiros Sirmakessis'],
            language='eng',
            publisher='Springer',
            isbn10='3540250700',
            isbn13='9783540250708',
            title='Knowledge Mining Proceedings Of The NEMIS 2004 Final Conference',
            year='2005'
        )
        m1 = ISBNMetadata(
            authors=['Bogdan Gabrys'],
            language='eng',
            publisher='Springer',
            isbn10='3540240772',
            isbn13='9783540240778',
            title='Do Smart Adaptive Systems Exist?: Best Practice For Selection And Combination Of Intelligent Methods',
            year='2005'
        )
        m2 = ISBNMetadata(
            authors=['Larry Bull', 'Tim Kovacs'],
            language='eng',
            publisher='Springer',
            isbn10='3540250735',
            isbn13='9783540250739',
            title='Foundations Of Learning Classifier Systems',
            year='2005'
        )
        m3 = ISBNMetadata(
            authors=['Wesley Chu', 'Tsau Young Lin'],
            language='eng',
            publisher='Springer',
            isbn10='3540250573',
            isbn13='9783540250579',
            title='Foundations And Advances In Data Mining',
            year='2005'
        )

        m4 = ISBNMetadata(
            authors=['Zhong Li', 'Wolfgang A. Halang', 'Guanrong Chen'],
            language='eng',
            publisher='Springer',
            isbn10='3540268995',
            isbn13='9783540268994',
            title='Integration Of Fuzzy Logic And Chaos Theory',
            year='2006'
        )
        m5 = ISBNMetadata(
            authors=['Ana María Gil Lafuente'],
            language='eng',
            publisher='Springer',
            isbn10='3540232133',
            isbn13='9783540232131',
            title='Fuzzy Logic In Financial Analysis',
            year='2005'
        )
        m6 = ISBNMetadata(
            authors=['Udo Seiffert', 'Patrick Schweizer'],
            language='eng',
            publisher='Springer',
            isbn10='3540229019',
            isbn13='9783540229018',
            title='Bioinformatics Using Computational Intelligence Paradigms',
            year='2005'
        )
        m7 = ISBNMetadata(
            authors=['Mircea Gh. Negoita', 'Daniel Neagu', 'Vasile Palade'],
            language='eng',
            publisher='Springer',
            isbn10='3540232192',
            isbn13='9783540232193',
            title='Computational Intelligence: Engineering Of Hybrid Systems',
            year='2005'
        )
        m8 = ISBNMetadata(
            authors=['Nadia Nedjah', 'Luiza de Macedo Mourelle'],
            language='eng',
            publisher='Springer',
            isbn10='354025322X',
            isbn13='9783540253228',
            title='Fuzzy Systems Engineering: Theory And Practice',
            year='2005'
        )
        m9 = ISBNMetadata(
            authors=['Claude Ghaoui'],
            language='eng',
            publisher='Springer',
            isbn10='354025045X',
            isbn13='9783540250456',
            title='Knowledge-Based Virtual Education: User-Centred Paradigms',
            year='2005'
        )
        m10 = ISBNMetadata(
            authors=['John N. Mordeson', 'Kiran R. Bhutani', 'A. Rosenfeld'],
            language='eng',
            publisher='Springer',
            isbn10='3540250727',
            isbn13='9783540250722',
            title='Fuzzy Group Theory',
            year='2005'
        )
        m11 = ISBNMetadata(
            authors=['Mircea Gh. Negoita', 'Bernd Reusch'],
            language='eng',
            publisher='Springer',
            isbn10='3540250069',
            isbn13='9783540250067',
            title='Real World Applications Of Computational Intelligence',
            year='2005'
        )
        unique_isbn_metadata = set()
        unique_isbn_metadata.add(m0)
        unique_isbn_metadata.add(m1)
        unique_isbn_metadata.add(m2)
        unique_isbn_metadata.add(m3)
        unique_isbn_metadata.add(m4)
        unique_isbn_metadata.add(m5)
        unique_isbn_metadata.add(m6)
        unique_isbn_metadata.add(m7)
        unique_isbn_metadata.add(m8)
        unique_isbn_metadata.add(m9)
        unique_isbn_metadata.add(m10)
        unique_isbn_metadata.add(m11)
        self.assertEqual(12, len(unique_isbn_metadata))


@skipIf(*ISBNLIB_IS_NOT_AVAILABLE)
class TestExtractEbookISBNsInText(TestCase):
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
        actual = extract_ebook_isbns_from_text(text)
        self.assertIn('9783540762881', actual)


@skipIf(*ISBNLIB_IS_NOT_AVAILABLE)
class TestMalformedISBNMetadata(TestCase):
    def test_malformed_author_field_list_of_lists(self):
        actual = ISBNMetadata(
            authors=['Stephen Wynkoop [Chris Lester]'],
            language='eng',
            publisher='Que',
            title='Special Edition Using Microsoft SQL Server 6.5',
            year='1997',
            isbn13='9780789711175'
        )

        _expected_authors = ['Stephen Wynkoop', 'Chris Lester']
        expect = ISBNMetadata(
            authors=_expected_authors,
            language='eng',
            publisher='Que',
            title='Special Edition Using Microsoft SQL Server 6.5',
            year='1997',
            isbn13='9780789711175'
        )
        self.assertEqual(expect, actual)
        self.assertEqual(_expected_authors, actual.authors)

    def test_malformed_author_field_list_of_lists_with_and(self):
        actual = ISBNMetadata(
            authors=['Stephen Wynkoop [and Chris Lester]'],
            language='eng',
            publisher='Que',
            title='Special Edition Using Microsoft SQL Server 6.5',
            year='1997',
            isbn13='9780789711175'
        )

        _expected_authors = ['Stephen Wynkoop', 'Chris Lester']
        expect = ISBNMetadata(
            authors=_expected_authors,
            language='eng',
            publisher='Que',
            title='Special Edition Using Microsoft SQL Server 6.5',
            year='1997',
            isbn13='9780789711175'
        )
        self.assertEqual(expect, actual)
        self.assertEqual(_expected_authors, actual.authors)
