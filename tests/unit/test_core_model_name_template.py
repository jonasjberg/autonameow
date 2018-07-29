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

from core.model.name_template import NameTemplate
from core.model.name_template import template_placeholder_substrings


def _get_nametemplate(*args, **kwargs):
    return NameTemplate(*args, **kwargs)


class TestNameTemplate(TestCase):
    def test_instantiated_name_template_is_not_none_given_unicode_str(self):
        nt = _get_nametemplate('foo')
        self.assertIsNotNone(nt)

    def test_str_placeholders(self):
        nta = _get_nametemplate('foo')
        self.assertEqual([], nta.str_placeholders)

        ntb = _get_nametemplate('{foo}')
        self.assertEqual(['foo'], ntb.str_placeholders)

        ntc = _get_nametemplate('{foo} bar {baz}')
        self.assertEqual(['foo', 'baz'], ntc.str_placeholders)

    def test___str__(self):
        nta = _get_nametemplate('foo')
        self.assertEqual('foo', str(nta))

        ntb = _get_nametemplate('{foo}')
        self.assertEqual('{foo}', str(ntb))

        ntc = _get_nametemplate('{foo} bar {baz}')
        self.assertEqual('{foo} bar {baz}', str(ntc))


class TestFormatStringPlaceholders(TestCase):
    def test_raises_exception_when_given_bad_arguments(self):
        for bad_arg in [
            None,
            False,
            1,
            1.0,
            b'', b' ', b'foo', b'{foo}',
            object(),
        ]:
            with self.subTest(given=bad_arg):
                with self.assertRaises(AssertionError):
                    template_placeholder_substrings(bad_arg)

    def _assert_template(self, template, placeholders):
        actual = template_placeholder_substrings(template)
        self.assertEqual(placeholders, actual)

    def test_returns_no_placeholders_if_template_is_empty_or_whitespace(self):
        self._assert_template('', placeholders=[])
        self._assert_template(' ', placeholders=[])

    def test_returns_empty_list_given_template_without_placeholders(self):
        self._assert_template('abc', placeholders=[])
        self._assert_template('abc}', placeholders=[])
        self._assert_template('{abc', placeholders=[])
        self._assert_template('{abc {foo', placeholders=[])
        self._assert_template('{abc foo}', placeholders=[])

    def test_returns_expected_given_template_with_one_valid_placeholder(self):
        self._assert_template('abc {foo}', placeholders=['foo'])
        self._assert_template('abc {foo}', placeholders=['foo'])
        self._assert_template('{abc {foo}', placeholders=['foo'])
        self._assert_template('abc} {foo}', placeholders=['foo'])
        self._assert_template('{abc def} {foo}', placeholders=['foo'])
        self._assert_template('abc{ def} {foo}', placeholders=['foo'])

    def test_returns_expected_given_template_with_two_unique_placeholders(self):
        self._assert_template('{abc} {foo}', placeholders=['abc', 'foo'])
        self._assert_template('{abc} abc {foo}', placeholders=['abc', 'foo'])
        self._assert_template('{abc} {{foo}', placeholders=['abc', 'foo'])
        self._assert_template('{abc} {abc {foo}', placeholders=['abc', 'foo'])
        self._assert_template('{abc} {abc }{foo}', placeholders=['abc', 'foo'])

    def test_returns_expected_given_template_with_repeated_placeholders(self):
        self._assert_template('{foo} {foo}', placeholders=['foo', 'foo'])
        self._assert_template('{foo} abc {foo}', placeholders=['foo', 'foo'])
        self._assert_template('{foo} {foo}', placeholders=['foo', 'foo'])
        self._assert_template('{foo} {abc {foo}', placeholders=['foo', 'foo'])
        self._assert_template('{foo} abc} {foo}', placeholders=['foo', 'foo'])
        self._assert_template('{foo} {abc } {foo}', placeholders=['foo', 'foo'])
        self._assert_template('{foo} {abc} {foo}', placeholders=['foo', 'abc', 'foo'])
        self._assert_template('{abc} {abc} {foo}', placeholders=['abc', 'abc', 'foo'])
