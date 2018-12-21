# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg <autonameow@jonasjberg.com>
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

from unittest import TestCase

from core.truths.known_metadata import canonical_values


class TestCanonicalValues(TestCase):
    def test_returns_empty_set_given_bad_fieldname(self):
        actual = canonical_values('foobarbaz')
        self.assertIsInstance(actual, set)

    def test_returns_non_empty_set_given_valid_fieldname(self):
        actual = canonical_values('publisher')
        self.assertIsInstance(actual, set)
        self.assertGreater(len(actual), 0)
