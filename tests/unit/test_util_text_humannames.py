# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2019 Jonas Sjöberg <autonameow@jonasjberg.com>
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

import itertools
import unittest
from collections import namedtuple
from unittest import TestCase

import nameparser
from util.text.humannames import filter_multiple_names
from util.text.humannames import filter_name
from util.text.humannames import format_name
from util.text.humannames import format_name_list
from util.text.humannames import HumanNameFormatter
from util.text.humannames import HumanNameParser
from util.text.humannames import LastNameInitialsFormatter
from util.text.humannames import normalize_letter_case
from util.text.humannames import preprocess_names
from util.text.humannames import split_multiple_names
from util.text.humannames import strip_author_et_al
from util.text.humannames import strip_edited_by
from util.text.humannames import strip_foreword_by
from util.text.humannames import strip_repeating_periods
from util.text.humannames import _parse_name


TD = namedtuple('TD', 'given expect')

TESTDATA_NAME_LASTNAME_INITIALS = [
    # Special cases
    TD(given='', expect=''),
    TD(given=' ', expect=''),
    TD(given='G', expect='G.'),

    # First name only
    TD(given='Gibson', expect='G.'),
    TD(given='Jonas', expect='J.'),

    # First, last
    TD(given='Gibson Sjöberg', expect='Sjöberg G.'),
    TD(given='Zhiguo Gong', expect='Gong Z.'),
    TD(given='Di Zou', expect='Zou D.'),
    TD(given='Muhammad Younas', expect='Younas M.'),
    TD(given='Katt Smulan', expect='Smulan K.'),
    TD(given='Irfan Awan', expect='Awan I.'),
    TD(given='Natalia Kryvinska', expect='Kryvinska N.'),
    TD(given='Christine Strauss', expect='Strauss C.'),
    TD(given='Yimin Wei', expect='Wei Y.'),
    TD(given='Weiyang Ding', expect='Ding W.'),
    TD(given='Russell, Bertrand', expect='Russell B.'),
    TD(given='Bertrand Russell', expect='Russell B.'),

    # First, compound last
    TD(given='Do van Thanh', expect='Thanh D.v.'),
    TD(given='David Simchi-Levi', expect='Simchi-Levi D.'),

    # First, middle, last
    TD(given='Gibson Mjau Sjöberg', expect='Sjöberg G.M.'),
    TD(given='Hatt Katt Smulan', expect='Smulan H.K.'),

    TD(given='Friedrich Wilhelm Nietzsche', expect='Nietzsche F.W.'),
    TD(given='Nietzsche, Friedrich Wilhelm', expect='Nietzsche F.W.'),

    # First, middle, middle, last
    TD(given='Gibson Mjau Mjao Sjöberg', expect='Sjöberg G.M.M.'),

    # Various Titles
    TD(given='Sir Gibson Mjau Mjao Sjöberg', expect='Sjöberg G.M.M.'),
    TD(given='Lord Gibson Mjau Mjao Sjöberg', expect='Sjöberg G.M.M.'),
    TD(given='Catness Gibson Mjau Mjao Sjöberg', expect='Sjöberg C.G.M.M.'),
    TD(given='Sir Catness Gibson Mjau Mjao Sjöberg', expect='Sjöberg C.G.M.M.'),

    # First. middle initial and last
    TD(given='David B. Makofske', expect='Makofske D.B.'),
    TD(given='Michael J. Donahoo', expect='Donahoo M.J.'),
    TD(given='Kenneth L. Calvert', expect='Calvert K.L.'),
    TD(given='William T. Ziemba', expect='Ziemba W.T.'),
    TD(given='Raymond G. Vickson', expect='Vickson R.G.'),

    # First. middle initial, middle initial, last
    TD(given='Dickson K. W. Chiu', expect='Chiu D.K.W.'),

    # First. middle initial, compound last
    TD(given='Antonio J. Tallon-Ballesteros', expect='Tallon-Ballesteros A.J.'),
    TD(given='Tallon-Ballesteros A.J.', expect='Tallon-Ballesteros A.J.'),

    # Input in output format
    TD(given='Makofske D.B.', expect='Makofske D.B.'),
    TD(given='Donahoo M.J.', expect='Donahoo M.J.'),
    TD(given='Calvert K.L.', expect='Calvert K.L.'),
    TD(given='Gong Z.', expect='Gong Z.'),
    TD(given='Chiu D.K.W.', expect='Chiu D.K.W.'),
    TD(given='Zou D.', expect='Zou D.'),
    TD(given='Younas M.', expect='Younas M.'),
    TD(given='Smulan K.', expect='Smulan K.'),
    TD(given='Smulan H.K.', expect='Smulan H.K.'),
    TD(given='Awan I.', expect='Awan I.'),
    TD(given='Kryvinska N.', expect='Kryvinska N.'),
    TD(given='Strauss C.', expect='Strauss C.'),
    TD(given='vanThanh D.V.', expect='vanThanh D.V.'),
    TD(given='Thanh D.V.', expect='Thanh D.V.'),
    TD(given='Ziemba W.T.', expect='Ziemba W.T.'),
    TD(given='Vickson R.G.', expect='Vickson R.G.'),
    TD(given='Wei Y.', expect='Wei Y.'),
    TD(given='Ding W.', expect='Ding W.'),
    TD(given='Russell B.', expect='Russell B.'),
    TD(given='Simchi-Levi D.', expect='Simchi-Levi D.'),
    TD(given='DeDecker B.', expect='Dedecker B.'),

    # Multiple authors; et al.
    TD(given='Steve Anson ... [et al.]', expect='Anson S.'),
    TD(given='Steve Anson, et al.', expect='Anson S.'),
    TD(given='Steve Anson, ... et al.', expect='Anson S.'),
    TD(given='Steve Anson, ... et al', expect='Anson S.'),
    TD(given='Steve Anson ... et al', expect='Anson S.'),
    TD(given='Steve Anson ... [et al]', expect='Anson S.'),
    TD(given='Steve Anson ... [et al.]', expect='Anson S.'),

    # Failed special cases
    TD(given='Regina O. Obe', expect='Obe R.O.'),
    TD(given='Le Minh Nguyen', expect='Nguyen L.M.'),
    TD(given='Shiva Prasad K.', expect='Prasad S.K.'),
    TD(given='Shiva Prasad K.M.', expect='Prasad S.K.M.'),
    TD(given='Florin Popentiu-Vladicescu', expect='Popentiu-Vladicescu F.'),
    TD(given='I. Bronsh', expect='Bronsh I.'),
    TD(given='I.N. Bronsh', expect='Bronsh I.N.'),
    TD(given='Bronsh I.', expect='Bronsh I.'),
    TD(given='Bronsh I.N.', expect='Bronsh I.N.'),
    TD(given='Bart de Decker', expect='deDecker B.'),
    TD(given='Bart De Decker', expect='deDecker B.'),
]

