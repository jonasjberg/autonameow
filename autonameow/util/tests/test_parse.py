#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from util import fuzzy_date_parser2

VALUES = [
    (u'January 3, 2003', u'2003-01-03 00:00:00'),
    [u'Thursday, November 18', u'2016-11-18 00:00:00'],
    (u'7/24/04', u'2004-07-24 00:00:00'),
    (u'24-7-2004', u'2004-07-24 00:00:00'),
    (u'20040724_114321', u'2004-07-24 11:43:21'),
    (u'2004-07-24 11:43:21', u'2004-07-24 11:43:21'),
    (u'2004.07.24 11.43.21', u'2004-07-24 11:43:21'),
    (u'20040724114321', u'2004-07-24 11:43:21'),
    (u'2004.07.24T114321', u'2004-07-24 11:43:21')
]
# {'date': "5-10-1955", "dayfirst": True},  # a dict including the kwarg
# "5-10-1955",  # dayfirst, no kwarg
# 19950317,  # not a string
# "11AM on the 11th day of 11th month, in the year of our Lord 1945",


class ParseTestCase(unittest.TestCase):

    def setUp(self):
        self.parse = fuzzy_date_parser2.Parser()

    def tearDown(self):
        self.parse = None

    def test_date_parsing(self):
        for date_string, output_date in VALUES:
            print('date_string: \"%s\"' % date_string)
            d = self.parse.datetime(str(date_string))
            self.assertEqual(d, output_date, 'incorrect time/date')


if __name__ == '__main__':
    unittest.main()
