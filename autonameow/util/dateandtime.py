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

import re
from datetime import datetime

from core import constants as C
from core.exceptions import DependencyError

try:
    import pytz
except ImportError:
    raise DependencyError(missing_modules='pytz')


def _extract_digits(s):
    # Local import to avoid circular imports within the 'util' module.
    from util.text import extract_digits
    return extract_digits(s)


def is_datetime_instance(thing):
    return bool(isinstance(thing, datetime))


def date_is_probable(date,
                     year_max=C.YEAR_UPPER_LIMIT.year,
                     year_min=C.YEAR_LOWER_LIMIT.year):
    """
    Checks if the year of a given date is "probable".

    Very simple probability test checks if the date lies between a lowest
    threshold year, 'year_min' and a highest threshold year, 'year_max'.

    Args:
        date (datetime): The date to test as an instance of 'datetime'.
        year_max (int): Optional maximum threshold for probable years.
        year_min (int): Optional minimum threshold for probable years.

    Returns:
        True if the date is "probable", else False.
    """
    return bool(year_min < date.year < year_max)


def _parse_datetime_and_check_if_probable(s, date_format):
    """
    Try to parse a string into a datetime object with a specific format.

    Args:
        s (str): Unicode string to parse.
        date_format (str): Unicode 'datetime' format string.

    Returns:
        An instance of 'datetime' if the string is parsed and deemed
        "probable", otherwise None.
    """
    assert isinstance(s, str)
    assert isinstance(date_format, str)

    try:
        dt = datetime.strptime(s, date_format)
    except (TypeError, ValueError):
        pass
    else:
        if date_is_probable(dt):
            return dt

    return None


def parse_datetime_from_start_to_char_n_patterns(s, match_patterns):
    """
    Try to parse a string into a datetime object using multiple patterns.

    Patterns are tuples with a date format and a number of characters to
    include when parsing that format, from the first character to N.

    Args:
        s (str): Unicode string to parse.
        match_patterns: List of tuples containing a date format string and
                        number of characters in the string to include,
                        from 0 to N.
    Returns:
        The first successful datetime-conversion that is also "probable".
    """
    assert isinstance(s, str)
    if not s.strip():
        return None

    for date_format, num_chars in match_patterns:
        partial_string = s[:num_chars]
        dt = _parse_datetime_and_check_if_probable(partial_string, date_format)
        if dt:
            return dt

    return None


def match_special_case(s):
    """
    Matches variations of ISO-like (YYYY-mm-dd HH:MM:SS) date/time in strings.

    NOTE(jonas): These are patterns I have personally used over the years
                 that I know are highly likely to be correct if in a filename.
                 This should be made much more flexible, using user-specified
                 or possibly "learned" patterns ..

    Args:
        s: Unicode string to attempt to extract a datetime object from.

    Returns: A "probable" time/date as an instance of 'datetime' or None.
    """
    assert isinstance(s, str)
    if not s.strip():
        return None

    modified_string = re.sub(r'[-_T]', '-', s).strip()

    # TODO: [TD0130] Implement general-purpose substring matching/extraction.
    # TODO: [TD0043] Allow specifying custom matching patterns in the config.
    # MATCH_PATTERNS = [('%Y-%m-%d-%H-%M-%S', 19),
    #                   ('%Y-%m-%d-%H%M%S', 17),
    #                   ('%Y%m%d-%H%M%S', 15)]
    DATETIME_FORMAT_FOR_N_CHARS = {
        19: '%Y-%m-%d-%H-%M-%S',
        17: '%Y-%m-%d-%H%M%S',
        15: '%Y%m%d-%H%M%S'
    }
    modified_string_len = len(modified_string)
    pattern = DATETIME_FORMAT_FOR_N_CHARS.get(modified_string_len)
    if not pattern:
        return None

    return _parse_datetime_and_check_if_probable(modified_string, pattern)