TESTDATA_LIST_OF_NAMES_LASTNAME_INITIALS = [
    TD(given=['David B. Makofske', 'Michael J. Donahoo',
              'Kenneth L. Calvert'],
       expect=['Calvert K.L.', 'Donahoo M.J.', 'Makofske D.B.']),

    TD(given=['Zhiguo Gong', 'Dickson K. W. Chiu', 'Di Zou'],
       expect=['Chiu D.K.W.', 'Gong Z.', 'Zou D.']),

    TD(given=['Muhammad Younas', 'Irfan Awan', 'Natalia Kryvinska',
              'Christine Strauss', 'Do van Thanh'],
       expect=['Awan I.', 'Kryvinska N.', 'Strauss C.', 'Thanh D.v.',
               'Younas M.']),

    TD(given=['William T. Ziemba', 'Raymond G. Vickson'],
       expect=['Vickson R.G.', 'Ziemba W.T.']),

    TD(given=['Yimin Wei', 'Weiyang Ding'],
       expect=['Ding W.', 'Wei Y.']),

    TD(given=['Charles Miller', 'Dino Dai Zovi'],
       expect=['Miller C.', 'Zovi D.D.']),

    TD(given=['Chrisina Jayne', 'Lazaros Iliadis'],
       expect=['Iliadis L.', 'Jayne C.']),

    TD(given=['Nihad Ahmad Hassan', 'Rami Hijazi'],
       expect=['Hassan N.A.', 'Hijazi R.']),

    TD(given=['David Simchi-Levi', 'Xin Chen', 'Julien Bramel'],
       expect=['Bramel J.', 'Chen X.', 'Simchi-Levi D.']),

    TD(given=['Hujun Yin', 'Yang Gao', 'Bin Li', 'Daoqiang Zhang',
              'Ming Yang', 'Yun Li', 'Frank Klawonn',
              'Antonio J. Tallon-Ballesteros'],
       expect=['Gao Y.', 'Klawonn F.', 'Li B.', 'Li Y.',
               'Tallon-Ballesteros A.J.', 'Yang M.', 'Yin H.', 'Zhang D.']),

    TD(given=['Benjamin Bearkins', 'Jacob Rock Hammer', 'Jam M. Raid'],
       expect=['Bearkins B.', 'Hammer J.R.', 'Raid J.M.']),
    TD(given=['Subhransu Sekhar Dash', 'Swagatam Das', 'Bijaya Ketan Panigrahi'],
       expect=['Das S.', 'Dash S.S.', 'Panigrahi B.K.']),
    TD(given=['Syed Faraz Hasan', 'Nazmul Siddique', 'Shyam Chakraborty'],
       expect=['Chakraborty S.', 'Hasan S.F.', 'Siddique N.']),
    TD(given=['Elias Kyriakides', 'Marios Polycarpou'],
       expect=['Kyriakides E.', 'Polycarpou M.']),

    # Failed special cases
    TD(given=['Regina O. Obe', 'Leo S. Hsu'],
       expect=['Hsu L.S.', 'Obe R.O.']),
    TD(given=['Hermann Lödding', 'Ralph Riedel', 'Klaus-Dieter Thoben', 'Gregor von Cieminski', 'Dimitris Kiritsis'],
       expect=['Kiritsis D.', 'Lödding H.', 'Riedel R.', 'Thoben K.', 'vonCieminski G.']),
    TD(given=['Le Minh Nguyen', 'Bogdan Trawinski'],
       expect=['Nguyen L.M.', 'Trawinski B.']),
    TD(given=['Ngoc Thanh Nguyen', 'Satoshi Tojo', 'Le Minh Nguyen', 'Bogdan Trawinski'],
       expect=['Nguyen L.M.', 'Nguyen N.T.', 'Tojo S.', 'Trawinski B.']),
    TD(given=['M. Sreenivasa Reddy', 'K. Viswanath', 'Shiva Prasad K.M.'],
       expect=['Prasad S.K.M.', 'Reddy M.S.', 'Viswanath K.']),
    TD(given=['M. Sreenivasa Reddy', 'K. Viswanath', 'Shiva Prasad K.'],
       expect=['Prasad S.K.', 'Reddy M.S.', 'Viswanath K.']),
    TD(given=['Srikanta Patnaik', 'Florin Popentiu-Vladicescu'],
       expect=['Patnaik S.', 'Popentiu-Vladicescu F.']),
    TD(given=['I.N. Bronsh', 'K.A. Semandyayev', 'Gert Musiol', 'Steiner Mühlig'],
       expect=['Bronsh I.N.', 'Musiol G.', 'Mühlig S.', 'Semandyayev K.A.']),
    TD(given=['I.N. Bronsh', 'K. Semandyayev', 'Gert Musiol', 'Steiner Mühlig'],
       expect=['Bronsh I.N.', 'Musiol G.', 'Mühlig S.', 'Semandyayev K.']),
    TD(given=['I. Bronsh', 'K. Semandyayev', 'Gert Musiol', 'Steiner Mühlig'],
       expect=['Bronsh I.', 'Musiol G.', 'Mühlig S.', 'Semandyayev K.']),

    TD(given=['Johnson, Dean R.', 'Paymer, Carol A.', 'Chamberlain, Aaron P.'],
       expect=['Chamberlain A.P.', 'Johnson D.R.', 'Paymer C.A.']),

    TD(given=['Ivan Nunes Da Silva', 'Danilo Hernane Spatti',
              'Rogerio Andrade Flauzino', 'Luisa Helena Bartocci Liboni',
              'Silas Franco Dos Reis Alves'],
       expect=['Alves S.F.D.R.', 'DaSilva I.N.', 'Flauzino R.A.',
               'Liboni L.H.B.', 'Spatti D.H.']),

    TD(given=['Danilo P. Mandic'],
       expect=['Mandic D.P.']),
    # TD(given=['Vanessa Su Lee Goh'],
    #    expect=['Goh V.S.L.']),
    # TD(given=['Danilo P. Mandic', 'Vanessa Su Lee Goh'],
    #    expect=['Goh V.S.L.', 'Mandic D.P.']),

    TD(given=['M. N. S. Swamy'],
       expect=['Swamy M.N.S.']),
    TD(given=['Swamy M.N.S.'],
       expect=['Swamy M.N.S.']),

]


class TeststripAuthorEtAl(TestCase):
    def test_strips_trailing_variations_of_et_al(self):
        EXPECTED = 'Gibson Catberg'
        for given in [
            'Gibson Catberg, et al.',
            'Gibson Catberg, et al',
            'Gibson Catberg et al',
            'Gibson Catberg [et al]',
            'Gibson Catberg [et al.]',
            'Gibson Catberg {et al}',
            'Gibson Catberg {et al.}',
            'Gibson Catberg, ... et al.',
            'Gibson Catberg, ... et al',
            'Gibson Catberg ... et al',
            'Gibson Catberg ... [et al]',
            'Gibson Catberg ... [et al.]',
            'Gibson Catberg ... {et al}',
            'Gibson Catberg ... {et al.}',
            'Gibson Catberg ... [et al.]',
        ]:
            with self.subTest(given=given, expected=EXPECTED):
                actual = strip_author_et_al(given)
                self.assertEqual(EXPECTED, actual)

    def test_strips_trailing_variations_of_et_al_seen_in_live_data(self):
        def _assert_returns(expected, given):
            actual = strip_author_et_al(given)
            self.assertEqual(expected, actual)

        _assert_returns('Bart de Decker', 'Bart de Decker ... [et al.]')
        _assert_returns('Frederick Gallegos', 'Frederick Gallegos...[et al.]')
        _assert_returns('Eric Oberg', 'Eric Oberg ... [et al.]')
        _assert_returns('Steven Hanson', 'Steven Hanson ... [et al.]')
        _assert_returns('Jim L. Weaver', 'Jim L. Weaver ... [et al.]')


