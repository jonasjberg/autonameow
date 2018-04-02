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

import logging
import re
import string
from datetime import datetime

from core import constants as C
from core.exceptions import DependencyError
from util import encoding as enc

try:
    import pytz
except ImportError:
    raise DependencyError(missing_modules='pytz')


log = logging.getLogger(__name__)


def _extract_digits(string):
    # Local import to avoid circular imports within the 'util' module.
    from util.text import extract_digits
    return extract_digits(string)


def is_datetime_instance(thing):
    return bool(isinstance(thing, datetime))


def hyphenate_date(date_str):
    """
    Convert a date in 'YYYYMMDD' format to 'YYYY-MM-DD' format.
    This function is lifted as-is from utils.py in the "youtube-dl" project.
    """
    match = re.match(r'^(\d\d\d\d)(\d\d)(\d\d)$', date_str)
    if match is not None:
        return '-'.join(match.groups())
    return date_str


def _year_is_probable(int_year):
    """
    Check if year is "probable", meaning greater than 1900 and
    not in the future, I.E. greater than the current year.
    That is, simply: 1900 < year < this year

    Args:
        int_year: The year to test as an integer.

    Returns:
        True if the year is "probable", else False.
    """
    # Check if number of digits in "year" is less than three,
    # I.E. we got something like '86' (1986) or maybe '08' (2008).
    year = int_year
    if len(str(year)) <= 2:
        # Assume 50-99 becomes 1950-1999, and 0-49 becomes 2000-2049.
        if year < 50:
            year += 2000
        else:
            year += 1900

    try:
        year = datetime.strptime(str(year), '%Y')
    except (ValueError, TypeError):
        return False

    return date_is_probable(year)


def date_is_probable(date):
    """
    Check if date is "probable", meaning greater than 1900 and
    not in the future, I.E. greater than the year of todays date.
    That is, simply: 1900 < date < today

    Args:
        date: The date to test as an instance of 'datetime'.

    Returns:
        True if the date is "probable", else False.
    """
    if date.year > C.YEAR_UPPER_LIMIT.year:
        return False
    elif date.year < C.YEAR_LOWER_LIMIT.year:
        return False
    return True


DATE_SEP = r'[:\-._ /]?'
TIME_SEP = r'[T:\-. _]?'
DATE_REGEX = r'[12]\d{3}' + DATE_SEP + r'[01]\d' + DATE_SEP + r'[0123]\d'
TIME_REGEX = TIME_SEP + r'[012]\d' + TIME_SEP + r'[012345]\d(.[012345]\d)?'
DATETIME_REGEX = r'(' + DATE_REGEX + r'(' + TIME_REGEX + r')?)'

DT_PATTERN_1 = re.compile(DATETIME_REGEX)

# Expected date format:         2016:04:07
DT_PATTERN_2 = re.compile(r'(\d{4}-[01]\d-[0123]\d)')
DT_STRPTIME_FMT_2 = '%Y-%m-%d'

# Matches '(C) 2014' and similar.
DT_PATTERN_3 = re.compile(r'\( ?[Cc] ?\) ?([12]\d{3})')
DT_STRPTIME_FMT_3 = '%Y'


