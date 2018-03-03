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

from collections import namedtuple
from unittest import (
    skipIf,
    TestCase,
)

from util.text.humannames import (
    _parse_name,
    format_name,
    format_name_list,
    HumanNameFormatter,
    HumanNameParser,
    LastNameInitialsFormatter,
    split_multiple_names,
    strip_author_et_al,
    strip_edited_by
)


TD = namedtuple('TD', 'Given Expect')

TESTDATA_NAME_LASTNAME_INITIALS = [
    # Special cases
    TD(Given='', Expect=''),
    TD(Given=' ', Expect=''),
    TD(Given='G', Expect='G.'),

    # First name only
    TD(Given='Gibson', Expect='G.'),
    TD(Given='Jonas', Expect='J.'),

    # First, last
    TD(Given='Gibson Sjöberg', Expect='Sjöberg G.'),
    TD(Given='Zhiguo Gong', Expect='Gong Z.'),
    TD(Given='Di Zou', Expect='Zou D.'),
    TD(Given='Muhammad Younas', Expect='Younas M.'),
    TD(Given='Katt Smulan', Expect='Smulan K.'),
    TD(Given='Irfan Awan', Expect='Awan I.'),
    TD(Given='Natalia Kryvinska', Expect='Kryvinska N.'),
    TD(Given='Christine Strauss', Expect='Strauss C.'),
    TD(Given='Yimin Wei', Expect='Wei Y.'),
    TD(Given='Weiyang Ding', Expect='Ding W.'),
    TD(Given='Russell, Bertrand', Expect='Russell B.'),
    TD(Given='Bertrand Russell', Expect='Russell B.'),

    # First, compound last
    TD(Given='Do van Thanh', Expect='vanThanh D.'),
    TD(Given='David Simchi-Levi', Expect='Simchi-Levi D.'),

    # First, middle, last
    TD(Given='Gibson Mjau Sjöberg', Expect='Sjöberg G.M.'),
    TD(Given='Hatt Katt Smulan', Expect='Smulan H.K.'),

    TD(Given='Friedrich Wilhelm Nietzsche', Expect='Nietzsche F.W.'),
    TD(Given='Nietzsche, Friedrich Wilhelm', Expect='Nietzsche F.W.'),

    # First, middle, middle, last
    TD(Given='Gibson Mjau Mjao Sjöberg', Expect='Sjöberg G.M.M.'),

    # Various Titles
    TD(Given='Sir Gibson Mjau Mjao Sjöberg', Expect='Sjöberg G.M.M.'),
    TD(Given='Lord Gibson Mjau Mjao Sjöberg', Expect='Sjöberg G.M.M.'),
    TD(Given='Catness Gibson Mjau Mjao Sjöberg', Expect='Sjöberg C.G.M.M.'),
    TD(Given='Sir Catness Gibson Mjau Mjao Sjöberg', Expect='Sjöberg C.G.M.M.'),

    # First. middle initial and last
    TD(Given='David B. Makofske', Expect='Makofske D.B.'),
    TD(Given='Michael J. Donahoo', Expect='Donahoo M.J.'),
    TD(Given='Kenneth L. Calvert', Expect='Calvert K.L.'),
    TD(Given='William T. Ziemba', Expect='Ziemba W.T.'),
    TD(Given='Raymond G. Vickson', Expect='Vickson R.G.'),

    # First. middle initial, middle initial, last
    TD(Given='Dickson K. W. Chiu', Expect='Chiu D.K.W.'),

    # First. middle initial, compound last
    TD(Given='Antonio J. Tallon-Ballesteros', Expect='Tallon-Ballesteros A.J.'),
    TD(Given='Tallon-Ballesteros A.J.', Expect='Tallon-Ballesteros A.J.'),

    # Input in output format
    TD(Given='Makofske D.B.', Expect='Makofske D.B.'),
    TD(Given='Donahoo M.J.', Expect='Donahoo M.J.'),
    TD(Given='Calvert K.L.', Expect='Calvert K.L.'),
    TD(Given='Gong Z.', Expect='Gong Z.'),
    TD(Given='Chiu D.K.W.', Expect='Chiu D.K.W.'),
    TD(Given='Zou D.', Expect='Zou D.'),
    TD(Given='Younas M.', Expect='Younas M.'),
    TD(Given='Smulan K.', Expect='Smulan K.'),
    TD(Given='Smulan H.K.', Expect='Smulan H.K.'),
    TD(Given='Awan I.', Expect='Awan I.'),
    TD(Given='Kryvinska N.', Expect='Kryvinska N.'),
    TD(Given='Strauss C.', Expect='Strauss C.'),
    TD(Given='vanThanh D.', Expect='vanThanh D.'),
    TD(Given='Ziemba W.T.', Expect='Ziemba W.T.'),
    TD(Given='Vickson R.G.', Expect='Vickson R.G.'),
    TD(Given='Wei Y.', Expect='Wei Y.'),
    TD(Given='Ding W.', Expect='Ding W.'),
    TD(Given='Russell B.', Expect='Russell B.'),
    TD(Given='Simchi-Levi D.', Expect='Simchi-Levi D.'),

    # Multiple authors; et al.
    TD(Given='Steve Anson ... [et al.]', Expect='Anson S.'),
    TD(Given='Steve Anson, et al.', Expect='Anson S.'),
    TD(Given='Steve Anson, ... et al.', Expect='Anson S.'),
    TD(Given='Steve Anson, ... et al', Expect='Anson S.'),
    TD(Given='Steve Anson ... et al', Expect='Anson S.'),
    TD(Given='Steve Anson ... [et al]', Expect='Anson S.'),
    TD(Given='Steve Anson ... [et al.]', Expect='Anson S.'),

    # Failed special cases
    TD(Given='Regina O. Obe', Expect='Obe R.O.'),
]

