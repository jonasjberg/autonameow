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

import itertools
from collections import namedtuple
from unittest import skipIf, TestCase

from util.text.humannames import (
    _parse_name,
    filter_name,
    filter_multiple_names,
    format_name,
    format_name_list,
    HumanNameFormatter,
    HumanNameParser,
    LastNameInitialsFormatter,
    normalize_letter_case,
    split_multiple_names,
    strip_repeating_periods,
    strip_author_et_al,
    strip_edited_by,
    strip_foreword_by
)
from thirdparty import nameparser as _nameparser


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
    TD(given='Do van Thanh', expect='vanThanh D.'),
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
    TD(given='vanThanh D.', expect='vanThanh D.'),
    TD(given='Ziemba W.T.', expect='Ziemba W.T.'),
    TD(given='Vickson R.G.', expect='Vickson R.G.'),
    TD(given='Wei Y.', expect='Wei Y.'),
    TD(given='Ding W.', expect='Ding W.'),
    TD(given='Russell B.', expect='Russell B.'),
    TD(given='Simchi-Levi D.', expect='Simchi-Levi D.'),

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
]

TESTDATA_LIST_OF_NAMES_LASTNAME_INITIALS = [
    TD(given=['David B. Makofske', 'Michael J. Donahoo',
              'Kenneth L. Calvert'],
       expect=['Calvert K.L.', 'Donahoo M.J.', 'Makofske D.B.']),

    TD(given=['Zhiguo Gong', 'Dickson K. W. Chiu', 'Di Zou'],
       expect=['Chiu D.K.W.', 'Gong Z.', 'Zou D.']),

    TD(given=['Muhammad Younas', 'Irfan Awan', 'Natalia Kryvinska',
              'Christine Strauss', 'Do van Thanh'],
       expect=['Awan I.', 'Kryvinska N.', 'Strauss C.', 'vanThanh D.',
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

    # Failed special cases
    TD(given=['Regina O. Obe', 'Leo S. Hsu'],
       expect=['Hsu L.S.', 'Obe R.O.']),
    TD(given=['Hermann Lödding', 'Ralph Riedel', 'Klaus-Dieter Thoben', 'Gregor von Cieminski', 'Dimitris Kiritsis'],
       expect=['Kiritsis D.', 'Lödding H.', 'Riedel R.', 'Thoben K.', 'vonCieminski G.']),
]


def nameparser_unavailable():
    return _nameparser is None, 'Failed to import "thirdparty.nameparser"'


class TeststripAuthorEtAl(TestCase):
    def test_strips_et_al_variations(self):
        def _t(test_input):
            actual = strip_author_et_al(test_input)
            expect = 'Gibson Catberg'
            self.assertEqual(expect, actual)

        _t('Gibson Catberg, et al.')
        _t('Gibson Catberg, et al')
        _t('Gibson Catberg et al')
        _t('Gibson Catberg [et al]')
        _t('Gibson Catberg [et al.]')
        _t('Gibson Catberg {et al}')
        _t('Gibson Catberg {et al.}')
        _t('Gibson Catberg, ... et al.')
        _t('Gibson Catberg, ... et al')
        _t('Gibson Catberg ... et al')
        _t('Gibson Catberg ... [et al]')
        _t('Gibson Catberg ... [et al.]')
        _t('Gibson Catberg ... {et al}')
        _t('Gibson Catberg ... {et al.}')


class TestStripEditedBy(TestCase):
    def test_strips_edited_by_variations(self):
        def _t(test_input):
            actual = strip_edited_by(test_input)
            expect = 'Gibson Catberg'
            self.assertEqual(expect, actual)

        _t('ed. by Gibson Catberg')
        _t('Ed. by Gibson Catberg')
        _t('edited by Gibson Catberg')
        _t('Edited by Gibson Catberg')


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


class TestNameParser(TestCase):
    def test_thirdparty_nameparser_is_available(self):
        self.assertIsNotNone(_nameparser)

    def test__parse_name_returns_expected_type_given_single_word_name(self):
        actual = _parse_name('foo')
        self.assertIsInstance(actual, dict)


@skipIf(*nameparser_unavailable())
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


@skipIf(*nameparser_unavailable())
class TestLastNameInitialsFormatter(TestCase):
    def test_formats_full_human_names(self):
        for given, expect in TESTDATA_NAME_LASTNAME_INITIALS:
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


@skipIf(*nameparser_unavailable())
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


@skipIf(*nameparser_unavailable())
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
        self._assert_unchanged(['Anandra Mitra'])

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


class TestFilterMultipleNames(TestCase):
    def _assert_filter_output_contains(self, expected, given):
        actual = filter_multiple_names(given)
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

    def test_removes_edited_by_from_start_of_a_name(self):
        for given_names in [
            ['edited by Gibson Sjöberg', 'Achim Weckar',         'Tomáš Navasod'],
            ['ed. by Gibson Sjöberg',    'Achim Weckar',         'Tomáš Navasod'],
            ['Edited by Gibson Sjöberg', 'Achim Weckar',         'Tomáš Navasod'],
            ['Ed. by Gibson Sjöberg',    'Achim Weckar',         'Tomáš Navasod'],
            ['Edited by Gibson Sjöberg', 'author Achim Weckar',  'Tomáš Navasod'],
            ['Ed. by Gibson Sjöberg',    'author Achim Weckar',  'Tomáš Navasod'],
            ['edited by Gibson Sjöberg', 'author: Achim Weckar', 'Tomáš Navasod'],
            ['ed. by Gibson Sjöberg',    'author: Achim Weckar', 'Tomáš Navasod'],
            ['Edited by Gibson Sjöberg', 'Author Achim Weckar',  'Tomáš Navasod'],
            ['Ed. by Gibson Sjöberg',    'Author Achim Weckar',  'Tomáš Navasod'],
            ['edited by Gibson Sjöberg', 'Author: Achim Weckar', 'Tomáš Navasod'],
            ['ed. by Gibson Sjöberg',    'Author: Achim Weckar', 'Tomáš Navasod'],
        ]:
            for name_ordering in itertools.permutations(given_names):
                self._assert_filter_output_contains(
                    expected=['Gibson Sjöberg', 'Achim Weckar', 'Tomáš Navasod'],
                    given=name_ordering
                )

    def test_removes_editor_from_list_of_names(self):
        self._assert_filter_returns(
            expected=['John P. Vecca'],
            given=['editor', 'John P. Vecca']
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

    def test_returns_empty_string_given_name_editor(self):
        self._assert_filter_does_not_pass('editor')
        self._assert_filter_does_not_pass('Editor')

    def test_returns_empty_string_given_name_author(self):
        self._assert_filter_does_not_pass('author')
        self._assert_filter_does_not_pass('Author')

    def test_returns_empty_string_given_name_foreword(self):
        self._assert_filter_does_not_pass('foreword')
        self._assert_filter_does_not_pass('Foreword')
