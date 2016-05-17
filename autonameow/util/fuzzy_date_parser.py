# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

#import dateutil.parser
import logging
import time, datetime
import re

OPT_TODAY = frozenset(['t', 'today'])
OPT_YESTERDAY = frozenset(['y', 'yesterday'])


class DateParse(object):
    @staticmethod
    def day(date_string):
        today = datetime.date.today()
        date_string = date_string.strip().lower()
        if date_string in OPT_TODAY:
            return datetime.date(today.year, today.month, today.day)
        elif date_string in OPT_YESTERDAY:
            return datetime.date(today.year, today.month,
                                 today.day) - datetime.timedelta(days=1)
        elif re.search(r'(\d{1,3}|a) days? ago', date_string):
            return DateParse.n_day(date_string)
        else:
            return DateParse.date(date_string)

    @staticmethod
    def n_day(date_string):
        """
        date_string string in format "(number|a) day(s) ago"
        """
        today = datetime.date.today()
        match = re.match(r'(\d{1,3}|a) days? ago', date_string)
        groups = match.groups()
        if groups:
            decrement = groups[0]
            if decrement == 'a':
                decrement = 1
            return today - datetime.timedelta(days=int(decrement))
        return None

    @staticmethod
    def date(date_string):
        if date_string is None:
            return None

        SEPARATOR_CHARS = ['/', '-', ',', '.', ':', '_']
        for char in SEPARATOR_CHARS:
            date_string = date_string.replace(char, ' ')

        # If the string is all numbers without separators, add in spaces at
        # set locations.
        if date_string.isdigit() and len(date_string) == 8:
            d = date_string
            d = d[:4] + ' ' + d[4:6] + ' ' + d[6:8]
            date_string = d

        date_formats_with_year = ['%m %d %Y', '%Y %m %d', '%B %d %Y',
                                  '%b %d %Y',
                                  '%m %d %y', '%y %m %d', '%B %d %y',
                                  '%B %d %y', ]

        date_formats_without_year = ['%m %d', '%d %B', '%B %d',
                                     '%d %b', '%b %d']

        for format in date_formats_with_year:
            try:
                result = time.strptime(date_string, format)
                return datetime.date(result.tm_year, result.tm_mon,
                                     result.tm_mday)
            except ValueError:
                pass

        for format in date_formats_without_year:
            try:
                result = time.strptime(date_string, format)
                year = datetime.date.today().year
                return datetime.date(year, result.tm_mon, result.tm_mday)
            except ValueError:
                pass

        return None

    @staticmethod
    def time(time_string):
        if time_string is None:
            return None

        SEPARATOR_CHARS = ['-', '.', ':']
        for char in SEPARATOR_CHARS:
            time_string = time_string.replace(char, ' ')

        # If the string is all numbers without separators, add in spaces at
        # set locations.
        if time_string.isdigit() and len(time_string) == 6:
            s = time_string
            s = s[:2] + ' ' + s[2:4] + ' ' + s[4:6]
            time_string = s

        # Match time, for instance: 19:29:07
        match = re.match('([0123]\d)[:.-]?([012345]\d)[:.-]?([012345]\d)?',
                         time_string)
        # groups = match.groups()
        # if groups:
        #     print(groups)
        # return None

        time_formats = ['%H %M %S', '%H %M xx', '%H xx xx']

        for format in time_formats:
            try:
                result = time.strptime(time_string, format)
                return datetime.time(result.tm_hour, result.tm_min,
                                     result.tm_sec)
            except ValueError:
                pass

        return None

    @staticmethod
    def datetime(str):
        if str is None:
            logging.warn('Got NULL string')
            return None

        if type(str) is datetime:
            logging.debug('Returning datetime-object as-is.')
            return str

        SEPARATOR_CHARS = ['/', '-', ',', '.', ':', '_']
        for char in SEPARATOR_CHARS:
            str = str.replace(char, ' ')

        digits = ""
        for c in str:
            if c.isdigit():
                digits += c
            return digits

        datetime_formats = ['%Y %m %d',
                            '%m %d %Y',
                            '%B %d %Y',

                            '%b %d %Y',
                            '%m %d %y',
                            '%y %m %d',

                            '%B %d %y',
                            '%B %d %y',



                            ]

        date_formats_without_year = ['%m %d', '%d %B', '%B %d',
                                     '%d %b', '%b %d']

        for format in date_formats_with_year:
            try:
                result = time.strptime(date_string, format)
                return datetime.date(result.tm_year, result.tm_mon,
                                     result.tm_mday)
            except ValueError:
                pass



