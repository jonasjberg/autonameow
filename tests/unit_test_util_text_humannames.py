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

from core.util import textutils


def nameparser_unavailable():
    from thirdparty import nameparser as _nameparser
    return _nameparser is None, 'Failed to import "thirdparty.nameparser"'


@unittest.skipIf(*nameparser_unavailable())
class TestFormatNameLastnameInitials(unittest.TestCase):
    def test_formats_author(self):
        def _aE(input_, expect):
            actual = textutils.format_name_lastname_initials(input_)
            self.assertEqual(actual, expect)

        _aE('Gibson', 'G.')
        _aE('Gibson Sjöberg', 'Sjöberg G.')
        _aE('Gibson Mjau Sjöberg', 'Sjöberg G.M.')
        _aE('Gibson Mjau Mjao Sjöberg', 'Sjöberg G.M.M.')
        _aE('Sir Gibson Mjau Mjao Sjöberg', 'Sjöberg G.M.M.')
        _aE('Lord Gibson Mjau Mjao Sjöberg', 'Sjöberg G.M.M.')
        _aE('Catness Gibson Mjau Mjao Sjöberg', 'Sjöberg C.G.M.M.')
        _aE('Sir Catness Gibson Mjau Mjao Sjöberg', 'Sjöberg C.G.M.M.')

        _aE('David B. Makofske', 'Makofske D.B.')
        _aE('Michael J. Donahoo', 'Donahoo M.J.')
        _aE('Kenneth L. Calvert', 'Calvert K.L.')
        _aE('Zhiguo Gong', 'Gong Z.')
        _aE('Dickson K. W. Chiu', 'Chiu D.K.W.')
        _aE('Di Zou', 'Zou D.')
        _aE('Muhammad Younas', 'Younas M.')
        _aE('Katt Smulan', 'Smulan K.')
        _aE('Hatt Katt Smulan', 'Smulan H.K.')
        _aE('Irfan Awan', 'Awan I.')
        _aE('Natalia Kryvinska', 'Kryvinska N.')
        _aE('Christine Strauss', 'Strauss C.')
        _aE('Do van Thanh', 'vanThanh D.')
        _aE('William T. Ziemba', 'Ziemba W.T.')
        _aE('Raymond G. Vickson', 'Vickson R.G.')
        _aE('Yimin Wei', 'Wei Y.')
        _aE('Weiyang Ding', 'Ding W.')

        _aE('David Simchi-Levi', 'Simchi-Levi D.')
        _aE('Antonio J. Tallon-Ballesteros', 'Tallon-Ballesteros A.J.')
        _aE('Makofske D.B.', 'Makofske D.B.')
        _aE('Donahoo M.J.', 'Donahoo M.J.')
        _aE('Calvert K.L.', 'Calvert K.L.')
        _aE('Gong Z.', 'Gong Z.')
        _aE('Chiu D.K.W.', 'Chiu D.K.W.')
        _aE('Zou D.', 'Zou D.')
        _aE('Younas M.', 'Younas M.')
        _aE('Smulan K.', 'Smulan K.')
        _aE('Smulan H.K.', 'Smulan H.K.')
        _aE('Awan I.', 'Awan I.')
        _aE('Kryvinska N.', 'Kryvinska N.')
        _aE('Strauss C.', 'Strauss C.')
        _aE('vanThanh D.', 'vanThanh D.')
        _aE('Ziemba W.T.', 'Ziemba W.T.')
        _aE('Vickson R.G.', 'Vickson R.G.')
        _aE('Wei Y.', 'Wei Y.')
        _aE('Ding W.', 'Ding W.')

        _aE('Russell, Bertrand', 'Russell B.')
        _aE('Bertrand Russell', 'Russell B.')
        _aE('Russell B.', 'Russell B.')

        _aE('Steve Anson ... [et al.]', 'Anson S.')
        _aE('Steve Anson, et al.', 'Anson S.')
        _aE('Steve Anson, ... et al.', 'Anson S.')
        _aE('Steve Anson, ... et al', 'Anson S.')
        _aE('Steve Anson ... et al', 'Anson S.')
        _aE('Steve Anson ... [et al]', 'Anson S.')
        _aE('Steve Anson ... [et al.]', 'Anson S.')

        _aE('Simchi-Levi D.', 'Simchi-Levi D.')
        _aE('Tallon-Ballesteros A.J.', 'Tallon-Ballesteros A.J.')


class TestFormatNamesLastnameInitials(unittest.TestCase):
    def test_formats_authors(self):
        def _aE(input_, expect):
            actual = textutils.format_names_lastname_initials(input_)
            self.assertEqual(actual, expect)

        _aE(input_=['David B. Makofske', 'Michael J. Donahoo',
                    'Kenneth L. Calvert'],
            expect=['Calvert K.L.', 'Donahoo M.J.', 'Makofske D.B.'])

        _aE(input_=['Zhiguo Gong', 'Dickson K. W. Chiu', 'Di Zou'],
            expect=['Chiu D.K.W.', 'Gong Z.', 'Zou D.'])

        _aE(input_=['Muhammad Younas', 'Irfan Awan', 'Natalia Kryvinska',
                    'Christine Strauss', 'Do van Thanh'],
            expect=['Awan I.', 'Kryvinska N.', 'Strauss C.', 'vanThanh D.',
                    'Younas M.'])

        _aE(input_=['William T. Ziemba', 'Raymond G. Vickson'],
            expect=['Vickson R.G.', 'Ziemba W.T.'])

        _aE(input_=['Yimin Wei', 'Weiyang Ding'],
            expect=['Ding W.', 'Wei Y.'])

        _aE(input_=['Charles Miller', 'Dino Dai Zovi'],
            expect=['Miller C.', 'Zovi D.D.'])

        _aE(input_=['Chrisina Jayne', 'Lazaros Iliadis'],
            expect=['Iliadis L.', 'Jayne C.'])

        _aE(input_=['Nihad Ahmad Hassan', 'Rami Hijazi'],
            expect=['Hassan N.A.', 'Hijazi R.'])

        _aE(input_=['David Simchi-Levi', 'Xin Chen', 'Julien Bramel'],
            expect=['Bramel J.', 'Chen X.', 'Simchi-Levi D.'])

        _aE(input_=['Hujun Yin', 'Yang Gao', 'Bin Li', 'Daoqiang Zhang',
                    'Ming Yang', 'Yun Li', 'Frank Klawonn',
                    'Antonio J. Tallon-Ballesteros'],
            expect=['Gao Y.', 'Klawonn F.', 'Li B.', 'Li Y.',
                    'Tallon-Ballesteros A.J.', 'Yang M.', 'Yin H.', 'Zhang D.'])


@unittest.skipIf(*nameparser_unavailable())
class TestParseName(unittest.TestCase):
    def test_parses_strings(self):
        actual = textutils.parse_name('foo')
        self.assertIsNotNone(actual)
        self.assertEqual(actual.original, 'foo')

    def test_parses_name(self):
        actual = textutils.parse_name('Gibson Catson, Ph.D.')
        self.assertIsNotNone(actual)
        self.assertEqual(actual.first, 'Gibson')
        self.assertEqual(actual.last, 'Catson')
        self.assertEqual(actual.suffix, 'Ph.D.')