class TestStripEditedBy(TestCase):
    def test_returns_names_without_edited_by_variations_as_is(self):
        for given_and_expected in [
            'Armstrong, Edwin',
            'Byrd, Richard E.',
            'Cavell, Edith',
            'Edison, Thomas Alva',
            'Edite French',
            'Edite',
            'Edith Cavell',
            'Edith Piaf',
            'Edith',
            'Edith, P.',
            'Piaf, Edith',
            'Richard E. Byrd',
            'Thomas Alva Edison',
            'Thomas Edison',
        ]:
            actual = strip_edited_by(given_and_expected)
            self.assertEqual(given_and_expected, actual)

    def test_strips_leading_variations_of_edited_by(self):
        EXPECTED = 'Gibson Catberg'
        for given in [
            'ed. by Gibson Catberg',
            'Ed. by Gibson Catberg',
            'edited by Gibson Catberg',
            'Edited by Gibson Catberg',
            'Edited by Gibson Catberg',
        ]:
            with self.subTest(given=given, expected=EXPECTED):
                actual = strip_edited_by(given)
                self.assertEqual(EXPECTED, actual)

    def test_strips_trailing_variations_of_edited_by(self):
        EXPECTED = 'Gibson Catberg'
        for given in [
            'Gibson Catberg (Ed)',
            'Gibson Catberg (Ed.)',
            'Gibson Catberg (Edited by)',
            'Gibson Catberg (Editor)',
            'Gibson Catberg (Technical Ed.)',
            'Gibson Catberg,Technical Ed.',
            'Gibson Catberg, Technical Ed.',
            'Gibson Catberg (Technical Editor)',
            'Gibson Catberg,Technical Editor',
            'Gibson Catberg, Technical Editor',
        ]:
            with self.subTest(given=given, expected=EXPECTED):
                actual = strip_edited_by(given)
                self.assertEqual(EXPECTED, actual)


class TestStripForewordBy(TestCase):
    def test_strips_foreword_by_variations(self):
        def _t(test_input):
            actual = strip_foreword_by(test_input)
            expect = 'Gibson Catberg'
            self.assertEqual(expect, actual)

        _t('Foreword by: Gibson Catberg')
        _t('foreword by: Gibson Catberg')
        _t('Foreword: Gibson Catberg')
        _t('foreword: Gibson Catberg')


class TestStripRepeatingPeriods(TestCase):
    def _assert_returns(self, expected, given):
        actual = strip_repeating_periods(given)
        self.assertEqual(expected, actual)

    def test_returns_valid_author_as_is(self):
        self._assert_returns('Gibson C. Sjöberg',
                             'Gibson C. Sjöberg')

    def test_strips_repeating_periods(self):
        self._assert_returns('Gibson C. Sjöberg',
                             'Gibson C. Sjöberg ...')
        self._assert_returns('Gibson C. Sjöberg',
                             'Gibson C. Sjöberg .....')
        self._assert_returns('Gibson C. Sjöberg',
                             'Gibson C. Sjöberg...')
        self._assert_returns('Gibson C. Sjöberg',
                             'Gibson C. Sjöberg.....')


class TestNormalizeLetterCase(TestCase):
    def _assert_returns(self, expected, given):
        actual = normalize_letter_case(given)
        self.assertEqual(expected, actual)

    def test_returns_name_with_proper_letter_case_as_is(self):
        for given_and_expected in [
            'Gibson Sjöberg',
            'Gibson C. Sjöberg'
        ]:
            with self.subTest(given_and_expected=given_and_expected):
                self._assert_returns(given_and_expected, given_and_expected)

    def test_returns_testdata_list_of_names_lastname_initials_as_is(self):
        for list_of_names, _ in TESTDATA_LIST_OF_NAMES_LASTNAME_INITIALS:
            for name in list_of_names:
                with self.subTest(given_and_expected=name):
                    self._assert_returns(name, name)

    def test_normalizes_names_with_all_lower_case_letters(self):
        for testdata in [
            TD(given='gibson sjöberg', expect='Gibson Sjöberg'),
            TD(given='gibson c. sjöberg', expect='Gibson C. Sjöberg'),
            TD(given='gibson van cat', expect='Gibson van Cat'),
            TD(given='gibson von cat', expect='Gibson von Cat'),
        ]:
            with self.subTest():
                self._assert_returns(testdata.expect, testdata.given)

    def test_normalizes_names_with_all_upper_case_letters(self):
        self._assert_returns('Gibson Sjöberg', 'GIBSON SJÖBERG')

    def test_normalizes_names_with_all_upper_case_first_name(self):
        self._assert_returns('Gibson Sjöberg', 'GIBSON Sjöberg')

    def test_normalizes_names_with_all_upper_case_last_name(self):
        self._assert_returns('Gibson Sjöberg', 'Gibson SJÖBERG')

    def test_normalizes_names_with_mixed_case_first_name(self):
        for given in ['GiBsOn Sjöberg', 'gIbSoN Sjöberg']:
            self._assert_returns('Gibson Sjöberg', given)

    def test_normalizes_names_with_mixed_case_last_name(self):
        for given in ['Gibson SjÖbErG', 'Gibson sJöBeRg']:
            self._assert_returns('Gibson Sjöberg', given)

    def test_normalizes_names_with_nobiliary_particles(self):
        for testdata in [
            TD(given='Gibson von Sjöberg', expect='Gibson von Sjöberg'),
            TD(given='Gibson Von Sjöberg', expect='Gibson von Sjöberg'),
            TD(given='Gibson van Sjöberg', expect='Gibson van Sjöberg'),
            TD(given='Gibson Van Sjöberg', expect='Gibson van Sjöberg'),
            TD(given='Gibson von Sjöberg', expect='Gibson von Sjöberg'),
            TD(given='Gibson de Sjöberg', expect='Gibson de Sjöberg'),
            TD(given='Gibson De Sjöberg', expect='Gibson de Sjöberg'),
        ]:
            with self.subTest():
                self._assert_returns(testdata.expect, testdata.given)

    @unittest.expectedFailure
    def test_returns_name_with_van_as_is(self):
        self._assert_returns('Vanessa Su Lee Goh', 'Vanessa Su Lee Goh')


class TestNameParser(TestCase):
    def test_thirdparty_nameparser_is_available(self):
        self.assertIsNotNone(nameparser)

    def test__parse_name_returns_expected_type_given_single_word_name(self):
        actual = _parse_name('foo')
        self.assertIsInstance(actual, dict)