TESTDATA_LIST_OF_NAMES_LASTNAME_INITIALS = [
    TD(Given=['David B. Makofske', 'Michael J. Donahoo',
              'Kenneth L. Calvert'],
       Expect=['Calvert K.L.', 'Donahoo M.J.', 'Makofske D.B.']),

    TD(Given=['Zhiguo Gong', 'Dickson K. W. Chiu', 'Di Zou'],
       Expect=['Chiu D.K.W.', 'Gong Z.', 'Zou D.']),

    TD(Given=['Muhammad Younas', 'Irfan Awan', 'Natalia Kryvinska',
              'Christine Strauss', 'Do van Thanh'],
       Expect=['Awan I.', 'Kryvinska N.', 'Strauss C.', 'vanThanh D.',
               'Younas M.']),

    TD(Given=['William T. Ziemba', 'Raymond G. Vickson'],
       Expect=['Vickson R.G.', 'Ziemba W.T.']),

    TD(Given=['Yimin Wei', 'Weiyang Ding'],
       Expect=['Ding W.', 'Wei Y.']),

    TD(Given=['Charles Miller', 'Dino Dai Zovi'],
       Expect=['Miller C.', 'Zovi D.D.']),

    TD(Given=['Chrisina Jayne', 'Lazaros Iliadis'],
       Expect=['Iliadis L.', 'Jayne C.']),

    TD(Given=['Nihad Ahmad Hassan', 'Rami Hijazi'],
       Expect=['Hassan N.A.', 'Hijazi R.']),

    TD(Given=['David Simchi-Levi', 'Xin Chen', 'Julien Bramel'],
       Expect=['Bramel J.', 'Chen X.', 'Simchi-Levi D.']),

    TD(Given=['Hujun Yin', 'Yang Gao', 'Bin Li', 'Daoqiang Zhang',
              'Ming Yang', 'Yun Li', 'Frank Klawonn',
              'Antonio J. Tallon-Ballesteros'],
       Expect=['Gao Y.', 'Klawonn F.', 'Li B.', 'Li Y.',
               'Tallon-Ballesteros A.J.', 'Yang M.', 'Yin H.', 'Zhang D.']),

    # Failed special cases
    TD(Given=['Regina O. Obe', 'Leo S. Hsu'],
       Expect=['Hsu L.S.', 'Obe R.O.']),
]