def regex_search_str(text):
    """
    Extracts date/time-information from a text string using regex searches.

    This is meant to be more "directed" than the bruteforce method.
    Return values (should) work the same as "bruteforce_str".

    :param text: the text to extract information from
    :return: list of any datetime-objects or None if nothing was found
    """
    MAX_NUMBER_OF_RESULTS = 10

    results = []
    if not text:
        return results

    if isinstance(text, list):
        text = ' '.join(text)

    # TODO: [TD0091] This code should be removed and/or rewritten ..
    # TODO: [TD0130] Implement general-purpose substring matching/extraction.

    for m_date, m_time, _ in re.findall(DT_PATTERN_1, text):
        # Skip if entries doesn't contain digits.
        m_date = _extract_digits(m_date)
        m_time = _extract_digits(m_time)

        if not m_date or not m_time:
            continue

        # Check if m_date is actually m_date *AND* m_date.
        if len(m_date) > 8 and m_date.endswith(m_time):
            m_date = m_date.replace(m_time, '')

        # Skip matches with unexpected number of digits.
        if len(m_date) != 8 or len(m_time) != 6:
            continue

        dt_fmt_1 = '%Y%m%d_%H%M%S'
        dt_str = m_date + '_' + m_time
        try:
            dt = datetime.strptime(dt_str, dt_fmt_1)
        except (TypeError, ValueError):
            pass
        else:
            if date_is_probable(dt):
                log.debug('Extracted datetime from text: "{}"'.format(dt))
                results.append(dt)

            if len(results) >= MAX_NUMBER_OF_RESULTS:
                log.debug(
                    'Hit max results limit {} ..'.format(MAX_NUMBER_OF_RESULTS)
                )
                return results

    for re_pattern, datetime_format in [(DT_PATTERN_2, DT_PATTERN_3),
                                        (DT_STRPTIME_FMT_2, DT_STRPTIME_FMT_3)]:
        for dt_str in re.findall(re_pattern, text):
            try:
                dt = datetime.strptime(dt_str, datetime_format)
            except (TypeError, ValueError):
                pass
            else:
                if date_is_probable(dt):
                    log.debug('Extracted datetime from text: "{}"'.format(dt))
                    results.append(dt)

                if len(results) >= MAX_NUMBER_OF_RESULTS:
                    log.debug(
                        'Hit max results limit {} ..'.format(MAX_NUMBER_OF_RESULTS)
                    )
                    return results

    log.debug('DATETIME Regex matcher found {:^3} matches'.format(len(results)))
    return results


def _parse_datetime_from_start_to_char_n_patterns(text, match_patterns):
    """
    Try to parse string into a datetime object using multiple patterns.

    Patterns are tuples with a date format and a number of characters to
    include when parsing that format, from the first character to N.

    Args:
        text: String to parse. Should be single line of text.
        match_patterns: List of tuples containing a date format and number of
                        characters in the text string to include, from 0 to N.

    Returns:
        The first successful datetime-conversion that is also "probable".
    """
    if not text or text.strip() is None:
        return None

    for date_format, num_chars in match_patterns:
        try:
            dt = datetime.strptime(text[:num_chars], date_format)
        except (TypeError, ValueError):
            pass
        else:
            if date_is_probable(dt):
                return dt

    return None


def match_special_case(text):
    """
    Matches variations of ISO-like (YYYY-mm-dd HH:MM:SS) date/time strings.

    NOTE(jonas): These are patterns I have personally used over the years
                 that I know are highly likely to be correct if in a filename.
                 This should be made much more flexible, using user-specified
                 or possibly "learned" patterns ..

    Args:
        text: Text line to extract datetime object from as a Unicode text.

    Returns: A date and time as an instance of 'datetime' or None.
    """
    if not text:
        return None

    subbed_text = re.sub(r'[-_T]', '-', text)
    # TODO: [TD0130] Implement general-purpose substring matching/extraction.
    # TODO: [TD0043] Allow specifying custom matching patterns in the config.
    MATCH_PATTERNS = [('%Y-%m-%d-%H-%M-%S', 19),
                      ('%Y-%m-%d-%H%M%S', 17),
                      ('%Y%m%d-%H%M%S', 15)]
    return _parse_datetime_from_start_to_char_n_patterns(subbed_text, MATCH_PATTERNS)


def match_special_case_no_date(text):
    """
    Matches strings with a ISO-like date on the form YYYY-mm-dd.

    NOTE(jonas): These are patterns I have personally used over the years
                 that I know are highly likely to be correct if in a filename.
                 This should be made much more flexible, using user-specified
                 or possibly "learned" patterns ..

    Args:
        text: Text to extract datetime object from as a Unicode string.

    Returns: A date as an instance of 'datetime' or None.
    """
    # TODO: [TD0130] Implement general-purpose substring matching/extraction.
    # TODO: [TD0043] Allow the user to tweak hardcoded settings.
    MATCH_PATTERNS = [('%Y-%m-%d', 10),
                      ('%Y%m%d', 8)]
    return _parse_datetime_from_start_to_char_n_patterns(text, MATCH_PATTERNS)