class TestHumanNameParser(TestCase):
    TESTDATA_FULLNAME_EXPECTED = [
        TD(given=None, expect={}),
        TD(given='', expect={}),
        TD(given=' ', expect={}),
        # NOTE: Includes empty values, which are NOT tested!
        TD(given='G',
           expect={'first': 'G',
                   'first_list': ['G'],
                   'last': '',
                   'last_list': [],
                   'middle': '',
                   'middle_list': [],
                   'original': 'G',
                   'suffix': '',
                   'title': '',
                   'title_list': []}),
        # NOTE: This is equivalent to the above.
        TD(given='G',
           expect={'first': 'G',
                   'first_list': ['G'],
                   'original': 'G'}),
        TD(given='Gibson',
           expect={'first': 'Gibson',
                   'first_list': ['Gibson'],
                   'original': 'Gibson'}),
        TD(given='Gibson Sjöberg',
           expect={'first': 'Gibson',
                   'first_list': ['Gibson'],
                   'last': 'Sjöberg',
                   'last_list': ['Sjöberg'],
                   'original': 'Gibson Sjöberg'}),
        TD(given='Russell, Bertrand',
           expect={'first': 'Bertrand',
                   'first_list': ['Bertrand'],
                   'last': 'Russell',
                   'last_list': ['Russell'],
                   'original': 'Russell, Bertrand'}),
        TD(given='Bertrand Russell',
           expect={'first': 'Bertrand',
                   'first_list': ['Bertrand'],
                   'last': 'Russell',
                   'last_list': ['Russell'],
                   'original': 'Bertrand Russell'}),
        TD(given='Friedrich Wilhelm Nietzsche',
           expect={'first': 'Friedrich',
                   'first_list': ['Friedrich'],
                   'last': 'Nietzsche',
                   'last_list': ['Nietzsche'],
                   'middle': 'Wilhelm',
                   'middle_list': ['Wilhelm'],
                   'original': 'Friedrich Wilhelm Nietzsche'}),
        TD(given='Nietzsche, Friedrich Wilhelm',
           expect={'first': 'Friedrich',
                   'first_list': ['Friedrich'],
                   'last': 'Nietzsche',
                   'last_list': ['Nietzsche'],
                   'middle': 'Wilhelm',
                   'middle_list': ['Wilhelm'],
                   'original': 'Nietzsche, Friedrich Wilhelm'}),

        # Failed special cases
        TD(given='Shiva Prasad K.M.',
           expect={'first': 'Shiva',
                   'first_list': ['Shiva'],
                   'last': 'Prasad',
                   'last_list': ['Prasad'],
                   'middle': 'K.M.',
                   'middle_list': ['K', 'M'],
                   'original': 'Shiva Prasad K.M.'}),
        TD(given='I.N. Bronsh',
           expect={'first': 'I',
                   'first_list': ['I'],
                   'last': 'Bronsh',
                   'last_list': ['Bronsh'],
                   'middle': 'N',
                   'middle_list': ['N'],
                   'original': 'I.N. Bronsh'}),
        TD(given='K.A. Semandyayev',
           expect={'first': 'K',
                   'first_list': ['K'],
                   'last': 'Semandyayev',
                   'last_list': ['Semandyayev'],
                   'middle': 'A',
                   'middle_list': ['A'],
                   'original': 'K.A. Semandyayev'}),
        TD(given='Ke-Lin Du',
           expect={'first': 'Ke-Lin',
                   'first_list': ['Ke-Lin'],
                   'last': 'Du',
                   'last_list': ['Du'],
                   'middle': '',
                   'middle_list': [],
                   'original': 'Ke-Lin Du'}),
        TD(given='M. N. S. Swamy',
           expect={'first': 'M.',
                   'first_list': ['M.'],
                   'last': 'Swamy',
                   'last_list': ['Swamy'],
                   'middle': 'N. S.',
                   'middle_list': ['N.', 'S.'],
                   'original': 'M. N. S. Swamy'}),
    ]

    def setUp(self):
        self.name_parser = HumanNameParser()

    def test_parses_strings(self):
        actual = self.name_parser('Foo')
        self.assertIsInstance(actual, dict)
        self.assertEqual('Foo', actual['original'])

    def test_parses_name(self):
        actual = self.name_parser('Gibson Catson, Ph.D.')
        self.assertIsInstance(actual, dict)
        self.assertEqual('Gibson', actual['first'])
        self.assertEqual('Catson', actual['last'])
        self.assertEqual('Ph.D.', actual['suffix'])

    def test_preprocess_returns_empty_string_for_empty_input(self):
        def _assert_empty_string(given):
            actual = self.name_parser._preprocess(given)
            self.assertEqual('', actual)

        _assert_empty_string('')
        _assert_empty_string(' ')
        _assert_empty_string('\t')
        _assert_empty_string('\t ')

    def _check_preprocess(self, given, expect):
        actual = self.name_parser._preprocess(given)
        self.assertEqual(expect, actual)

    def test_preprocess_pass_through_valid_input_as_is(self):
        self._check_preprocess('Foo', 'Foo')

    def test_preprocess_strips_whitespace(self):
        self._check_preprocess('Foo ', 'Foo')
        self._check_preprocess(' Foo', 'Foo')
        self._check_preprocess('\tfoo', 'Foo')
        self._check_preprocess(' \tfoo', 'Foo')
        self._check_preprocess('Foo \t', 'Foo')

    def test_preprocess_strips_trailing_characters(self):
        self._check_preprocess('Foo,', 'Foo')
        self._check_preprocess('Foo,,', 'Foo')

    def test_preprocess_strips_et_al(self):
        self._check_preprocess('Foo et al.', 'Foo')
        self._check_preprocess('Foo, et al.', 'Foo')

    def test_parses_human_names(self):
        for given, expect in self.TESTDATA_FULLNAME_EXPECTED:
            actual = self.name_parser(given)
            self.assertIsInstance(actual, dict)
            for k, v in actual.items():
                # Skip comparison of empty values for brevity.
                if v:
                    expected = expect.get(k)
                    self.assertEqual(expected, v,
                                     'Key "{}". Expected: "{!s}"  '
                                     'Got: "{!s}"'.format(k, expected, v))


class TestHumanNameFormatter(TestCase):
    def setUp(self):
        self.name_formatter = HumanNameFormatter()

    def test_call_raises_exception_gives_invalid_arguments(self):
        with self.assertRaises(AssertionError):
            _ = self.name_formatter('Foo')

    def test_format_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            _ = self.name_formatter.format('Foo')

    def test_call_raises_exception_given_none(self):
        with self.assertRaises(AssertionError):
            _ = self.name_formatter(None)


class TestLastNameInitialsFormatter(TestCase):
    def test_formats_full_human_names(self):
        for given, expect in TESTDATA_NAME_LASTNAME_INITIALS:
            with self.subTest(given=given, expect=expect):
                actual = format_name(given, formatter=LastNameInitialsFormatter)
                self.assertEqual(expect, actual)

    def test_raises_exception_given_byte_strings(self):
        with self.assertRaises(AssertionError):
            _ = format_name(b'Foo', formatter=LastNameInitialsFormatter)

    def test_returns_empty_string_for_none_or_empty_input(self):
        def _aE(test_input):
            actual = format_name(test_input,
                                 formatter=LastNameInitialsFormatter)
            self.assertEqual('', actual)

        _aE(None)
        _aE('')
        _aE(' ')
        _aE('\t')
        _aE('\t ')


class TestFormatName(TestCase):
    def test_formats_full_name_with_default_formatter(self):
        for given, expect in TESTDATA_NAME_LASTNAME_INITIALS:
            actual = format_name(given)
            self.assertEqual(expect, actual)

    def test_raises_exception_given_invalid_formatter(self):
        invalid_formatter = True
        with self.assertRaises(AssertionError):
            _ = format_name('', invalid_formatter)

    def test_formats_full_name_given_valid_formatter(self):
        valid_formatter = LastNameInitialsFormatter

        for given, expect in TESTDATA_NAME_LASTNAME_INITIALS:
            actual = format_name(given, valid_formatter)
            self.assertEqual(expect, actual)


class TestFormatNameList(TestCase):
    def test_formats_list_of_full_human_names_with_default_formatter(self):
        for given, expect in TESTDATA_LIST_OF_NAMES_LASTNAME_INITIALS:
            actual = format_name_list(given)
            self.assertEqual(expect, actual)

    def test_raises_exception_given_invalid_formatter(self):
        invalid_formatter = True
        with self.assertRaises(AssertionError):
            _ = format_name_list('', invalid_formatter)

    def test_formats_list_of_full_human_names_given_valid_formatter(self):
        valid_formatter = LastNameInitialsFormatter

        for given, expect in TESTDATA_LIST_OF_NAMES_LASTNAME_INITIALS:
            actual = format_name_list(given, valid_formatter)
            self.assertEqual(expect, actual)


