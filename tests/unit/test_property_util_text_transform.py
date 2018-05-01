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

from unittest import SkipTest, TestCase

try:
    from hypothesis import given
    from hypothesis.strategies import binary
    from hypothesis.strategies import booleans
    from hypothesis.strategies import characters
    from hypothesis.strategies import integers
    from hypothesis.strategies import text
except ImportError:
    raise SkipTest('Unable to import "hypothesis". Skipping ..')

from util.text.transform import normalize_unicode
from util.text.transform import simplify_unicode


class TestNormalizeUnicode(TestCase):
    @given(text())
    def test_text_input(self, s):
        actual = normalize_unicode(s)
        self.assertIsInstance(actual, str)


class TestSimplifyUnicode(TestCase):
    @given(text())
    def test_text_input(self, s):
        actual = simplify_unicode(s)
        self.assertIsInstance(actual, str)
