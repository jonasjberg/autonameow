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

import dateutil
import logging as log
import re
import string
from datetime import datetime, timedelta

import pytz
from dateutil import parser

from core import util
from core.util import textutils


def hyphenate_date(date_str):
    """
    Convert a date in 'YYYYMMDD' format to 'YYYY-MM-DD' format.
    This function is lifted as-is from utils.py in the "youtube-dl" project.
    """
    match = re.match(r'^(\d\d\d\d)(\d\d)(\d\d)$', date_str)
    if match is not None:
        return '-'.join(match.groups())
    else:
        return date_str


def nextyear(dt):
    # http://stackoverflow.com/a/11206511
    try:
        return dt.replace(year=dt.year+1)
    except ValueError:
        # February 29th in a leap year
        # Add 365 days instead to arrive at March 1st
        return dt + timedelta(days=365)


# TODO: [TD0043] Allow storing these in the configuration file.
YEAR_LOWER_LIMIT = datetime.strptime('1900', '%Y')
YEAR_UPPER_LIMIT = nextyear(datetime.today())


def _year_is_probable(year):
    """
    Check if year is "probable", meaning greater than 1900 and
    not in the future, I.E. greater than the current year.
    That is, simply: 1900 < year < this year
    :param year: Year to check, preferably as a datetime-object.
                 Other types will be converted if possible.
    :return: True if the year is probable.
             False if the year is not probable or a conversion to
             datetime-object failed.
    """
    if type(year) is not datetime:
        # Try to convert to integer, then from integer to datetime.
        try:
            year = int(year)
        except ValueError as ex:
            log.warning('Got unexpected type "{}". '
                        'Casting failed: {}'.format(type(year), ex))
            return False

        # Check if number of digits in "year" is less than three,
        # I.E. we got something like '86' (1986) or maybe '08' (2008).
        if year < 999:
            # Assume 50-99 becomes 1950-1999, and 0-49 becomes 2000-2049.
            if year < 50:
                year += 2000
            else:
                year += 1900

        if not isinstance(year, int):
            year = util.decode_(year)
        try:
            year = datetime.strptime(str(year), '%Y')
        except (ValueError, TypeError):
            log.warning('Failed converting "{}" '
                        'to datetime-object.'.format(year))
            return False

    if year.year > YEAR_UPPER_LIMIT.year:
        return False
    elif year.year < YEAR_LOWER_LIMIT.year:
        return False
    else:
        # Year lies within window, assume it is OK.
        return True


def date_is_probable(date):
    """
    Check if date is "probable", meaning greater than 1900 and
    not in the future, I.E. greater than the year of todays date.
    That is, simply: 1900 < date < today
    :param date: Date to check, preferably as a datetime-object.
                 Other types will be converted if possible.
    :return: True if the date is probable.
             False if the date is not probable or a conversion to
             datetime-object failed.
    """
    if type(date) is not datetime:
        log.warning('Got unexpected type "{}" '
                    '(expected datetime)'.format(type(date)))
        return False

    if date.year > YEAR_UPPER_LIMIT.year:
        return False
    elif date.year < YEAR_LOWER_LIMIT.year:
        return False
    else:
        # Date lies within window, assume it is OK.
        return True