class TestSplitMultipleNames(TestCase):
    def _assert_that_it_returns(self, expected, given_any_of):
        for given in given_any_of:
            with self.subTest(given=given, expected=expected):
                actual = split_multiple_names(given)
                self.assertEqual(expected, actual)

    def _assert_unchanged(self, given):
        actual = split_multiple_names(given)
        self.assertEqual(given, actual)

    def test_does_not_split_single_name(self):
        self._assert_unchanged(['Enandra Mitra'])
        self._assert_unchanged(['Foobar, S.'])
        self._assert_unchanged(['Paul, Baz'])

    def test_does_not_split_single_name_comma_between_surname_lastname(self):
        self._assert_unchanged(['edited by Ludlow, David'])

    def test_does_not_split_any_in_list_of_three_valid_names(self):
        self._assert_unchanged(['Benjamin Bearkins', 'Jacob Rock Hammer', 'Jam M. Raid'])

    def test_splits_two_names_where_one_contains_an_initial(self):
        self._assert_that_it_returns(
            expected=[
                'Gross Gorelick', 'Andy D. Kennel'
            ],
            given_any_of=[
                ['Gross Gorelick, Andy D. Kennel'],
                ['Gross Gorelick,Andy D. Kennel'],
                ['Gross Gorelick and Andy D. Kennel'],
                ['Gross Gorelick, and Andy D. Kennel'],
                ['Gross Gorelick,and Andy D. Kennel'],
            ])

    def test_splits_two_first_name_last_name_names_various_separators(self):
        self._assert_that_it_returns(
            expected=[
                'Raúl Garreta', 'Guillermo Moncecchi'
            ],
            given_any_of=[
                ['Raúl Garreta, Guillermo Moncecchi'],
                ['Raúl Garreta,Guillermo Moncecchi'],
                ['Raúl Garreta and Guillermo Moncecchi'],
                ['Raúl Garreta, and Guillermo Moncecchi'],
                ['Raúl Garreta + Guillermo Moncecchi'],
                ['Raúl Garreta+Guillermo Moncecchi'],
            ])

    def test_splits_three_first_name_last_name_names_various_separators(self):
        self._assert_that_it_returns(
            expected=[
                'Gibson Pawsy', 'Friedrich Nietzsche', 'Foobar Baz'
            ],
            given_any_of=[
                ['Gibson Pawsy, Friedrich Nietzsche, Foobar Baz'],
                ['Gibson Pawsy, Friedrich Nietzsche and Foobar Baz'],
                ['Gibson Pawsy and Friedrich Nietzsche, Foobar Baz'],
                ['Gibson Pawsy and Friedrich Nietzsche and Foobar Baz'],
                ['Gibson Pawsy, Friedrich Nietzsche, and Foobar Baz'],
                ['Gibson Pawsy and Friedrich Nietzsche, and Foobar Baz'],
                ['Gibson Pawsy, and Friedrich Nietzsche and Foobar Baz'],
                ['Gibson Pawsy, and Friedrich Nietzsche, and Foobar Baz'],

                ['Gibson Pawsy,Friedrich Nietzsche,Foobar Baz'],
                ['Gibson Pawsy,Friedrich Nietzsche and Foobar Baz'],
                ['Gibson Pawsy and Friedrich Nietzsche,Foobar Baz'],
                ['Gibson Pawsy and Friedrich Nietzsche and Foobar Baz'],
                ['Gibson Pawsy,Friedrich Nietzsche,and Foobar Baz'],
                ['Gibson Pawsy and Friedrich Nietzsche,and Foobar Baz'],
                ['Gibson Pawsy,and Friedrich Nietzsche and Foobar Baz'],
                ['Gibson Pawsy,and Friedrich Nietzsche,and Foobar Baz'],
            ])

    def test_splits_two_names_where_one_contains_a_middle_name(self):
        self._assert_that_it_returns(
            expected=[
                'Gibson Cat Sjöberg', 'Woo Blackmoon'
            ],
            given_any_of=[
                ['Gibson Cat Sjöberg, Woo Blackmoon'],
                ['Gibson Cat Sjöberg and Woo Blackmoon'],
                ['Gibson Cat Sjöberg, and Woo Blackmoon'],
            ])

    def test_splits_three_names_split_across_two_lists(self):
        self._assert_that_it_returns(
            expected=[
                'Gibson Cat Sjöberg', 'Woo Blackmoon', 'Friedrich Nietzsche'
            ],
            given_any_of=[
                [['Gibson Cat Sjöberg, Woo Blackmoon'], 'Friedrich Nietzsche'],
                [['Gibson Cat Sjöberg and Woo Blackmoon'], 'Friedrich Nietzsche'],
                [['Gibson Cat Sjöberg, and Woo Blackmoon'], 'Friedrich Nietzsche'],
            ])

    def test_splits_three_name_separated_by_commas_without_spaces(self):
        self._assert_that_it_returns(
            expected=[
                'Mahssen Mahemmad', 'Muhemmad Badruddin Khen', 'Eiheb Bashiar Mahemmad Beshiar'
            ],
            given_any_of=[
                ['Mahssen Mahemmad,Muhemmad Badruddin Khen,Eiheb Bashiar Mahemmad Beshiar']
            ]
        )

    def test_does_not_split_names_with_name_parts_separated_by_comma(self):
        self._assert_unchanged(['Foobar, S.', 'Paul, Baz', 'Gibson, N.'])
        self._assert_unchanged(['Foobar, S.', 'Paul, Baz'])
        self._assert_unchanged(['Paul, Baz', 'Gibson, N.'])
        self._assert_unchanged(['Sullivan, Jonathan, Jewett, Carl, Hibbs, Kurt'])

    @unittest.expectedFailure
    def test_does_not_split_names_with_some_name_parts_separated_by_comma(self):
        self._assert_unchanged(['Sullivan, Jonathan, Jewett, Carl, Hibbs, Kurt',
                                'Carl Jewett',
                                'Jonathan Sullivan'])

    def test_splits_two_names_separated_by_ampersand(self):
        self._assert_that_it_returns(
            expected=[
                "Larry O'Brien", 'Bruce Eckel'
            ],
            given_any_of=[
                ["Larry O'Brien & Bruce Eckel"],
                ["Larry O'Brien &  Bruce Eckel"],
                ["Larry O'Brien  &  Bruce Eckel"]
            ]
        )

    def test_splits_three_names_separated_by_semicolons(self):
        self._assert_that_it_returns(
            expected=['Romano, Ray', 'Philips, Dusty', 'Hatten, Rick van'],
            given_any_of=[
                ['Romano, Ray;  Philips, Dusty;  Hatten, Rick van'],
                ['Romano, Ray; Philips, Dusty; Hatten, Rick van'],
                ['Romano, Ray;Philips, Dusty;Hatten, Rick van'],
                ['Romano, Ray;;  Philips, Dusty;;  Hatten, Rick van'],
                ['Romano, Ray;; Philips, Dusty;; Hatten, Rick van'],
                ['Romano, Ray;;Philips, Dusty;;Hatten, Rick van'],
            ]
        )
        self._assert_that_it_returns(
            expected=['Romano,Ray', 'Philips,Dusty', 'Hatten,Rick van'],
            given_any_of=[
                ['Romano,Ray;  Philips,Dusty;  Hatten,Rick van'],
                ['Romano,Ray; Philips,Dusty; Hatten,Rick van'],
                ['Romano,Ray;Philips,Dusty;Hatten,Rick van'],
                ['Romano,Ray;;  Philips,Dusty;;  Hatten,Rick van'],
                ['Romano,Ray;; Philips,Dusty;; Hatten,Rick van'],
                ['Romano,Ray;;Philips,Dusty;;Hatten,Rick van'],
            ]
        )
        self._assert_that_it_returns(
            expected=['Romano Ray', 'Philips Dusty', 'Hatten Rick van'],
            given_any_of=[
                ['Romano Ray;  Philips Dusty;  Hatten Rick van'],
                ['Romano Ray; Philips Dusty; Hatten Rick van'],
                ['Romano Ray;Philips Dusty;Hatten Rick van'],
                ['Romano Ray;;  Philips Dusty;;  Hatten Rick van'],
                ['Romano Ray;; Philips Dusty;; Hatten Rick van'],
                ['Romano Ray;;Philips Dusty;;Hatten Rick van'],
            ]
        )

    def test_handle_malformed_metadata_from_external_provider(self):
        self._assert_that_it_returns(
            expected=['Carthik S.', 'Paul Enand'],
            given_any_of=[
                ['Carthik', 'S.', 'Paul', 'Enand'],
            ]
        )
        self._assert_that_it_returns(
            expected=['Carthik S.', 'Karthikayen N.'],
            given_any_of=[
                ['Carthik', 'S.', 'Karthikayen', 'N.'],
            ]
        )
        self._assert_that_it_returns(
            expected=['Carthik S.', 'Paul Enand', 'Karthikayen N.'],
            given_any_of=[
                ['Carthik', 'S.', 'Paul', 'Enand', 'Karthikayen', 'N.'],
            ]
        )

    def test_based_on_live_data_a(self):
        self._assert_that_it_returns(
            expected=['Stuart K. Rassel', 'Pitr Narval', 'Arnest Dawid'],
            given_any_of=[
                ['Stuart K. Rassel', 'Pitr Narval', 'Arnest Dawid'],
                ['Stuart K. Rassel and Pitr Narval', 'Arnest Dawid']
            ]
        )

    def test_based_on_live_data_b(self):
        self._assert_that_it_returns(
            expected=['Christopher Columbus', 'Prabhkar Ragvan', 'Heinrich Schueltze'],
            given_any_of=[
                ['Christopher Columbus, Prabhkar Ragvan, and Heinrich Schueltze'],
                ['Christopher Columbus, Prabhkar Ragvan, Heinrich Schueltze']
            ]
        )
        self._assert_that_it_returns(
            expected=['Christopher Z. Columbus', 'Prabhkar Ragvan', 'Heinrich K. Schueltze'],
            given_any_of=[
                ['Christopher Z. Columbus, Prabhkar Ragvan, and Heinrich K. Schueltze'],
                ['Christopher Z. Columbus, Prabhkar Ragvan, Heinrich K. Schueltze']
            ]
        )

    def test_based_on_live_data_c(self):
        self._assert_that_it_returns(
            expected=['Prastant Natarojan', 'John Q. Frienzal', 'Deitlev I. Saltz'],
            given_any_of=[
                ['Prastant Natarojan', 'John Q. Frienzal and Deitlev I. Saltz'],
                ['Prastant Natarojan', 'John Q. Frienzal, and Deitlev I. Saltz'],
            ]
        )
        self._assert_that_it_returns(
            expected=['Andreas D. Müllör', 'Farah Guido'],
            given_any_of=[
                ['Andreas D. Müllör and Farah Guido'],
                ['Andreas D. Müllör, and Farah Guido'],
            ]
        )

    def test_based_on_live_data_d(self):
        self._assert_that_it_returns(
            expected=['Ashok N. Srivasaduva', 'Ramarena Nemaniskt', 'Kirsten KleinSteinhaeuser'],
            given_any_of=[
                ['Ashok N. Srivasaduva,Ramarena Nemaniskt,Kirsten KleinSteinhaeuser'],
                ['Ashok N. Srivasaduva, Ramarena Nemaniskt,Kirsten KleinSteinhaeuser'],
                ['Ashok N. Srivasaduva,Ramarena Nemaniskt, Kirsten KleinSteinhaeuser'],
                ['Ashok N. Srivasaduva, Ramarena Nemaniskt, Kirsten KleinSteinhaeuser'],
            ]
        )

    def test_based_on_live_data_e(self):
        self._assert_that_it_returns(
            expected=['Danilo P. Mandic', 'Vanessa Su Lee Goh'],
            given_any_of=[
                ['Danilo P. Mandic, Vanessa Su Lee Goh'],
            ]
        )

    def test_refactored_handles_ad_hoc_isbn_metadata_cleanup(self):
        self._assert_that_it_returns(
            expected=['Stephen Wynkoop', 'Chris Lester'],
            given_any_of=[
                ['Stephen Wynkoop [Chris Lester]'],
                ['Stephen Wynkoop [and Chris Lester]'],
            ]
        )


