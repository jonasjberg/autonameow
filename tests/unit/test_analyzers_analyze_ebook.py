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

from itertools import permutations
from unittest import skipIf, TestCase
from unittest.mock import Mock

try:
    import isbnlib
except ImportError:
    ISBNLIB_IS_NOT_AVAILABLE = True, 'Missing (failed to import) required module "isbnlib"'
else:
    ISBNLIB_IS_NOT_AVAILABLE = False, ''

import unit.utils as uu
from analyzers.analyze_ebook import calculate_authors_similarity
from analyzers.analyze_ebook import calculate_title_similarity
from analyzers.analyze_ebook import deduplicate_isbns
from analyzers.analyze_ebook import EbookAnalyzer
from analyzers.analyze_ebook import extract_ebook_isbns_from_text
from analyzers.analyze_ebook import extract_isbns_from_text
from analyzers.analyze_ebook import filter_isbns
from analyzers.analyze_ebook import ISBNMetadata


def _get_ebook_analyzer(fileobject):
    return EbookAnalyzer(
        fileobject=fileobject,
        config=Mock(),
        request_data_callback=Mock()
    )


@skipIf(*ISBNLIB_IS_NOT_AVAILABLE)
class TestEbookAnalyzer(TestCase):
    @classmethod
    def setUpClass(cls):
        class DummyFileObject(object):
            def __init__(self, mime, basename_suffix):
                self.mime_type = mime
                self.basename_suffix = basename_suffix

            def __repr__(self):
                return '<DummyFileObject({!s}, {!s})>'.format(
                    self.mime_type, self.basename_suffix
                )

        cls.file_objects_not_handled = [
            DummyFileObject('application/octet-stream', 'o'),
            DummyFileObject('application/octet-stream', 'exe'),
            DummyFileObject('image/jpeg', 'jpg'),
            DummyFileObject('text/plain', 'txt'),
        ]
        cls.file_objects_handled = [
            DummyFileObject('application/epub+zip', b'epub'),
            DummyFileObject('application/octet-stream', b'azw'),
            DummyFileObject('application/octet-stream', b'azw3'),
            DummyFileObject('application/octet-stream', b'azw4'),
            DummyFileObject('application/octet-stream', b'mobi'),
            DummyFileObject('application/pdf', b'pdf'),
            DummyFileObject('image/vnd.djvu', b'djvu'),
        ]

    def setUp(self):
        self.fileobject = uu.get_named_fileobject('2010-01-31_161251.jpg')
        self.analyzer = _get_ebook_analyzer(self.fileobject)

    def test_setup(self):
        self.assertIsNotNone(self.fileobject)
        self.assertIsNotNone(self.analyzer)

    def test_can_handle_returns_false_as_expected(self):
        for dummy_file_object in self.file_objects_not_handled:
            with self.subTest(fo=dummy_file_object):
                self.assertFalse(self.analyzer.can_handle(dummy_file_object))

    def test_can_handle_returns_true_as_expected(self):
        for dummy_file_object in self.file_objects_handled:
            with self.subTest(fo=dummy_file_object):
                self.assertTrue(self.analyzer.can_handle(dummy_file_object))


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

    def test_deduplicates_equivalent_isbn13_and_isbn10_numbers(self):
        self._assert_that_it(
            returns=['9780387303031'],
            given=['0387303030', '9780387303031']
        )
        self._assert_that_it(
            returns=['9783540762881', '9783540762874'],
            given=['3540762884', '3540762876', '9783540762881', '9783540762874']
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
            [None],
            [''],
            ['1111111111'],
            ['9999999999'],
        ]
        for sample_isbn in sample_invalid_isbns:
            actual = filter_isbns(sample_isbn, self.BLACKLISTED_ISBN_NUMBERS)
            self.assertEqual(actual, [])


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

    def test_comparison_of_live_isbn_metadata_3(self):
        m0 = ISBNMetadata(
            authors=['Stephen G. Kochan'],
            language='eng',
            publisher='Addison-Wesley',
            isbn10='0321967607',
            isbn13='9780321967602',
            title='Programming In Objective-C',
            year='2014'
        )
        m1 = ISBNMetadata(
            authors=['Stephen G. Kochan'],
            language='eng',
            publisher='Addison-Wesley',
            isbn10='0321776410',
            isbn13='9780321776419',
            title='Programming In C',
            year='2013'
        )
        self.assertNotEqual(m0, m1)
        unique_isbn_metadata = set()
        unique_isbn_metadata.add(m0)
        unique_isbn_metadata.add(m1)
        self.assertEqual(2, len(unique_isbn_metadata))

    def test_comparison_of_live_isbn_metadata_4(self):
        m0 = ISBNMetadata(
            authors=['Gilbert Strang'],
            language='eng',
            publisher='WellesleyCambridge',
            isbn10='0980232740',
            isbn13='9780980232745',
            title='Calculus',
            year='2010'
        )
        m1 = ISBNMetadata(
            authors=['Gilbert Strang', 'Truong Nguyen'],
            language='eng',
            publisher='WellesleyCambridge',
            isbn10='0961408871',
            isbn13='9780961408879',
            title='Wavelets And Filter Banks',
            year='1997'
        )
        self.assertNotEqual(m0, m1)
        unique_isbn_metadata = set()
        unique_isbn_metadata.add(m0)
        unique_isbn_metadata.add(m1)
        self.assertEqual(2, len(unique_isbn_metadata))

    def test_comparison_of_live_isbn_metadata_5(self):
        mx = ISBNMetadata(
            authors=['Robert Shimonski', 'Will Schmied'],
            language='eng',
            publisher='Syngress',
            isbn10='1931836884',
            isbn13='9781931836883',
            title='Building DMZs For Enterprise Networks: [Design, Deploy, And Maintain A Secure DMZ On Your Network ; Build DMZ Segments Using Cisco PIX Firewalls, Check Point NG, Nokia, And Microsoft ISA Server 2000 ; Learn DMZ Security Measures: Reconnaissance, Penetration Testing, DMZ Hardening, And More ; Plan And Design A Wireless DMZ ; Bonus Chapter On IIS Web Server Hardening Available From Syngress.Com]',
            year='2003'
        )
        m0 = ISBNMetadata(
            authors=['Doug Maxwell'],
            language='eng',
            publisher='Syngress',
            isbn10='1931836701',
            isbn13='9781931836708',
            title='Nokia Network Security Solutions Handbook',
            year='2002'
        )
        m1 = ISBNMetadata(
            authors=['Syngress'],
            language='eng',
            publisher='Syngress',
            isbn10='1931836841',
            isbn13='9781931836845',
            title='MCSE/MCSA Implementing & Administering Security In A Windows 2000 Network (Exam 70-214): Study Guide And DVD Training System',
            year='2003'
        )
        m2 = ISBNMetadata(
            authors=['Melissa Craft'],
            language='eng',
            publisher='Syngress',
            isbn10='1928994601',
            isbn13='9781928994602',
            title='Windows 2000 Active Directory',
            year='2001'
        )
        m3 = ISBNMetadata(
            authors=['Drew Simonis'],
            language='eng',
            publisher='Syngress',
            isbn10='1928994741',
            isbn13='9781928994749',
            title='Check Point NG: Next Generation Security Administration ; [Bonus Coverage Of CCSA NG Exam 156-210 Objectives]',
            year='2002'
        )
        m4 = ISBNMetadata(
            authors=['Robert J. Shimonski', 'Wally Eaton', 'Umer Khan'],
            language='eng',
            publisher='Syngress',
            isbn10='1931836574',
            isbn13='9781931836579',
            title='Sniffer Pro Network Optimization & Troubleshooting Handbook',
            year='2002'
        )
        m5 = ISBNMetadata(
            authors=['Thomas W. Shinder', 'Debra Littlejohn Shinder', 'Martin Grasdal'],
            language='eng',
            publisher='Syngress',
            isbn10='1931836663',
            isbn13='9781931836661',
            title='ISA Server And Beyond Real World Security Solutions For Microsoft Enterprise Networks',
            year='2002'
        )
        m6 = ISBNMetadata(
            authors=['Norris L. Johnson', 'Jr.', 'Robert J. Shimonski'],
            language='eng',
            publisher='Syngress',
            isbn10='1931836728',
            isbn13='9781931836722',
            title='Security+: Study Guide & DVD Training System',
            year='2002'
        )
        unique_isbn_metadata = set()
        unique_isbn_metadata.add(mx)
        unique_isbn_metadata.add(m0)
        unique_isbn_metadata.add(m1)
        unique_isbn_metadata.add(m2)
        unique_isbn_metadata.add(m3)
        unique_isbn_metadata.add(m4)
        unique_isbn_metadata.add(m5)
        unique_isbn_metadata.add(m6)
        self.assertEqual(8, len(unique_isbn_metadata))

        self.assertNotEqual(mx, m0)
        self.assertNotEqual(mx, m1)
        self.assertNotEqual(mx, m2)
        self.assertNotEqual(mx, m3)
        self.assertNotEqual(mx, m4)
        self.assertNotEqual(mx, m5)
        self.assertNotEqual(mx, m6)