def match_special_case_no_date(s):
    """
    Matches variations of ISO-like (YYYY-mm-dd) dates in strings.

    NOTE(jonas): These are patterns I have personally used over the years
                 that I know are highly likely to be correct if in a filename.
                 This should be made much more flexible, using user-specified
                 or possibly "learned" patterns ..

    Args:
        s (str): Unicode string to attempt to extract a datetime object from.

    Returns: A "probable" date as an instance of 'datetime' or None.
    """
    assert isinstance(s, str)

    modified_string = re.sub(r'[^\d]+', '', s).strip()
    if not modified_string:
        return None

    # TODO: [TD0130] Implement general-purpose substring matching/extraction.
    # TODO: [TD0043] Allow the user to tweak hardcoded settings.
    DATETIME_FORMAT_FOR_N_CHARS = {
        10: '%Y-%m-%d',
        8: '%Y%m%d'
    }
    modified_string_len = len(modified_string)
    pattern = DATETIME_FORMAT_FOR_N_CHARS.get(modified_string_len)
    if not pattern:
        return None

    return _parse_datetime_and_check_if_probable(modified_string, pattern)


def match_macos_screenshot(s):
    """
    Matches date/time strings in default MacOS screenshot filenames.

    Args:
        s: Unicode string to attempt to extract a datetime object from.

    Returns: Any date/time as an instance of 'datetime' or None.
    """
    assert isinstance(s, str)

    match = re.search(r'(\d{4}-\d\d-\d\d at \d\d\.\d\d\.\d\d)', s)
    if match:
        try:
            return datetime.strptime(match.group(1), '%Y-%m-%d at %H.%M.%S')
        except (ValueError, TypeError):
            pass

    return None


def match_android_messenger_filename(text):
    """
    Test if text (file name) matches that of Android messenger.
    Example: received_10151287690965808.jpeg
    :param text: text (file name) to test
    :return: list of datetime-objects if matches were found, otherwise None
    """
    # TODO: [TD0130] Implement general-purpose substring matching/extraction.
    assert isinstance(text, str)
    if not text.strip():
        return None

    # TODO: [cleanup] Fix this! It currently does not seem to work, at all.
    # Some hints are in the Android Messenger source code:
    # .. /Messaging.git/src/com/android/messaging/datamodel/action/DownloadMmsAction.java

    # $ date --date='@1453473286' --rfc-3339=seconds
    #   2016-01-22 15:34:46+01:00
    # $ 1453473286723
    dt_pattern = re.compile(r'.*(received_)(\d{17})(\.jpe?g)?')

    results = list()
    for _, dt_str, _ in re.findall(dt_pattern, text):
        try:
            microseconds = int(dt_str[13:])
            ms = microseconds % 1000 * 1000
            dt = datetime.utcfromtimestamp(ms // 1000).replace(microsecond=ms)
        except ValueError:
            pass
        else:
            if date_is_probable(dt):
                results.append(dt)
    return results


def match_any_unix_timestamp(text):
    """
    Searches a string for UNIX "seconds since epoch" timestamps.

    Args:
        text (str): String to search for UNIX timestamp.

    Returns:
        The first "valid" date/time as an instance of 'datetime' or None.
    """
    # TODO: [TD0130] Implement general-purpose substring matching/extraction.
    assert isinstance(text, str)
    if not text.strip():
        return None

    match_iter = re.finditer(r'(\d{10,13})', text)

    for match in match_iter:
        digits = match.group(0)

        # Example Android phone file name: 1461786010455.jpg
        # Remove last 3 digits to be able to convert using GNU date:
        # $ date --date ='@1461786010'
        # ons 27 apr 2016 21:40:10 CEST
        if len(digits) == 13:
            digits = digits[:10]

        try:
            dt = datetime.fromtimestamp(float(digits))
        except (TypeError, ValueError):
            pass
        else:
            if date_is_probable(dt):
                return dt

    return None


def match_screencapture_unixtime(text):
    """
    Match filenames created by the Chrome extension "Full Page Screen Capture".
    :param text: text to search for UNIX timestamp
    :return: datetime-object if a match is found, else None
    """
    # TODO: [TD0130] Implement general-purpose substring matching/extraction.
    assert isinstance(text, str)
    if not text.strip():
        return None

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