class TestFilterMultipleNames(TestCase):
    def _assert_filter_output_contains(self, expected, given):
        for name_ordering in itertools.permutations(given):
            actual = filter_multiple_names(name_ordering)
            self.assertEqual(sorted(expected), sorted(actual))

    def _assert_filter_returns(self, expected, given):
        actual = filter_multiple_names(given)
        self.assertEqual(expected, actual)

    def test_returns_valid_names_as_is(self):
        self._assert_filter_returns(
            expected=['Friedrich Nietzsche', 'Gibson Sjöberg'],
            given=['Friedrich Nietzsche', 'Gibson Sjöberg']
        )
        self._assert_filter_returns(
            expected=['Benjamin Bearkins', 'Jacob Rock Hammer', 'Jam M. Raid'],
            given=['Benjamin Bearkins', 'Jacob Rock Hammer', 'Jam M. Raid']
        )

    def test_removes_names_consisting_of_a_single_letter(self):
        self._assert_filter_returns(
            expected=['Ankur Ankan', 'Abinash P'],
            given=['Ankur Ankan', 'Abinash P', 'a']
        )

    def test_removes_variations_of_edited_by_from_any_name_in_list_of_names(self):
        for given in [
            ['ed. by Gibson Sjöberg', 'Achim Weckar', 'Tomáš Navasod'],
            ['Ed. by Gibson Sjöberg', 'Achim Weckar', 'Tomáš Navasod'],
            ['edited by Gibson Sjöberg', 'Achim Weckar', 'Tomáš Navasod'],
            ['Edited by Gibson Sjöberg', 'Achim Weckar', 'Tomáš Navasod'],
            ['Gibson Sjöberg', 'ed. by Achim Weckar', 'Tomáš Navasod'],
            ['Gibson Sjöberg', 'Ed. by Achim Weckar', 'Tomáš Navasod'],
            ['Gibson Sjöberg', 'edited by Achim Weckar', 'Tomáš Navasod'],
            ['Gibson Sjöberg', 'Edited by Achim Weckar', 'Tomáš Navasod'],
            ['Gibson Sjöberg', 'Achim Weckar', 'ed. by Tomáš Navasod'],
            ['Gibson Sjöberg', 'Achim Weckar', 'Ed. by Tomáš Navasod'],
            ['Gibson Sjöberg', 'Achim Weckar', 'edited by Tomáš Navasod'],
            ['Gibson Sjöberg', 'Achim Weckar', 'Edited by Tomáš Navasod'],
        ]:
            with self.subTest(given=given):
                self._assert_filter_output_contains(
                    expected=['Gibson Sjöberg', 'Achim Weckar', 'Tomáš Navasod'],
                    given=given
                )

    def test_removes_variations_of_author_from_any_name_in_list_of_names(self):
        for given in [
            ['author Gibson Sjöberg', 'Achim Weckar', 'Tomáš Navasod'],
            ['Author Gibson Sjöberg', 'Achim Weckar', 'Tomáš Navasod'],
            ['author: Gibson Sjöberg', 'Achim Weckar', 'Tomáš Navasod'],
            ['Author: Gibson Sjöberg', 'Achim Weckar', 'Tomáš Navasod'],
            ['Gibson Sjöberg', 'author Achim Weckar', 'Tomáš Navasod'],
            ['Gibson Sjöberg', 'Author Achim Weckar', 'Tomáš Navasod'],
            ['Gibson Sjöberg', 'author: Achim Weckar', 'Tomáš Navasod'],
            ['Gibson Sjöberg', 'Author: Achim Weckar', 'Tomáš Navasod'],
            ['Gibson Sjöberg', 'Achim Weckar', 'author Tomáš Navasod'],
            ['Gibson Sjöberg', 'Achim Weckar', 'Author Tomáš Navasod'],
            ['Gibson Sjöberg', 'Achim Weckar', 'author: Tomáš Navasod'],
            ['Gibson Sjöberg', 'Achim Weckar', 'Author: Tomáš Navasod'],
        ]:
            with self.subTest(given=given):
                self._assert_filter_output_contains(
                    expected=['Gibson Sjöberg', 'Achim Weckar', 'Tomáš Navasod'],
                    given=given
                )

    def test_removes_editor_element_from_list_with_one_actual_name(self):
        for given in [
            ['(Ed)', 'John P. Vecca'],
            ['(ed)', 'John P. Vecca'],
            ['(Ed.)', 'John P. Vecca'],
            ['(ed.)', 'John P. Vecca'],
            ['(Editor)', 'John P. Vecca'],
            ['(editor)', 'John P. Vecca'],
            ['editor', 'John P. Vecca'],
            ['Editor', 'John P. Vecca'],
        ]:
            with self.subTest(given=given):
                self._assert_filter_returns(expected=['John P. Vecca'], given=given)

    def test_removes_variations_of_editor_from_list_with_one_name(self):
        for given in [
            ['Petra Werner (ed)'],
            ['Petra Werner (Ed)'],
            ['Petra Werner (ed.)'],
            ['Petra Werner (Ed.)'],
            ['Petra Werner (Editor)'],
            ['Petra Werner (editor)'],
            ['Petra Werner editor'],
            ['Petra Werner Editor'],
        ]:
            with self.subTest(given=given):
                self._assert_filter_returns(expected=['Petra Werner'], given=given)

    def test_handles_apparent_list_in_string_with_leading_by_and_trailing_et_al(self):
        self._assert_filter_returns(
            expected=['Eric Oberg'],
            given=['[by Eric Oberg ... et al.]']
        )

    def test_handles_single_name_with_leading_edited_by_and_trailing_et_al(self):
        self.skipTest('TODO')
        self._assert_filter_returns(
            expected=['Bart de Decker'],
            given=['edited by Bart de Decker ... [et al.]']
        )

    def test_based_on_live_data_a(self):
        self._assert_filter_returns(
            expected=['Daboreh Littlajohn Shindar', 'Thomes X. Shindar', 'Leure F. Huntar', 'Will Schmiad'],
            given=['Daboreh Littlajohn Shindar', 'Thomes X. Shindar', 'Leure F. Huntar', 'technical review', 'Will Schmiad', 'DVD presenter']
        )

    def test_based_on_live_data_b(self):
        self._assert_filter_returns(
            expected=['Hairdo Barber', 'Green Grasdal'],
            given=['Hairdo Barber ...', 'et al.', 'Green Grasdal', 'technical editor']
        )

    def test_based_on_live_data_c(self):
        self._assert_filter_returns(
            expected=['Michael Kross'],
            given=['Michael Kross', 'et al.']
        )

    def test_based_on_live_data_d(self):
        self.skipTest('TODO: ..')
        self._assert_filter_returns(
            expected=['David Astolfo ... Technical reviewers: Mario Ferrari ...'],
            given=['Michael Kross', 'et al.']
        )

    def test_based_on_live_data_e(self):
        self._assert_filter_returns(
            expected=['Eric Conrad', 'Sith Misaner', 'Josh Faldmen'],
            given=['by Eric Conrad', 'Sith Misaner', 'Josh Faldmen']
        )

    def test_based_on_live_data_f(self):
        self._assert_filter_returns(
            expected=['Hermann Lödding', 'Ralph Riedel', 'Klaus-Dieter Thoben', 'Gregor von Cieminski', 'Dimitris Kiritsis'],
            given=['Hermann Lödding', 'Ralph Riedel', 'Klaus-Dieter Thoben', 'Gregor von Cieminski', 'Dimitris Kiritsis']
        )

    def test_based_on_live_data_g(self):
        self._assert_filter_returns(
            expected=['I.N. Bronsh', 'K.A. Semandyayev', 'Gert Musiol', 'Steiner Mühlig'],
            given=['I.N. Bronsh', 'K.A. Semandyayev', 'Gert Musiol', 'Steiner Mühlig']
        )

    def test_based_on_live_data_h(self):
        self._assert_filter_returns(
            expected=['Stuart J. Russell', 'Peter Norvig', 'Ernest Davis'],
            given=['Stuart J. Russell', 'Peter Norvig', 'Contributing Writers', 'Ernest Davis']
        )
        self._assert_filter_returns(
            expected=['Ricard Dahl', 'William Z. Longdon', 'Nichlas H. Bee', 'Carl K. Soze'],
            given=['Ricard Dahl', 'William Z. Longdon', 'Nichlas H. Bee', 'With Contributions By Carl K. Soze']
        )

    def test_based_on_live_data_i(self):
        self._assert_filter_returns(
            expected=['Johnson, Dean R.', 'Paymer, Carol A.', 'Chamberlain, Aaron P.'],
            given=['Johnson, Dean R.', 'Paymer, Carol A.', 'Chamberlain, Aaron P.']
        )

    def test_based_on_live_data_j(self):
        self._assert_filter_returns(
            expected=['Lauren F. Hanter', 'Rubert K. Shimanski'],
            given=['Lauren F. Hanter ... [et al.]', 'Rubert K. Shimanski, technical editor']
        )
        self._assert_filter_returns(
            expected=['Bran Barbit', 'Mårten Gräsdal'],
            given=['Bran Barbit ... [et al.]', 'Mårten Gräsdal, technical editor'],
        )


