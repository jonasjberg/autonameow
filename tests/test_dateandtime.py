from datetime import datetime
from unittest import TestCase

from util.dateandtime import (
    hyphenate_date,
    match_unix_timestamp,
    match_special_case
)


class TestDateAndTime(TestCase):
    def test_hyphenate_date(self):
        self.assertEqual(hyphenate_date('20161224'), '2016-12-24')
        self.assertEqual(hyphenate_date('20161224T121314'), '20161224T121314')
        self.assertEqual(hyphenate_date('return as-is'), 'return as-is')

    def test_match_unix_timestamp(self):
        self.assertEqual(match_unix_timestamp('1464459165'),
                         datetime.strptime('20160528 201245', '%Y%m%d %H%M%S'))
        self.assertEqual(match_unix_timestamp('date --date="@1461786010" '
                                              '--rfc-3339=seconds'),
                         datetime.strptime('20160427 214010', '%Y%m%d %H%M%S'))
        self.assertEqual(match_unix_timestamp('1464459165038'),
                         datetime.strptime('20160528 201245', '%Y%m%d %H%M%S'))
        self.assertEqual(match_unix_timestamp('IMG_1464459165038.jpg'),
                         datetime.strptime('20160528 201245', '%Y%m%d %H%M%S'))
        self.assertEqual(match_unix_timestamp('IMG_1464459165038.jpg'
                                              '1464459165038'),
                         datetime.strptime('20160528 201245', '%Y%m%d %H%M%S'))
        self.assertEqual(match_unix_timestamp('1464459165038 1464459165038'),
                         datetime.strptime('20160528 201245', '%Y%m%d %H%M%S'))
        self.assertIsNone(match_unix_timestamp(None))
        self.assertIsNone(match_unix_timestamp(''))
        self.assertIsNone(match_unix_timestamp('123456'))
        self.assertIsNone(match_unix_timestamp('abc'))
        self.assertNotEqual(match_unix_timestamp('1464459165'),
                            datetime.strptime('20160427 214010', '%Y%m%d %H%M%S'))

    def test_match_special_case(self):
        self.assertIsNone(match_special_case(None))
        self.assertIsNone(match_special_case(''))
        self.assertIsNone(match_special_case(' '))
        self.assertIsNone(match_special_case('abc'))
        self.assertIsNotNone(match_special_case('2016-07-22_131730'))

        expected = datetime.strptime('20160722 131730', '%Y%m%d %H%M%S')
        self.assertEqual(expected, match_special_case('2016-07-22_131730'))
        self.assertEqual(expected, match_special_case('2016-07-22T131730'))
        self.assertNotEqual(expected, match_special_case('2016-07-22T131731'))
