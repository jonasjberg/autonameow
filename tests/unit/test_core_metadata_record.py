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

from unittest import TestCase

from core.metadata.record import bundle
from core.metadata.record import Record


def _get_record(*args, **kwargs):
    return Record(*args, **kwargs)


def _bundle(*args, **kwargs):
    return bundle(*args, **kwargs)


class TestRecord(TestCase):
    def test_instance_created_without_arguments_is_not_none(self):
        self.assertIsNotNone(_get_record())

    def test_new_record_does_not_contain_any_fields(self):
        record = _get_record()

        def _assert_does_not_contain_field(field):
            actual = getattr(record, field)
            self.assertIsNone(actual)

        _assert_does_not_contain_field('author')
        _assert_does_not_contain_field('isbn')
        _assert_does_not_contain_field('publisher')
        _assert_does_not_contain_field('title')


class TestBundle(TestCase):
    def test_returns_record_given_a_dict_of_field_names_and_values(self):
        given = {
            'author': ['Gibson Sjöberg'],
            'title': 'Thy will Lick the Cheese',
            'publisher': 'Meow Publishing',
        }
        actual_bundled_record = _bundle(given)

        self.assertEqual(['Gibson Sjöberg'], actual_bundled_record.author)
        self.assertEqual('Thy will Lick the Cheese', actual_bundled_record.title)
        self.assertEqual('Meow Publishing', actual_bundled_record.publisher)