class TestFilterName(TestCase):
    def _assert_filter_returns(self, expected, given):
        actual = filter_name(given)
        self.assertEqual(expected, actual)

    def _assert_filter_does_not_pass(self, given):
        actual = filter_name(given)
        self.assertEqual('', actual)

    def test_removes_variations_of_edited_by_from_start_of_name(self):
        self._assert_filter_returns('Gibson Sjöberg', given='edited by Gibson Sjöberg')
        self._assert_filter_returns('Gibson Sjöberg', given='Edited by Gibson Sjöberg')
        self._assert_filter_returns('Gibson Sjöberg', given='ed. by Gibson Sjöberg')
        self._assert_filter_returns('Gibson Sjöberg', given='Ed. by Gibson Sjöberg')

    def test_removes_variations_of_foreword_from_start_of_name(self):
        self._assert_filter_returns('Rick F. Haribay', given='Foreword By Rick F. Haribay')
        self._assert_filter_returns('Rick F. Haribay', given='Foreword: Rick F. Haribay')

    def test_removes_variations_of_contributions(self):
        for given in [
            'with contributions by Carl K. Soze',
            'with Contributions by Carl K. Soze',
            'With Contributions By Carl K. Soze',
            'contributions by Carl K. Soze',
            'Contributions by Carl K. Soze',
            'Contributions By Carl K. Soze',
            'contributions Carl K. Soze',
            'Contributions Carl K. Soze',
            'Contributions Carl K. Soze'
        ]:
            self._assert_filter_returns('Carl K. Soze', given)

    def test_returns_empty_string_given_name_editor(self):
        self._assert_filter_does_not_pass('editor')
        self._assert_filter_does_not_pass('Editor')

    def test_returns_empty_string_given_name_author(self):
        self._assert_filter_does_not_pass('author')
        self._assert_filter_does_not_pass('Author')

    def test_returns_empty_string_given_name_foreword(self):
        self._assert_filter_does_not_pass('foreword')
        self._assert_filter_does_not_pass('Foreword')

    @unittest.expectedFailure
    def test_returns_name_with_van_as_is(self):
        self._assert_filter_returns('Vanessa Su Lee Goh', 'Vanessa Su Lee Goh')


