#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.parser import parse as dateparse

try:
    import parsedatetime.parsedatetime_consts as pdt
except ImportError:
    import parsedatetime as pdt

FAKE_YEAR = 9999
DEFAULT_FUTURE = datetime(FAKE_YEAR, 12, 31, 23, 59, 59)
DEFAULT_PAST = datetime(FAKE_YEAR, 1, 1, 0, 0)

consts = pdt.Constants(usePyICU=False)
consts.DOWParseStyle = -1  # "Monday" will be either today or the last Monday
CALENDAR = pdt.Calendar(consts)


class Parser(object):
    def __init__(self):
        pass

    def datetime(date_str, inclusive=False, default_hour=None, default_minute=None):
        """Parses a string containing a fuzzy date and returns a datetime.datetime object"""
        if not date_str:
            return None
        elif isinstance(date_str, datetime):
            return date_str

        # # dateutil.parser needs a string argument: let's make one from our
        # # `date' argument, according to a few reasonable conventions...:
        # kwargs = {}  # assume no named-args
        # if isinstance(date_str, (tuple, list)):
        #     date_str = ' '.join([str(x) for x in date_str])  # join up sequences
        # elif isinstance(date_str, int):
        #     date_str = str(date_str)  # stringify integers
        # elif isinstance(date_str, dict):
        #     kwargs = date_str  # accept named-args dicts
        #     date_str = kwargs.pop('date_str')  # with a 'date' str



        default_date = DEFAULT_FUTURE if inclusive else DEFAULT_PAST
        date = None
        year_present = False
        while not date:
            try:
                date = dateparse(date_str, default=default_date)
                if date.year == FAKE_YEAR:
                    date = datetime(datetime.now().year, date.timetuple()[1:6])
                else:
                    year_present = True
                flag = 1 if date.hour == date.minute == 0 else 2
                date = date.timetuple()
            except Exception as e:
                if e.args[0] == 'day is out of range for month':
                    y, m, d, H, M, S = default_date.timetuple()[:6]
                    default_date = datetime(y, m, d - 1, H, M, S)
                else:
                    date, flag = CALENDAR.parse(date_str)

        if not flag:  # Oops, unparsable.
            try:  # Try and parse this as a single year
                year = int(date_str)
                return datetime(year, 1, 1)
            except ValueError:
                return None
            except TypeError:
                return None

        if flag is 1:  # Date found, but no time. Use the default time.
            date = datetime(*date[:3],
                            hour=23 if inclusive else default_hour or 0,
                            minute=59 if inclusive else default_minute or 0,
                            second=59 if inclusive else 0)
        else:
            date = datetime(*date[:6])

        # Ugly heuristic: if the date is more than 4 weeks in the future, we got the year wrong.
        # Rather then this, we would like to see parsedatetime patched so we can tell it to prefer
        # past dates
        dt = datetime.now() - date
        if dt.days < -28 and not year_present:
            date = date.replace(date.year - 1)
        return date


    if __name__ == "__main__":
        test_values = (
            "January 3, 2003",  # a string
            # (5, "Oct", 55),  # a tuple
            "Thursday, November 18",  # longer string without year
            "7/24/04",  # a string with slashes
            "24-7-2004",  # European-format string
            '20040724_114321',
            '2004-07-24 11:43:21',
            '2004.07.24 11.43.21',
            '20040724114321',
            '2004.07.24T114321',
            '2010:01:31 16:12:51',
            # {'date': "5-10-1955", "dayfirst": True},  # a dict including the kwarg
            # "5-10-1955",  # dayfirst, no kwarg
            # 19950317,  # not a string
            # "11AM on the 11th day of 11th month, in the year of our Lord 1945",
        )

        FORMAT = '%-40s : %-40s'
        print(FORMAT % ("Input", "Result"))
        for input in test_values:  # testing date formats
            result = None
            try:
                result = dateparse(input)
            except Exception, error:
                result = 'FAILED (error: %s)' % (error)

            print(FORMAT % (input, result))
