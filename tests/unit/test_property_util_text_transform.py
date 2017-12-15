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

from unittest import (
    SkipTest,
    TestCase
)

from util.text.transform import (
    strip_accents
)

try:
    from hypothesis import given
    from hypothesis.strategies import (
        binary,
        booleans,
        characters,
        integers,
        text
    )
except ImportError:
    raise SkipTest('Unable to import "hypothesis". Skipping ..')


class TestStripAccents(TestCase):
    @given(text())
    def test_text_input(self, s):
        actual = strip_accents(s)
        self.assertIsInstance(actual, str)