class PreProcessNames(TestCase):
    def _assert_preprocess_names_returns(self, expected, given=None, given_any_of=None):
        assert given or given_any_of

        if given:
            actual = preprocess_names(given)
            self.assertEqual(expected, actual)

        if given_any_of:
            for given_ in given_any_of:
                actual_ = preprocess_names(given_)
                self.assertEqual(expected, actual_)

    def test_returns_expected(self):
        self._assert_preprocess_names_returns(
            expected=['John V. Shindler', 'Monica Littlejohn Shindler', 'Mårtin Gräsdal'],
            given=['[John V. Shindler, Monica Littlejohn Shindler', 'Mårtin Gräsdal, technical ed.]']
        )
        self._assert_preprocess_names_returns(
            expected=['Lauren F. Hanter', 'Rubert K. Shimanski'],
            given_any_of=[
                ['Lauren F. Hanter ... [et al.]', 'Rubert K. Shimanski, technical editor'],
                ['Lauren F. Hanter ... [et al.], Rubert K. Shimanski, technical editor'],
            ]
        )
        self._assert_preprocess_names_returns(
            expected=['Bran Barbit', 'Mårten Gräsdal'],
            given_any_of=[
                ['Bran Barbit ... [et al.]', 'Mårten Gräsdal, technical editor'],
                ['Bran Barbit ... [et al.]', 'Mårten Gräsdal technical editor'],
                ['Bran Barbit ... [et al.], Mårten Gräsdal, technical editor'],
                ['Bran Barbit ... [et al.], Mårten Gräsdal', 'technical editor'],
            ]
        )
        self._assert_preprocess_names_returns(
            expected=['Graham Nash', 'John L. Wright Jr.', 'Niclas Hammel'],
            given_any_of=[
                ['Graham Nash, John L. Wright Jr., Niclas Hammel'],
                ['Graham Nash, John L. Wright Jr.,Niclas Hammel']
            ]
        )
        self._assert_preprocess_names_returns(
            expected=['E. Galenbe', 'L. Kaiser'],
            given=['Edited by E. Galenbe and L. Kaiser'],
        )
        self._assert_preprocess_names_returns(
            expected=['Norris L. Johnson', 'Robert J. Shimonski'],
            given=['Norris L. Johnson', 'Jr.', 'Robert J. Shimonski'],
        )
        self._assert_preprocess_names_returns(
            expected=['Ludlow, David'],
            given=['edited by Ludlow, David'],
        )
        self._assert_preprocess_names_returns(
            expected=['Jonathan J. Burns'],
            given_any_of=[
                ['by Jonathan J. Burns'],
                ['By Jonathan J. Burns'],
                ['written by Jonathan J. Burns'],
                ['Written by Jonathan J. Burns'],
                ['Written By Jonathan J. Burns'],
            ]
        )

    def test_failed_cases(self):
        self._assert_preprocess_names_returns(
            expected=['H. S. Seini', 'Ricky Soyal', 'Sandep Singh Rawth'],
            given=['H. S. Seini', 'Ricky Soyal', 'Sandep Singh Rawth']
        )
        self._assert_preprocess_names_returns(
            expected=['H.S. Seini', 'Ricky Soyal', 'Sandep Singh Rawth'],
            given=['H.S. Seini', 'Ricky Soyal', 'Sandep Singh Rawth']
        )

    def test_refactored_handles_ad_hoc_isbn_metadata_cleanup(self):
        self._assert_preprocess_names_returns(
            expected=['Stephen Wynkoop', 'Chris Lester'],
            given_any_of=[
                ['Stephen Wynkoop [Chris Lester]'],
                ['Stephen Wynkoop [and Chris Lester]'],
            ]
        )
        self._assert_preprocess_names_returns(
            expected=['Jose Argudo Blanco', 'David Upton'],
            given_any_of=[
                ['Jose Argudo Blanco and David Upton'],
                ['Jose Argudo Blanco, and David Upton'],
                ['Jose Argudo Blanco, David Upton'],
            ]
        )
        self._assert_preprocess_names_returns(
            expected=['Michael Dory', 'Adam Parrish', 'Brendan Berg'],
            given_any_of=[
                ['Michael Dory, Adam Parrish and Brendan Berg'],
                ['Michael Dory, Adam Parrish, and Brendan Berg'],
                ['Michael Dory, Adam Parrish, Brendan Berg'],
            ]
        )
        self._assert_preprocess_names_returns(
            expected=['Micha Gorelick', 'Andy R. Terrel'],
            given=['Micha Gorelick, Andy R. Terrel']
        )
        self._assert_preprocess_names_returns(
            expected=['David Astolfo'],
            given=['David Astolfo ... Technical reviewers: Mario Ferrari ...']
        )

    def test_post_refactor_leading_substring_regex(self):
        self._assert_preprocess_names_returns(
            expected=['Gibson Catberg'],
            given_any_of=[
                ['Gibson Catberg'],
                ['(Gibson Catberg'],
                ['[Gibson Catberg'],
                ['{Gibson Catberg'],
                [';Gibson Catberg'],
                ['(By Gibson Catberg'],
                ['(by Gibson Catberg'],
                ['[By Gibson Catberg'],
                ['[by Gibson Catberg'],
                ['{By Gibson Catberg'],
                ['{by Gibson Catberg'],
                ['(Written By Gibson Catberg'],
                ['(Written by Gibson Catberg'],
                ['(written by Gibson Catberg'],
                ['[Written By Gibson Catberg'],
                ['[Written by Gibson Catberg'],
                ['[written by Gibson Catberg'],
                ['{Written By Gibson Catberg'],
                ['{Written by Gibson Catberg'],
                ['{written by Gibson Catberg'],
            ]
        )

    def test_post_refactor_trailing_substring_regex(self):
        self._assert_preprocess_names_returns(
            expected=['Gibson Catberg'],
            given_any_of=[
                ['Gibson Catberg'],
                ['Gibson Catberg]'],
                ['Gibson Catberg)'],
                ['Gibson Catberg}'],
                ['Gibson Catberg;'],
            ]
        )

    def test_names_separated_by_semicolons_in_single_string(self):
        self._assert_preprocess_names_returns(
            expected=['Kubasiek, John R.', 'Morrissey, Steven.', 'Basilone, John.'],
            given_any_of=[
                ['Kubasiek, John R.; Morrissey, Steven.; Basilone, John.'],
                ['Kubasiek, John R.;Morrissey, Steven.;Basilone, John.'],
                ['Kubasiek, John R. ;Morrissey, Steven. ;Basilone, John.'],
                ['Kubasiek, John R.;Morrissey, Steven.;Basilone, John.'],
            ]
        )

    def test_names_separated_by_semicolons_in_separate_strings(self):
        self._assert_preprocess_names_returns(
            expected=['Kubasiek, John R.', 'Morrissey, Steven.', 'Basilone, John.'],
            given_any_of=[
                ['Kubasiek, John R.;', 'Morrissey, Steven.;', 'Basilone, John.'],
                ['Kubasiek, John R.', ';Morrissey, Steven.', ';Basilone, John.'],
            ]
        )

    @unittest.expectedFailure
    def test_duplicate_names(self):
        # TODO: Improve splitting and/or remove duplicates.
        self._assert_preprocess_names_returns(
            expected=['Sullivan J.', 'Jewett C.', 'Hibbs K.'],
            given=[
                'Sullivan, Jonathan, Jewett, Carl, Hibbs, Kurt',
                'Carl Jewett',
                'Jonathan Sullivan',
            ]
        )