@skipIf(*ISBNLIB_IS_NOT_AVAILABLE)
class TestExtractEbookISBNsFromText(TestCase):
    def _assert_returns(self, expected, given):
        actual = extract_ebook_isbns_from_text(given)
        self.assertEqual(expected, actual)

    def test_finds_expected_in_multiline_text_with_two_isbn_numbers(self):
        self._assert_returns(['9783540762881'],
                             given='''Computational Intelligence

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
''')

    def test_finds_expected_with_parenthesis_electronic_suffix(self):
        self._assert_returns(['9781484233184'],
                             given='ISBN (electronic): 978-1-4842-3318-4')

    def test_finds_expected_in_multiline_text_with_parenthesis_electronic_suffix(self):
        self._assert_returns(['9781484233184'],
                             given='''ISBN-13 (pbk): 978-1-4842-3317-7
https://doi.org/10.1007/978-1-4842-3318-4

ISBN-13 (electronic): 978-1-4842-3318-4

''')


@skipIf(*ISBNLIB_IS_NOT_AVAILABLE)
class TestExtractISBNsFromText(TestCase):
    def _assert_returns(self, expected, given):
        actual = extract_isbns_from_text(given)
        self.assertEqual(expected, actual)

    def test_find_expected_in_ocr_text_with_one_invalid_character(self):
        self.skipTest('TODO: Clean up invalid characters in OCR text')
        self._assert_returns(['0486650383'],
                             given='''I. Mathematical analysis. I. Title.
QAaOO.R63 1986
516
86-25300
ISBN 0-486-6&038-3 (pbk.)
''')

    def test_find_expected_in_ocr_text_with_multiple_invalid_characters(self):
        self.skipTest('TODO: Detect and replace 0488 should be 0486 ')
        self._assert_returns(['0486650383'],
                             given='''I. Mathematical analysis. I. Title.
QAaOO.R63 1986
516
86-25300
ISBN 0-488-6&038-3 (pbk.)
''')


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


