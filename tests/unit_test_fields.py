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

from unittest import TestCase

from core.fields import (
    GenericField,
    GenericDateCreated,
    GenericDateModified
)


class TestGenericFieldBase(TestCase):
    def test_uri_returns_expected(self):
        actual = GenericField.uri()
        expected = '{}.{}.{}'.format(GenericField.meowuri_root.lower(),
                                     GenericField.meowuri_node_generic,
                                     GenericField.meowuri_leaf.lower())
        self.assertEqual(actual, expected)


class TestGenericFieldStr(TestCase):
    def test_uri_field_date_created(self):
        actual = GenericDateCreated.uri()
        self.assertEqual(actual, 'metadata.generic.datecreated')

    def test_uri_field_date_modified(self):
        actual = GenericDateModified.uri()
        self.assertEqual(actual, 'metadata.generic.datemodified')