# From 'Python Cookbook' pages 127 to 129
# 3.7 Fuzzy Parsing of Dates
# Credit: Andrea Cavalcanti
#
# Problem
# -------
# Your program needs to read and accept dates that don't conform
# to the datetime standard format of "yyyy, mm, dd".
#
# Solution
# --------
# The third-party dateutil.parser module provides a simple answer.

# Discussion
# ----------
# dateutil.parser's parse function works on a variety of date formats. This recipe
# demonstrates a few of them. The parser can handle English-language month-names
# and two- or four-digit years (with some constraints). When you call parse without
# named arguments, its default is to first try parsing the string argument in the follow-
# ing order: mm-dd-yy. If that does not make logical sense, as, for example, it doesn't
# for the '24-7-2004' string in the recipe, parse then tries dd-mm-yy. Lastly, it tries yy-
# mm-dd. If a "keyword" such as dayfirst or yearfirst is passed (as we do in one
# test), parse attempts to parse based on that keyword.
# The recipe tests define a few edge cases that a date parser might encounter, such as
# trying to pass the date as a tuple, an integer (ISO-formatted without spaces), and
# even a phrase. To allow testing of the keyword arguments, the try_parse_date function in
# the recipe also accepts a dictionary argument, expecting, in this case, to find in it the
# value of the string to be parsed in correspondence to key 'date', and passing the rest
# on to dateutil's parser as keyword arguments.
# dateutil's parser can provide a pretty good level of "fuzzy" parsing, given some hints
# to let it know which piece is, for example, the hour (such as the AM in the test
# phrase in this recipe). For production code, you should avoid relying on fuzzy pars-
# ing, and either do some kind of preprocessing, or at least provide some kind of
# mechanism for checking the accuracy of the parsed date.
#
# See Also
# --------
# For more on date-parsing algorithms, see dateutil documentation at https://
# moin.conectiva.com.br/DateUtil?action=highlight&value=DateUtil; for date han-
# dling, see the datetime documentation in the Library Reference.

# def try_parse_date(date):
#     # dateutil.parser needs a string argument: let's make one from our
#     # `date' argument, according to a few reasonable conventions...:
#     kwargs = {}  # assume no named-args
#     if isinstance(date, (tuple, list)):
#         date = ' '.join([str(x) for x in date])  # join up sequences
#     elif isinstance(date, int):
#         date = str(date)  # stringify integers
#     elif isinstance(date, dict):
#         kwargs = date  # accept named-args dicts
#         date = kwargs.pop('date')  # with a 'date' str

    # else:
    #     # date = re.sub("\s", "-", date)
    #     date = re.sub("[^0-9a-zA-Z_-]", "", date)

    # try:
    #     try:
    #         parsedate = dateutil.parser.parse(date, **kwargs)
    #         print 'Sharp %r -> %s' % (date, parsedate)
    #     except ValueError:
    #         parsedate = dateutil.parser.parse(date, fuzzy=True, **kwargs)
    #         print 'Fuzzy %r -> %s' % (date, parsedate)
    # except Exception, err:
    #     print 'Try as I may, I cannot parse %r (%s)' % (date, err)


# if __name__ == "__main__":
#     tests = (
#         "January 3, 2003",  # a string
#         (5, "Oct", 55),  # a tuple
#         "Thursday, November 18",  # longer string without year
#         "7/24/04",  # a string with slashes
#         "24-7-2004",  # European-format string
#         {'date': "5-10-1955", "dayfirst": True},  # a dict including the kwarg
#         "5-10-1955",  # dayfirst, no kwarg
#         19950317,  # not a string
#         "11AM on the 11th day of 11th month, in the year of our Lord 1945",
#     )
#     for test in tests:  # testing date formats
#         try_parse_date(test)  # try to parse
