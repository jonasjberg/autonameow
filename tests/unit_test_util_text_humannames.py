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

from collections import namedtuple
import unittest

from core.util.text.humannames import (
    format_name,
    format_name_list,
    HumanNameFormatter,
    LastNameInitialsFormatter,
    parse_name,
    strip_author_et_al
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
               'Tallon-Ballesteros A.J.', 'Yang M.', 'Yin H.', 'Zhang D.'])
]


def nameparser_unavailable():
    from thirdparty import nameparser as _nameparser
    return _nameparser is None, 'Failed to import "thirdparty.nameparser"'


class TeststripAuthorEtAl(unittest.TestCase):
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


@unittest.skipIf(*nameparser_unavailable())
class TestParseName(unittest.TestCase):
    def test_parses_strings(self):
        actual = parse_name('foo')
        self.assertIsNotNone(actual)
        self.assertEqual(actual.original, 'foo')

    def test_parses_name(self):
        actual = parse_name('Gibson Catson, Ph.D.')
        self.assertIsNotNone(actual)
        self.assertEqual(actual.first, 'Gibson')
        self.assertEqual(actual.last, 'Catson')
        self.assertEqual(actual.suffix, 'Ph.D.')


class TestHumanNameFormatter(unittest.TestCase):
    def setUp(self):
        self.name_formatter = HumanNameFormatter()

    def test_call_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            _ = self.name_formatter('foo')

    def test_format_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            _ = self.name_formatter.format('foo')

    def test_call_raises_exception_given_none(self):
        with self.assertRaises(AssertionError):
            _ = self.name_formatter(None)

    def test_preprocess_returns_empty_string_for_empty_input(self):
        def _assert_empty_string(given):
            actual = self.name_formatter._preprocess(given)
            self.assertEqual(actual, '')

        _assert_empty_string('')
        _assert_empty_string(' ')
        _assert_empty_string('\t')
        _assert_empty_string('\t ')

    def _check_preprocess(self, given, expect):
        actual = self.name_formatter._preprocess(given)
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


@unittest.skipIf(*nameparser_unavailable())
class TestLastNameInitialsFormatter(unittest.TestCase):
    def setUp(self):
        self.name_formatter = LastNameInitialsFormatter()

    def test_formats_full_human_names(self):
        for given, expect in TESTDATA_NAME_LASTNAME_INITIALS:
            actual = self.name_formatter(given)
            self.assertEqual(actual, expect)

    def test_raises_exception_given_byte_strings(self):
        with self.assertRaises(AssertionError):
            _ = self.name_formatter(b'foo')

    def test_raises_exception_given_none(self):
        with self.assertRaises(AssertionError):
            _ = self.name_formatter(None)

    def test_returns_empty_string_for_none_or_empty_input(self):
        def _aE(test_input):
            actual = self.name_formatter(test_input)
            self.assertEqual(actual, '')

        _aE('')
        _aE(' ')
        _aE('\t')
        _aE('\t ')


@unittest.skipIf(*nameparser_unavailable())
class TestFormatName(unittest.TestCase):
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


@unittest.skipIf(*nameparser_unavailable())
class TestFormatNameList(unittest.TestCase):
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