def match_android_messenger_filename(text):
    """
    Test if text (file name) matches that of Android messenger.
    Example: received_10151287690965808.jpeg
    :param text: text (file name) to test
    :return: list of datetime-objects if matches were found, otherwise None
    """
    # TODO: [TD0130] Implement general-purpose substring matching/extraction.

    # TODO: [cleanup] Fix this! It currently does not seem to work, at all.
    # Some hints are in the Android Messenger source code:
    # .. /Messaging.git/src/com/android/messaging/datamodel/action/DownloadMmsAction.java

    # $ date --date='@1453473286' --rfc-3339=seconds
    #   2016-01-22 15:34:46+01:00
    # $ 1453473286723

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
    # TODO: [TD0130] Implement general-purpose substring matching/extraction.
    if text is None or text.strip() is None:
        return None

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


def bruteforce_str(text):
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
    # TODO: [TD0130] Implement general-purpose substring matching/extraction.
    MAX_NUMBER_OF_RESULTS = 30

    if text is None:
        # log.debug('[bruteforce_str] Got empty text')
        return None
    else:
        text = text.strip()
        if not text:
            # log.debug('[bruteforce_str] Got empty text')
            return None

    text = enc.decode_(text)

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

            if bruteforce_str.matches_total >= MAX_NUMBER_OF_RESULTS:
                log.debug(
                    'Hit max results limit {} ..'.format(MAX_NUMBER_OF_RESULTS)
                )
                return results

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
    digits_only = _extract_digits(text)

    if not digits_only or len(digits_only) < 4:
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

                if bruteforce_str.matches_total >= MAX_NUMBER_OF_RESULTS:
                    log.debug('Hit max results limit {} ..'.format(
                        MAX_NUMBER_OF_RESULTS
                    ))
                    return results

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

                    if bruteforce_str.matches_total >= MAX_NUMBER_OF_RESULTS:
                        log.debug('Hit max results limit {} ..'.format(
                            MAX_NUMBER_OF_RESULTS
                        ))
                        return results

            # log.debug('Gave up after {} tries ..'.format(tries))
            # log.debug('Removing leading number '
            #               '({} --> {})'.format(digits, digits[1:]))
            digits = digits[1:]

    log.debug('Second matcher found {:>3} matches after {:>4} '
              'tries.'.format(bruteforce_str.matches_total, tries_total))
    return results


def match_screencapture_unixtime(text):
    """
    Match filenames created by the Chrome extension "Full Page Screen Capture".
    :param text: text to search for UNIX timestamp
    :return: datetime-object if a match is found, else None
    """
    # TODO: [TD0130] Implement general-purpose substring matching/extraction.
    if text:
        pattern = re.compile(r'.*(\d{13}).*')
        for t in re.findall(pattern, text):
            dt = match_any_unix_timestamp(t)
            if dt:
                return dt
    return None


def timezone_aware_to_naive(aware_datetime):
    """
    Removes timezone information from a datetime object to make it "naive".

    Args:
        aware_datetime: A "aware" datetime object with timezone-information.

    Returns:
        A new datetime object without timezone information.
    """
    # TODO: [TD0054] Represent datetime as UTC within autonameow.
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
    # TODO: [TD0054] Represent datetime as UTC within autonameow.
    return pytz.utc.localize(naive_datetime)


def find_isodate_like(text):
    # TODO: [TD0130] Implement general-purpose substring matching/extraction.
    if text and isinstance(text, str):
        unicode_text = text.strip()
        if unicode_text:
            string_digits = _extract_digits(unicode_text)
            try:
                dt = datetime.strptime(string_digits, '%Y%m%d%H%M%S')
            except (ValueError, TypeError):
                pass
            else:
                return dt
    return None