def nameparser_unavailable():
    from thirdparty import nameparser as _nameparser
    return _nameparser is None, 'Failed to import "thirdparty.nameparser"'


class TeststripAuthorEtAl(TestCase):
    def test_strips_et_al_variations(self):
        def _t(test_input):
            actual = strip_author_et_al(test_input)
            expect = 'Gibson Catberg'
            self.assertEqual(actual, expect)

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


class TeststripEditedBy(TestCase):
    def test_strips_edited_by_variations(self):
        def _t(test_input):
            actual = strip_edited_by(test_input)
            expect = 'Gibson Catberg'
            self.assertEqual(expect, actual)

        _t('ed. by Gibson Catberg')
        _t('Ed. by Gibson Catberg')
        _t('edited by Gibson Catberg')
        _t('Edited by Gibson Catberg')


class TestNameParser(TestCase):
    def test_nameparser_return_type(self):
        # Make sure that 'nameparser' is indeed available.
        from thirdparty import nameparser
        self.assertIsNotNone(nameparser)

        actual = _parse_name('foo')
        self.assertIsInstance(actual, dict)


@skipIf(*nameparser_unavailable())
class TestHumanNameParser(TestCase):
    TESTDATA_FULLNAME_EXPECTED = [
        TD(Given=None, Expect={}),
        TD(Given='', Expect={}),
        TD(Given=' ', Expect={}),
        # NOTE: Includes empty values, which are NOT tested!
        TD(Given='G',
           Expect={'first': 'G',
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
        TD(Given='G',
           Expect={'first': 'G',
                   'first_list': ['G'],
                   'original': 'G'}),
        TD(Given='Gibson',
           Expect={'first': 'Gibson',
                   'first_list': ['Gibson'],
                   'original': 'Gibson'}),
        TD(Given='Gibson Sjöberg',
           Expect={'first': 'Gibson',
                   'first_list': ['Gibson'],
                   'last': 'Sjöberg',
                   'last_list': ['Sjöberg'],
                   'original': 'Gibson Sjöberg'}),
        TD(Given='Russell, Bertrand',
           Expect={'first': 'Bertrand',
                   'first_list': ['Bertrand'],
                   'last': 'Russell',
                   'last_list': ['Russell'],
                   'original': 'Russell, Bertrand'}),
        TD(Given='Bertrand Russell',
           Expect={'first': 'Bertrand',
                   'first_list': ['Bertrand'],
                   'last': 'Russell',
                   'last_list': ['Russell'],
                   'original': 'Bertrand Russell'}),
        TD(Given='Friedrich Wilhelm Nietzsche',
           Expect={'first': 'Friedrich',
                   'first_list': ['Friedrich'],
                   'last': 'Nietzsche',
                   'last_list': ['Nietzsche'],
                   'middle': 'Wilhelm',
                   'middle_list': ['Wilhelm'],
                   'original': 'Friedrich Wilhelm Nietzsche'}),
        TD(Given='Nietzsche, Friedrich Wilhelm',
           Expect={'first': 'Friedrich',
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
        actual = self.name_parser('foo')
        self.assertIsInstance(actual, dict)
        self.assertEqual(actual['original'], 'foo')

    def test_parses_name(self):
        actual = self.name_parser('Gibson Catson, Ph.D.')
        self.assertIsInstance(actual, dict)
        self.assertEqual(actual['first'], 'Gibson')
        self.assertEqual(actual['last'], 'Catson')
        self.assertEqual(actual['suffix'], 'Ph.D.')

    def test_preprocess_returns_empty_string_for_empty_input(self):
        def _assert_empty_string(given):
            actual = self.name_parser._preprocess(given)
            self.assertEqual(actual, '')

        _assert_empty_string('')
        _assert_empty_string(' ')
        _assert_empty_string('\t')
        _assert_empty_string('\t ')

    def _check_preprocess(self, given, expect):
        actual = self.name_parser._preprocess(given)
        self.assertEqual(actual, expect)

    def test_preprocess_pass_through_valid_input_as_is(self):
        self._check_preprocess('foo', 'foo')

    def test_preprocess_strips_whitespace(self):
        self._check_preprocess('foo ', 'foo')
        self._check_preprocess(' foo', 'foo')
        self._check_preprocess('\tfoo', 'foo')
        self._check_preprocess(' \tfoo', 'foo')
        self._check_preprocess('foo \t', 'foo')

    def test_preprocess_strips_trailing_characters(self):
        self._check_preprocess('foo,', 'foo')
        self._check_preprocess('foo,,', 'foo')

    def test_preprocess_strips_et_al(self):
        self._check_preprocess('foo et al.', 'foo')
        self._check_preprocess('foo, et al.', 'foo')

    def test_parses_human_names(self):
        for given, expect in self.TESTDATA_FULLNAME_EXPECTED:
            actual = self.name_parser(given)
            self.assertIsInstance(actual, dict)
            for k, v in actual.items():
                # Skip comparison of empty values for brevity.
                if v:
                    expected = expect.get(k)
                    self.assertEqual(v, expected,
                                     'Key "{}". Expected: "{!s}"  '
                                     'Got: "{!s}"'.format(k, expected, v))


class TestHumanNameFormatter(TestCase):
    def setUp(self):
        self.name_formatter = HumanNameFormatter()

    def test_call_raises_exception_gives_invalid_arguments(self):
        with self.assertRaises(AssertionError):
            _ = self.name_formatter('foo')

    def test_format_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            _ = self.name_formatter.format('foo')

    def test_call_raises_exception_given_none(self):
        with self.assertRaises(AssertionError):
            _ = self.name_formatter(None)


@skipIf(*nameparser_unavailable())
class TestLastNameInitialsFormatter(TestCase):
    def test_formats_full_human_names(self):
        for given, expect in TESTDATA_NAME_LASTNAME_INITIALS:
            actual = format_name(given, formatter=LastNameInitialsFormatter)
            self.assertEqual(actual, expect)

    def test_raises_exception_given_byte_strings(self):
        with self.assertRaises(AssertionError):
            _ = format_name(b'foo', formatter=LastNameInitialsFormatter)

    def test_returns_empty_string_for_none_or_empty_input(self):
        def _aE(test_input):
            actual = format_name(test_input,
                                 formatter=LastNameInitialsFormatter)
            self.assertEqual(actual, '')

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
            self.assertEqual(actual, expect)

    def test_raises_exception_given_invalid_formatter(self):
        invalid_formatter = True
        with self.assertRaises(AssertionError):
            _ = format_name('', invalid_formatter)

    def test_formats_full_name_given_valid_formatter(self):
        valid_formatter = LastNameInitialsFormatter

        for given, expect in TESTDATA_NAME_LASTNAME_INITIALS:
            actual = format_name(given, valid_formatter)
            self.assertEqual(actual, expect)


@skipIf(*nameparser_unavailable())
class TestFormatNameList(TestCase):
    def test_formats_list_of_full_human_names_with_default_formatter(self):
        for given, expect in TESTDATA_LIST_OF_NAMES_LASTNAME_INITIALS:
            actual = format_name_list(given)
            self.assertEqual(actual, expect)

    def test_raises_exception_given_invalid_formatter(self):
        invalid_formatter = True
        with self.assertRaises(AssertionError):
            _ = format_name_list('', invalid_formatter)

    def test_formats_list_of_full_human_names_given_valid_formatter(self):
        valid_formatter = LastNameInitialsFormatter

        for given, expect in TESTDATA_LIST_OF_NAMES_LASTNAME_INITIALS:
            actual = format_name_list(given, valid_formatter)
            self.assertEqual(actual, expect)


class TestSplitMultipleNames(TestCase):
    def _assert_that_it_returns(self, expected, given_any_of):
        for given in given_any_of:
            with self.subTest(given=given, expected=expected):
                actual = split_multiple_names(given)
                self.assertEqual(expected, actual)

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
