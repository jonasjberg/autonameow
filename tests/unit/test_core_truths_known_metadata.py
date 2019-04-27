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

from unittest import expectedFailure, TestCase

from core.truths.known_metadata import canonical_values
from core.truths.known_metadata import incorrect_values


class TestCanonicalValues(TestCase):
    def test_returns_empty_set_given_bad_fieldname(self):
        actual = canonical_values('foobarbaz')
        self.assertIsInstance(actual, set)

    def test_returns_non_empty_set_given_valid_fieldname(self):
        actual = canonical_values('publisher')
        self.assertIsInstance(actual, set)
        self.assertGreater(len(actual), 0)

    @expectedFailure
    def test_does_not_return_unknowns(self):
        actual = canonical_values('publisher')
        self.assertNotIn('UNKNOWN', actual)


class TestIncorrectValues(TestCase):
    def test_returns_empty_set_given_bad_fieldname(self):
        actual = incorrect_values('foobarbaz')
        self.assertIsInstance(actual, set)

    def test_returns_non_empty_set_given_valid_fieldname(self):
        actual = incorrect_values('publisher')
        self.assertIsInstance(actual, set)
        self.assertGreater(len(actual), 0)

    def test_returns_known_bad_creatortool_value(self):
        actual = incorrect_values('creatortool')
        self.assertIn('ProjectGutenberg', actual)
        self.assertIn('SWEDISH', actual)

    def test_returns_known_bad_language_value(self):
        actual = incorrect_values('language')
        self.assertIn('Calibre', actual)
        self.assertIn('Project Gutenberg', actual)

    def test_returns_known_bad_publisher_value(self):
        actual = incorrect_values('publisher')
        self.assertIn('Calibre', actual)
        self.assertIn('SWEDISH', actual)