def regex_search_str(text):
    """
    Extracts date/time-information from a text string using regex searches.

    This is meant to be more "directed" than the bruteforce method.
    Return values (should) work the same as "bruteforce_str".

    :param text: the text to extract information from
    :return: list of any datetime-objects or None if nothing was found
    """

    if isinstance(text, list):
        text = ' '.join(text)

    results = []

    # TODO: [TD0044] This code should be removed and/or rewritten.

    # TODO: [TD0004] Enforce encoding boundary for extracted data.
    text = util.decode_(text)

    DATE_SEP = r'[:\-._ /]?'
    TIME_SEP = r'[T:\-. _]?'
    DATE_REGEX = r'[12]\d{3}' + DATE_SEP + r'[01]\d' + DATE_SEP + r'[0123]\d'
    TIME_REGEX = TIME_SEP + r'[012]\d' + TIME_SEP + r'[012345]\d(.[012345]\d)?'
    DATETIME_REGEX = r'(' + DATE_REGEX + r'(' + TIME_REGEX + r')?)'

    try:
        # TODO: [hack] Fix this!
        dt_pattern_1 = re.compile(DATETIME_REGEX)
    except Exception as e:
        log.error(str(e))
        dt_pattern_1 = False

    # TODO: [hack] Fix this!
    if dt_pattern_1:
        matches = 0
        for m_date, m_time, m_time_ms in re.findall(dt_pattern_1, text):
            # Skip if entries doesn't contain digits.
            m_date = textutils.extract_digits(m_date)
            m_time = textutils.extract_digits(m_time)
            m_time_ms = textutils.extract_digits(m_time_ms)

            if m_date is None or m_time is None:
                continue

            # Check if m_date is actually m_date *AND* m_date.
            if len(m_date) > 8 and m_date.endswith(m_time):
                m_date = m_date.replace(m_time, '')

            if len(m_time) < 6:
                pass

            # Skip matches with unexpected number of digits.
            if len(m_date) != 8 or len(m_time) != 6:
                continue

            dt_fmt_1 = '%Y%m%d_%H%M%S'
            dt_str = (m_date + '_' + m_time).strip()
            try:
                dt = datetime.strptime(dt_str, dt_fmt_1)
            except (TypeError, ValueError):
                pass
            else:
                if date_is_probable(dt):
                    log.debug('Extracted datetime from text: "{}"'.format(dt))
                    results.append(dt)
                    matches += 1

    # Expected date format:         2016:04:07
    dt_pattern_2 = re.compile(r'(\d{4}-[01]\d-[0123]\d)')
    dt_fmt_2 = '%Y-%m-%d'
    for dt_str in re.findall(dt_pattern_2, text):
        # TODO: [TD0004] Enforce encoding boundary for extracted data.
        dt_str = util.decode_(dt_str)
        try:
            dt = datetime.strptime(dt_str, dt_fmt_2)
        except (TypeError, ValueError):
            pass
        else:
            if date_is_probable(dt):
                log.debug('Extracted datetime from text: "{}"'.format(dt))
                results.append(dt)
                matches += 1

    # Matches '(C) 2014' and similar.
    dt_pattern_3 = re.compile(r'\( ?[Cc] ?\) ?([12]\d{3})')
    dt_fmt_3 = '%Y'
    for dt_str in re.findall(dt_pattern_3, text):
        # TODO: [TD0004] Enforce encoding boundary for extracted data.
        dt_str = util.decode_(dt_str)
        try:
            dt = datetime.strptime(dt_str, dt_fmt_3)
        except (TypeError, ValueError):
            pass
        else:
            if date_is_probable(dt):
                log.debug('Extracted datetime from text: "{}"'.format(dt))
                results.append(dt)
                matches += 1

    log.debug('[DATETIME] Regex matcher found {:^3} matches'.format(matches))
    return results


def match_special_case(text):
    """
    Very special case that is almost guaranteed to be correct.
    That is my personal favorite naming scheme; 1992-12-24_121314
                                                1992-12-24T121314
    :param text: text to extract date/time from
    :return: datetime if found otherwise None
    """
    # TODO: [TD0043] Allow the user to tweak hardcoded settings.
    if text is None or text.strip() is None:
        return None

    # TODO: [TD0004] Enforce encoding boundary for extracted data.
    text = util.decode_(text)

    # TODO: [TD0043] Allow specifying custom matching patterns in the config.
    match_patterns = [('%Y-%m-%d_%H%M%S', 17),
                      ('%Y-%m-%dT%H%M%S', 17),
                      ('%Y%m%d_%H%M%S', 15),
                      ('%Y%m%dT%H%M%S', 15)]
    for mp, chars in match_patterns:
        try:
            dt = datetime.strptime(text[:chars], mp)
        except (TypeError, ValueError):
            log.debug('Failed matching very special case.')
        else:
            if date_is_probable(dt):
                log.debug('[DATETIME] Found very special case: '
                          '"{}"'.format(dt))
                return dt
    return None