class TestCalculateAuthorsSimilarity(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.LOW_SIMILARITY_THRESHOLD = 0.25
        cls.HIGH_SIMILARITY_THRESHOLD = 0.75

    def _assert_similarity(self, expected, authors_a, authors_b):
        actual = calculate_authors_similarity(authors_a, authors_b)
        self.assertEqual(expected, actual)

    def _assert_low_similarity(self, authors_a, authors_b):
        actual = calculate_authors_similarity(authors_a, authors_b)
        self.assertLessEqual(actual, self.LOW_SIMILARITY_THRESHOLD)

    def _assert_high_similarity(self, authors_a, authors_b):
        actual = calculate_authors_similarity(authors_a, authors_b)
        self.assertGreaterEqual(actual, self.HIGH_SIMILARITY_THRESHOLD)

    def test_expect_maximum_similarity_for_identical_authors(self):
        for authors_names_A, authors_names_B in [
            (['a'],       ['a']),
            (['A'],       ['a']),
            (['a'],       ['A']),
            (['foo'],     ['foo']),
            (['foo'],     ['Foo']),
            (['foo bar'], ['foo bar']),
            (['foo bar'], ['Foo bar']),
            (['foo bar'], ['Foo Bar']),
        ]:
            self._assert_similarity(1.0, authors_names_A, authors_names_B)

    def test_expect_high_similarity_for_similar_authors(self):
        self._assert_high_similarity(['Foo Bar'],   ['Fo Bar'])
        self._assert_high_similarity(['foo bar'],   ['foo barr'])
        self._assert_high_similarity(['nietzsche'], ['nietzsche f'])
        self._assert_high_similarity(['nietzsche'], ['f. nietzsche'])
        self._assert_high_similarity(['meemaw'],    ['MEEMAW'])
        self._assert_high_similarity(['Meemaw'],    ['Meemaw'])
        self._assert_high_similarity(['Meemaw'],    ['Meeoaw'])

    def test_identical_authors_but_different_counts_should_be_similar(self):
        self._assert_high_similarity(['gilbert strang'],                  ['gilbert strang', 'truong nguyen'])
        self._assert_high_similarity(['gilbert strang'],                  ['truong nguyen', 'gilbert strang'])
        self._assert_high_similarity(['gilbert strang', 'truong nguyen'], ['gilbert strang'])
        self._assert_high_similarity(['truong nguyen', 'gilbert strang'], ['gilbert strang'])

    def test_expect_low_similarity_for_completely_different_authors(self):
        self._assert_low_similarity(['aaa bbb'],       ['zzz xxx'])
        self._assert_low_similarity(['aaa'],           ['xxx'])
        self._assert_low_similarity(['gibson'],        ['smulan'])
        self._assert_low_similarity(['gibson smulan'], ['nietzsche kant'])
        self._assert_low_similarity(['nietzsche'],     ['kant'])
        self._assert_low_similarity(['Meemaw'],        ['grandmother'])

    def test_expect_high_similarity_for_same_authors_in_different_order(self):
        self._assert_high_similarity(
            ['Jan Reesch', 'Grayham Murroy', 'Vadin Ogievetsky', 'Joe Lawnery'],
            ['Jan Reesch', 'Grayham Murroy', 'Joe Lawnery', 'Vadin Ogievetsky']
        )
        self._assert_high_similarity(
            ['Grayham Murroy', 'Jan Reesch', 'Vadin Ogievetsky', 'Joe Lawnery'],
            ['Jan Reesch', 'Grayham Murroy', 'Joe Lawnery', 'Vadin Ogievetsky']
        )
        self._assert_high_similarity(
            ['Grayham Murroy', 'Jan Reesch', 'Vadin Ogievetsky', 'Joe Lawnery'],
            ['Joe Lawnery', 'Grayham Murroy', 'Vadin Ogievetsky', 'Jan Reesch']
        )

    def test_high_similarity_for_same_author_with_swapped_first_last_name(self):
        self._assert_high_similarity(['Lu, Chun-Shien'], ['Chun-Shien Lu'])
        self._assert_high_similarity(['Chun-Shien Lu'], ['Lu, Chun-Shien'])

    def test_high_similarity_for_authors_with_swapped_first_last_names(self):
        self._assert_high_similarity(
            ['Reesch J.', 'Murroy G.', 'Ogievetsky V.', 'Lawnery J.'],
            ['J. Reesch', 'G. Murroy', 'V. Ogievetsky', 'J. Lawnery']
        )
        self._assert_high_similarity(
            ['Reesch J.', 'Murroy G.', 'Ogievetsky V.', 'Lawnery J.'],
            ['Reesch J.', 'G. Murroy', 'Ogievetsky V.', 'J. Lawnery']
        )

    def test_high_similarity_for_authors_with_swapped_first_last_names_any_order(self):
        for given_authors_A, given_authors_B in zip(
            permutations(['Reesch J.', 'Murroy G.', 'Ogievetsky V.', 'Lawnery J.'], 4),
            permutations(['J. Reesch', 'G. Murroy', 'V. Ogievetsky', 'J. Lawnery'], 4)
        ):
            self._assert_high_similarity(given_authors_A, given_authors_B)


class TestCalculateTitleSimilarity(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.LOW_SIMILARITY_THRESHOLD = 0.4
        cls.HIGH_SIMILARITY_THRESHOLD = 0.6
        cls.SAMPLE_TITLES = [
            'isa server and beyond real world security solutions for microsoft enterprise networks',
            'hack proofing your network',
            'windows 2000 active directory',
            'configuring isa 2000 server building firewalls for windows 2000',
            'sniffer pro network optimization and troubleshooting handbook',
            'mcsemcsa implementing and administering security in a windows 2000 network exam 70214 study guide and dvd training system',
            'cisco security specialists guide to pix firewalls',
            'check point ng next generation security administration  bonus coverage of ccsa ng exam 156210 objectives',
            'hack proofing sun solaris 8',
            'nokia network security solutions handbook',
            'hack proofing windows 2000 server',
            'sscp study guide and dvd training system',
        ]
        long_title_parts = 'building dmzs for enterprise networks| design deploy and maintain a secure dmz on your network|  build dmz segments using cisco pix firewalls check point ng nokia and microsoft isa server 2000|  learn dmz security measures reconnaissance penetration testing dmz hardening and more|  plan and design a wireless dmz'.split('|')
        cls.INCREASINGLY_LONG_TITLE = list()
        for num_parts in range(0, len(long_title_parts)):
            long_title = ''.join(long_title_parts[:num_parts + 1])
            cls.INCREASINGLY_LONG_TITLE.append(long_title)

    def _assert_similarity(self, expected, title_a, title_b):
        actual = calculate_title_similarity(title_a, title_b)
        self.assertEqual(expected, actual)

    def _assert_low_similarity(self, title_a, title_b):
        actual = calculate_title_similarity(title_a, title_b)
        self.assertLessEqual(actual, self.LOW_SIMILARITY_THRESHOLD)

    def _assert_high_similarity(self, title_a, title_b):
        actual = calculate_title_similarity(title_a, title_b)
        self.assertGreaterEqual(actual, self.HIGH_SIMILARITY_THRESHOLD)

    def test_expect_maximum_similarity_for_identical_titles(self):
        for given_title in [
            'a',
            'foo',
            'foo bar',
            'foo bar baz',
            self.INCREASINGLY_LONG_TITLE[0],
        ]:
            self._assert_similarity(1.0, given_title, given_title)

    def test_expect_low_similarity_for_different_titles(self):
        for given_title in self.SAMPLE_TITLES:
            with self.subTest(given_title=given_title):
                self._assert_low_similarity(self.INCREASINGLY_LONG_TITLE[0], given_title)

    def test_expect_low_similarity_when_comparing_all_sample_titles(self):
        for given_title_A, given_title_B in permutations(self.SAMPLE_TITLES, 2):
            self.assertNotEqual(given_title_A, given_title_B)
            with self.subTest(given_title_A=given_title_A, given_title_B=given_title_B):
                self._assert_low_similarity(given_title_A, given_title_B)

    def test_expect_high_similarity_for_similar_titles(self):
        self.assertEqual(self.INCREASINGLY_LONG_TITLE[0], 'building dmzs for enterprise networks')
        for given_title in self.INCREASINGLY_LONG_TITLE:
            with self.subTest(given_title=given_title):
                self._assert_high_similarity(self.INCREASINGLY_LONG_TITLE[0], given_title)

    def test_expect_titles_with_common_substring_to_be_considered_more_similar(self):
        reference = 'building dmzs for enterprise networks'
        for given_title_B in self.SAMPLE_TITLES:
            for given_title_C in self.INCREASINGLY_LONG_TITLE:
                sim_bad = calculate_title_similarity(reference, given_title_B)
                sim_good = calculate_title_similarity(reference, given_title_C)
                with self.subTest(given_title_B=given_title_B, given_title_C=given_title_C):
                    self.assertGreater(sim_good, sim_bad)
