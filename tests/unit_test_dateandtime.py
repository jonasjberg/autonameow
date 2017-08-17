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

from datetime import datetime
from unittest import TestCase

from core.util.dateandtime import (
    hyphenate_date,
    match_any_unix_timestamp,
    match_special_case,
    to_datetime,
    naive_to_timezone_aware,
    timezone_aware_to_naive,
    find_isodate_like
)
import unit_utils as uu


class TestDateAndTime(TestCase):
    def test_hyphenate_date(self):
        self.assertEqual(hyphenate_date('20161224'), '2016-12-24')
        self.assertEqual(hyphenate_date('20161224T121314'), '20161224T121314')
        self.assertEqual(hyphenate_date('return as-is'), 'return as-is')


class TestMatchUnixTimestamp(TestCase):
    def test_match_unix_timestamp(self):
        expected = datetime.strptime('20160528 201245', '%Y%m%d %H%M%S')
        expected2 = datetime.strptime('20160427 214010', '%Y%m%d %H%M%S')
        self.assertIsInstance(expected, datetime)
        self.assertIsInstance(expected2, datetime)
        self.assertNotEqual(expected, expected2)

        self.assertEqual(expected, match_any_unix_timestamp('1464459165'))
        self.assertEqual(expected, match_any_unix_timestamp('1464459165038'))
        self.assertEqual(expected,
                         match_any_unix_timestamp('IMG_1464459165038.jpg'))
        self.assertEqual(expected,
                         match_any_unix_timestamp('IMG_1464459165038.jpg'
                                                  '1464459165038'))
        self.assertEqual(expected,
                         match_any_unix_timestamp('1464459165038 '
                                                  '1464459165038'))

        self.assertEqual(expected2,
                         match_any_unix_timestamp('date --date="@1461786010" '
                                                  '--rfc-3339=seconds'))
        self.assertNotEqual(expected2, match_any_unix_timestamp('1464459165'))

    def test_match_unix_timestamp_with_invalid_argument(self):
        self.assertIsNone(match_any_unix_timestamp(None))
        self.assertIsNone(match_any_unix_timestamp(''))
        self.assertIsNone(match_any_unix_timestamp(' '))
        self.assertIsNone(match_any_unix_timestamp('abc'))
        self.assertIsNone(match_any_unix_timestamp('123456'))


class TestMatchSpecialCase(TestCase):
    def setUp(self):
        self.expect = datetime.strptime('20160722 131730', '%Y%m%d %H%M%S')
        self.assertIsInstance(self.expect, datetime)

    def test_match_special_case_1st_variation(self):
        self.assertIsNotNone(match_special_case('2016-07-22_131730'))
        self.assertEqual(self.expect, match_special_case('2016-07-22_131730'))

    def test_match_special_case_2nd_variation(self):
        self.assertIsNotNone(match_special_case('2016-07-22T131730'))
        self.assertEqual(self.expect, match_special_case('2016-07-22T131730'))

    def test_match_special_case_3rd_variation(self):
        self.assertIsNotNone(match_special_case('20160722_131730'))
        self.assertEqual(self.expect, match_special_case('20160722_131730'))

    def test_match_special_case_4th_variation(self):
        self.assertIsNotNone(match_special_case('20160722T131730'))
        self.assertEqual(self.expect, match_special_case('20160722T131730'))

    def test_match_special_case_with_invalid_argument(self):
        self.assertIsNone(match_special_case(None))
        self.assertIsNone(match_special_case(''))
        self.assertIsNone(match_special_case(' '))
        self.assertIsNone(match_special_case('abc'))


class TestToDatetime(TestCase):
    # TODO: Handle time zone offsets properly!

    def setUp(self):
        self.TEST_DATA = [('2010:01:31 16:12:51', '2010-01-31 16:12:51'),
                          ('2016:01:11 12:41:32+00:00', '2016-01-11 12:41:32')]

    def test_does_not_return_none_given_valid_data(self):
        for given, expected in self.TEST_DATA:
            self.assertIsNotNone(to_datetime(given))

    def test_returns_expected_given_valid_data(self):
        for given, expected in self.TEST_DATA:
            self.assertEqual(str(to_datetime(given)), expected)


class TestNaiveToTimezoneAware(TestCase):
    def setUp(self):
        self.unaware = datetime.strptime('2016-01-11T12:41:32',
                                         '%Y-%m-%dT%H:%M:%S')
        self.aware = datetime.strptime('2016-01-11T12:41:32+0000',
                                       '%Y-%m-%dT%H:%M:%S%z')

    def test_setup(self):
        self.assertIsNotNone(self.unaware)
        self.assertIsNotNone(self.aware)

    def test_naive_dt_should_equal_aware_dt(self):
        self.assertEqual(naive_to_timezone_aware(self.unaware), self.aware)


class TestTimezoneAwareToNaive(TestCase):
    def setUp(self):
        self.unaware = datetime.strptime('2016-01-11T12:41:32',
                                         '%Y-%m-%dT%H:%M:%S')
        self.aware = datetime.strptime('2016-01-11T12:41:32+0000',
                                       '%Y-%m-%dT%H:%M:%S%z')

    def test_setup(self):
        self.assertIsNotNone(self.unaware)
        self.assertIsNotNone(self.aware)

    def test_aware_dt_should_forget_timezone_and_equal_unaware_dt(self):
        self.assertEqual(timezone_aware_to_naive(self.aware), self.unaware)


class FindIsoDateLike(TestCase):
    def setUp(self):
        self.expected = uu.str_to_datetime('2016-07-22 131730')
        self.assertIsInstance(self.expected, datetime)

    def test_invalid_argument_raises_value_error(self):
        def _assert_raises(test_data):
            with self.assertRaises(ValueError):
                find_isodate_like(test_data)

        _assert_raises(None)
        _assert_raises('')
        _assert_raises(' ')
        _assert_raises('  ')

    def _assert_none(self, test_data):
        self.assertIsNone(find_isodate_like(test_data))

    def test_returns_none_for_no_possible_matches(self):
        def _assert_none(test_data):
            self.assertIsNone(find_isodate_like(test_data))

        self._assert_none('abc')
        self._assert_none(' a ')
        self._assert_none(' 1 ')
        self._assert_none('1')
        self._assert_none('12')
        self._assert_none('123')
        self._assert_none('1234')
        self._assert_none('12345678912345')

    def test_returns_none_for_out_of_range_date_or_time(self):
        self._assert_none('0000-07-22_131730')
        self._assert_none('2016-07-22_131799')
        self._assert_none('2016-13-22_131730')
        self._assert_none('2016-07-99_131730')
        self._assert_none('2016-07-22_251730')
        self._assert_none('2016-07-22_136130')
        self._assert_none('2016-07-22_131761')

    def test_match_special_case_1st_variation(self):
        self.assertEqual(self.expected, find_isodate_like('2016-07-22_131730'))

        datetime9999 = uu.str_to_datetime('9999-07-22 131730')
        self.assertEqual(datetime9999, find_isodate_like('9999-07-22_131730'))

    def test_match_special_case_2nd_variation(self):
        self.assertIsNotNone(match_special_case('2016-07-22T131730'))
        self.assertEqual(self.expected, find_isodate_like('2016-07-22T131730'))

    def test_match_special_case_3rd_variation(self):
        self.assertIsNotNone(match_special_case('20160722_131730'))
        self.assertEqual(self.expected, find_isodate_like('20160722_131730'))

    def test_match_special_case_4th_variation(self):
        self.assertIsNotNone(match_special_case('20160722T131730'))
        self.assertEqual(self.expected, find_isodate_like('20160722T131730'))