def match_special_case_no_date(text):
    """
    Very special case that is almost guaranteed to be correct, date only.
    That is my personal favorite naming scheme: 1992-12-24
    :param text: text to extract date/time from
    :return: datetime if found otherwise None
    """
    # TODO: [TD0043] Allow the user to tweak hardcoded settings.
    text = util.decode_(text)
    try:
        dt = datetime.strptime(text[:10], '%Y-%m-%d')
    except (TypeError, ValueError):
        log.debug('Failed matching date only version of very special case.')
    else:
        if date_is_probable(dt):
            log.debug('[DATETIME] Found very special case, date only: '
                      '"{}"'.format(dt))
            return dt
    return None


def match_android_messenger_filename(text):
    """
    Test if text (file name) matches that of Android messenger.
    Example: received_10151287690965808.jpeg
    :param text: text (file name) to test
    :return: list of datetime-objects if matches were found, otherwise None
    """

    # TODO: [cleanup] Fix this! It currently does not seem to work, at all.
    # Some hints are in the Android Messenger source code:
    # .. /Messaging.git/src/com/android/messaging/datamodel/action/DownloadMmsAction.java

    # $ date --date='@1453473286' --rfc-3339=seconds
    #   2016-01-22 15:34:46+01:00
    # $ 1453473286723

    # TODO: [TD0004] Enforce encoding boundary for extracted data.
    text = util.decode_(text)

    results = []

    dt_pattern = re.compile(r'.*(received_)(\d{17})(\.jpe?g)?')
    for _, dt_str, _ in re.findall(dt_pattern, text):
        try:
            microsecond = int(dt_str[13:])
            ms = microsecond % 1000 * 1000
            dt = datetime.utcfromtimestamp(ms // 1000).replace(microsecond=ms)
        except ValueError as e:
            log.debug('Unable to extract datetime from "{}": {}'.format(dt_str,
                                                                        str(e)))
        else:
            if date_is_probable(dt):
                log.debug('Extracted datetime from Android messenger file '
                          'name text: "{}"'.format(dt.isoformat()))
                results.append(dt)

    return results


def match_any_unix_timestamp(text):
    """
    Match text against UNIX "seconds since epoch" timestamp.
    :param text: text to extract date/time from
    :return: datetime if found otherwise None
    """
    if text is None or text.strip() is None:
        return None

    # TODO: [TD0004] Enforce encoding boundary for extracted data.
    text = util.decode_(text)

    match_iter = re.finditer(r'(\d{10,13})', text)
    if match_iter is None:
        log.debug('Probably not a UNIX timestamp -- does not contain '
                  '10-13 consecutive digits.')
        return None

    for match in match_iter:
        digits = match.group(0)

        # Example Android phone file name: 1461786010455.jpg
        # Remove last 3 digits to be able to convert using GNU date:
        # $ date --date ='@1461786010'
        #   ons 27 apr 2016 21:40:10 CEST
        if len(digits) == 13:
            digits = digits[:10]

        # TODO: [TD0010] Returns at first "probable" date, should test all.
        try:
            digits = float(digits)
            dt = datetime.fromtimestamp(digits)
        except (TypeError, ValueError):
            log.debug('Failed matching UNIX timestamp.')
        else:
            if date_is_probable(dt):
                log.debug('Extracted date/time-info [{}] from UNIX timestamp '
                          '"{}"'.format(dt, text))
                return dt
    return None


def bruteforce_str(text, return_first_match=False):
    """
    Extracts date/time-information from a text string.

    Does a brute force extraction, trying a lot of different combinations.
    The result is a list of dicts, with keys named "prefix_000",
    "prefix_001", etc, after the order in which they were found.
    Some bad date/time-information is bound to be picked up.
    The method is split up into sections, with each section being increasingly
    liberal in what gets picked up, so the results produced by the last sections
    are likely to be less accurate compared to those produced by the first part.

    :param text: the text to extract information from
    :return: list of any datetime-objects or None if nothing was found
    """
    if text is None:
        # log.debug('[bruteforce_str] Got empty text')
        return None
    else:
        text = text.strip()
        if not text:
            # log.debug('[bruteforce_str] Got empty text')
            return None

    text = util.decode_(text)

    bruteforce_str.matches = bruteforce_str.matches_total = 0

    # Internal function checks result, adds to list of results if OK.
    # TODO: [TD0010] Include number of tries in the result to act as a weight;
    #                lower numbers more probable to be true positives.
    def validate_result(data):
        if date_is_probable(data):
            log.debug('Extracted datetime from text: [{}]'.format(data))
            results.append(data)
            bruteforce_str.matches += 1
            bruteforce_str.matches_total += 1
            if return_first_match:
                return data

    if len(text) < 4:
        return None

    number_digits_in_text = sum(c.isdigit() for c in text)
    if number_digits_in_text < 4:
        return None

    # Strip all letters from the left.
    text = text.lstrip(string.ascii_letters)
    text = text.lstrip('_-[](){}')

    results = []

    # ----------------------------------------------------------------
    # PART #1   -- pattern matching
    # This part does basic pattern matching on a slightly modified version
    # of the text. A bunch of preset patterns are tried, all of which does
    # the matching from the beginning of the text.

    for char in ['/', '-', ',', '.', ':', '_']:
        text = text.replace(char, '')

    # Replace "wildcard" parts, like '2016-02-xx', '2016-xx-xx', ..
    WILDCARDS = [['xx',   '01'],
                 ['XX',   '01'],
                 ['0x',   '01'],
                 ['0X',   '01'],
                 ['20xx', '2000'],
                 ['19XX', '1901']]
    for u_old, u_new in WILDCARDS:
        text = text.replace(u_old, u_new)

    text = text.strip()
    text = text.replace(' ', '')

    #               Chars   Date/time format        Example
    #               -----   ----------------        ----------------
    common_formats = [[14,  '%Y%m%d%H%M%S'],        # 19921224121314
                      [8,   '%Y%m%d'],              # 19921224
                      [6,   '%Y%m'],                # 199212
                      [4,   '%Y'],                  # 1992
                      [10,  '%m%d%Y'],              # 12241992
                      [8,   '%m%d%y'],              # 122492
                      [8,   '%d%m%y'],              # 241292
                      [8,   '%y%m%d'],              # 921224
                      [11,  '%b%d%Y'],              # Dec241992
                      [11,  '%d%b%Y'],              # 24Dec1992
                      [9,   '%b%d%y'],              # Dec2492
                      [9,   '%d%b%y'],              # 24Dec92
                      [20,  '%B%d%y'],              # December2492
                      [20,  '%B%d%Y']]              # December241992

    tries = tries_total = 0
    for chars, fmt in common_formats:
        if len(text) < chars:
            continue

        text_strip = text[:chars]
        tries += 1
        tries_total += 1
        try:
            dt = datetime.strptime(text_strip, fmt)
        except (TypeError, ValueError):
            pass
        else:
            # TODO: [TD0010] Include number of tries in the result to act as a
            #       weight; lower numbers more probable to be true positives.
            validate_result(dt)

    if results:
        log.debug('First matcher found  {:>3} matches after {:>4} '
                  'tries.'.format(bruteforce_str.matches, tries))
        return results
    else:
        log.debug('Gave up first approach after {:>4} tries.'.format(tries))

    # ----------------------------------------------------------------
    # PART #2   -- pattern matching on just the digits
    # This part works about the same as the previous one, except it
    # discards everything except digits in the text.

    # Try another approach, start by extracting all digits.
    digits_only = textutils.extract_digits(text)

    if len(digits_only) < 4:
        return results

    year_first = True
    digits = digits_only
    # Remove one number at a time from the front until first four digits
    # represent a probable year.
    while not _year_is_probable(int(digits[:4])) and year_first:
        digits = digits[1:]
        if len(digits) < 4:
            year_first = False

    if year_first:
        #                Chars  Date/time format   Example
        #                -----  ----------------   ----------------
        common_formats2 = [[14, '%Y%m%d%H%M%S'],    # 19921224121314
                           [12, '%Y%m%d%H%M'],      # 199212241213
                           [10, '%Y%m%d%H'],        # 1992122412
                           [8,  '%Y%m%d'],          # 19921224
                           [6,  '%Y%m'],            # 199212
                           [4,  '%Y']]              # 1992
        tries = 0
        for chars, fmt in common_formats2:
            digits_strip = digits[:chars]
            tries += 1
            tries_total += 1
            try:
                dt = datetime.strptime(digits_strip, fmt)
            except (TypeError, ValueError):
                pass
            else:
                # TODO: Include number of tries in the result as a weight.
                #       Lower numbers more probable to be true positives.
                validate_result(dt)

        # log.debug('Gave up after %d tries ..'.format(tries))

    # TODO: Examine this here below hacky conditional. Why is it there?
    if True:
        digits = digits_only
        while len(str(digits)) > 2:
            # log.debug('Assuming format other than year first.')
            #               Chars    Date/time format   Example
            #               -----    ----------------   ----------
            common_formats3 = [[8,   '%d%m%Y'],         # 24121992
                               [6,   '%d%m%y'],         # 241292
                               [8,   '%m%d%Y'],         # 12241992
                               [6,   '%m%d%y'],         # 122492
                               [6,   '%d%m%y'],         # 241292
                               [6,   '%y%m%d'],         # 921224
                               [6,   '%Y%m'],           # 199212
                               [4,   '%Y'],             # 1992
                               [2,   '%y']]             # 92
            tries = 0
            for chars, fmt in common_formats3:
                digits_strip = digits[:chars]
                tries += 1
                tries_total += 1
                try:
                    dt = datetime.strptime(digits_strip, fmt)
                except (TypeError, ValueError):
                    pass
                else:
                    # TODO: [BL002] Include number of tries in the result to
                    #       act as a weight; lower numbers more probable to be
                    #       true positives.
                    validate_result(dt)

            # log.debug('Gave up after {} tries ..'.format(tries))
            # log.debug('Removing leading number '
            #               '({} --> {})'.format(digits, digits[1:]))
            digits = digits[1:]

    log.debug('Second matcher found {:>3} matches after {:>4} '
              'tries.'.format(bruteforce_str.matches_total, tries_total))
    return results


def fuzzy_datetime(text, prefix):
    # TODO: [cleanup] Currently not used at all!
    dt = None
    try:
        try:
            dt = dateutil.parser.parse(text)
            print(('Sharp {} -> {}'.format(text, dt)))
        except ValueError:
            dt = dateutil.parser.parse(text, fuzzy=True)
            print(('Fuzzy {} -> {}'.format(text, dt)))
    except Exception as e:
        print(('Try as I may, I cannot parse {} ({})'.format(text, e)))

    return dt


def search_gmail(text, prefix):
    """
    Searches gmail content for date/time-information.
    :param text: the text to extract information from
    :param prefix: prefix this to the resulting dictionary keys
    :return: a list of dictionaries containing datetime-objects.
    """
    text = util.decode_(text)
    # TODO: [cleanup] Currently not used at all! Implement or remove.
    if type(text) is list:
        # log.debug('Converting list to string ..')
        text = ' '.join(text)

    if not text.lower().find('gmail'):
        # log.debug('Text does not contains "gmail", might not be a Gmail?')
        return

    results = {}

    # Expected date formats:         Fri, Jan 8, 2016 at 3:50 PM
    #                                1/11/2016
    SEP = r'[, ]'
    REGEX_GMAIL_LONG = re.compile(r'(\w{3,8})' + SEP + r'(\w{3,10}) (\d{1,2})'
                                  + SEP + r'([12]\d{3})' + r'( at )?' +
                                  r'(\d{1,2}:\d{1,2} [AP]M)')
    REGEX_GMAIL_SHORT = re.compile(r'\d{1,2}/\d{2}/[12]\d{3}')


def get_datetime_from_text(text, prefix='NULL'):
    """
    Extracts date/time-information from text.
    This method is used by both the text-analyzer and the pdf-analyzer.

    :param text: try to extract date/time-information from this text
    :param prefix: prefix this to the resulting dictionary keys
    :return: dictionary of lists of any datetime-objects found
             The dictionary is keyed by search method used to extract the
             datetime-objects.
    """
    # TODO: [cleanup][TD0044] Should this even be used at all?
    if text is None:
        log.warning('Got NULL argument')
        return None
    if prefix == 'NULL':
        pass
    # text = util.decode_(text)

    # TODO: [TD0044] Improve handling of generalized "text" from any source.
    #       (currently plain text and pdf documents)
    if type(text) == list:
        text = ' '.join(text)

    results_brute = []
    results_regex = []

    matches = 0
    text_split = text.split('\n')
    # log.debug('Try getting datetime from text split by newlines')
    for t in text_split:
        dt = bruteforce_str(t)
        if dt and dt is not None:
            results_brute.append(dt)
            matches += 1

    if matches == 0:
        # log.debug('No matches. Trying with text split by whitespace')
        text_split = text.split()
        for t in text_split:
            dt = bruteforce_str(t)
            if dt and dt is not None:
                results_brute.append(dt)
                matches += 1

    # TODO: [cleanup] Fix this here below. Looks completely broken.
    regex_match = 0
    dt_regex = regex_search_str(text)
    if dt_regex and dt_regex is not None:
        results_regex.append(dt_regex)
        regex_match += 1

    return results_regex, results_brute


def special_datetime_ocr_search(text):
    """
    Very special case. OCR text often mistakes "/" for "7", hence
    this search.
    Text actually contains:   2016/02/08
    OCR returns result:       2016702708
    :return:
    """
    # TODO: [TD0004] Enforce encoding boundary for extracted data.
    # TODO: [TD0044] Rework converting "raw data" to internal representations.
    text = util.decode_(text)

    pattern = re.compile(r'(\d{4}7[01]\d7[0123]\d)')
    dt_fmt = '%Y7%m7%d'
    for dt_str in re.findall(pattern, text):
        try:
            dt = datetime.strptime(dt_str, dt_fmt)
        except (TypeError, ValueError):
            pass
        else:
            if date_is_probable(dt):
                log.debug('[DATETIME] Special OCR search found {} '
                          'matches'.format(dt))
                return dt
    return None


def match_screencapture_unixtime(text):
    """
    Match filenames created by the Chrome extension "Full Page Screen Capture".
    :param text: text to search for UNIX timestamp
    :return: datetime-object if a match is found, else None
    """
    # TODO: [TD0004] Enforce encoding boundary for extracted data.
    text = util.decode_(text)

    pattern = re.compile(r'.*(\d{13}).*')
    for t in re.findall(pattern, text):
        dt = match_any_unix_timestamp(t)
        if dt:
            return dt
    return None


def to_datetime(datetime_string):
    """
    Convert a string with date/time information to a datetime-object.

    Args:
        datetime_string: Date/time data as a string.

    Returns:
        A datetime object representing the given input if successful.
    Raises:
        ValueError: An error occurred during the conversion.
        TypeError: An error occurred during the conversion.
    """
    # TODO: Handle timezone offsets properly!

    if datetime_string.endswith('+00:00'):
        datetime_string = datetime_string.replace('+00:00', '')
    elif datetime_string.endswith('+02:00'):
        datetime_string = datetime_string.replace('+02:00', '')

    REGEX_FORMAT_MAP = [(r'^\d{4}:\d{2}:\d{2} \d{2}:\d{2}:\d{2}$',
                         '%Y:%m:%d %H:%M:%S'),  # '2010:01:31 16:12:51'
                        ]

    for regex_pattern, datetime_format in REGEX_FORMAT_MAP:
        if re.match(regex_pattern, datetime_string):
            return datetime.strptime(datetime_string, datetime_format)

    try:
        datetime_object = parser.parse(datetime_string)
    except ValueError:
        raise ValueError
    except TypeError:
        raise TypeError
    else:
        return datetime_object


def timezone_aware_to_naive(aware_datetime):
    """
    Removes timezone information from a datetime object to make it "naive".

    Args:
        aware_datetime: A "aware" datetime object with timezone-information.

    Returns:
        A new datetime object without timezone information.
    """
    return aware_datetime.replace(tzinfo=None)


def naive_to_timezone_aware(naive_datetime):
    """
    Adds timezone information to a "naive" datetime to make it timezone-aware.

    Args:
        naive_datetime: A "naive" datetime object.

    Returns:
        A new datetime object with localized timezone information.
    """
    # Reference:  https://stackoverflow.com/a/7065242/7802196
    return pytz.utc.localize(naive_datetime)


def find_isodate_like(unicode_text):
    if not unicode_text:
        raise ValueError('Got None/empty argument')

    unicode_text = unicode_text.strip()
    if not unicode_text:
        raise ValueError('Got empty string argument')

    string_digits = textutils.extract_digits(unicode_text)
    try:
        dt = datetime.strptime(string_digits, '%Y%m%d%H%M%S')
    except (ValueError, TypeError):
        return None
    else:
        return dt
