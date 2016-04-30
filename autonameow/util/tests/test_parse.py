#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nose
from datetime import datetime

from util.fuzzy_date_parser2 import Parser

VALUES = [
    (u'January 3, 2003', '2003-01-03 00:00:00'),
    [u'Thursday, November 18', '2016-11-18 00:00:00'],
    (u'7/24/04', '2004-07-24 00:00:00'),
    (u'24-7-2004', '2004-07-24 00:00:00'),
    (u'20040724_114321', '2004-07-24 11:43:21'),
    (u'2004-07-24 11:43:21', '2004-07-24 11:43:21'),
    (u'2004.07.24 11.43.21', '2004-07-24 11:43:21'),
    (u'20040724114321', '2004-07-24 11:43:21'),
    (u'2004.07.24T114321', '2004-07-24 11:43:21')
]
# {'date': "5-10-1955", "dayfirst": True},  # a dict including the kwarg
# "5-10-1955",  # dayfirst, no kwarg
# 19950317,  # not a string
# "11AM on the 11th day of 11th month, in the year of our Lord 1945",


def test_date_parsing():

    parser = Parser()

    def string_to_datetime(str):
        return datetime.strptime(str, "%Y-%m-%d %H:%M:%S")

    for input_string, expected_date_string in VALUES:
        # print('input_string: \"%s\"' % input_string)
        result = parser.datetime(input_string)
        #expected_date = string_to_datetime(expected_date_string)
        #assert result == expected_date
