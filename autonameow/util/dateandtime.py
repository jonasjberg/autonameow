# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

import logging
import re
import string
from datetime import datetime, timedelta

import dateutil
import sys

from util import misc


def delta_frac(self, delta):
    """
    Calculate time delta between datetime objects.
    :param self:
    :param delta:
    :return:
    """
    delta_mins, delta_secs = divmod(delta.seconds, 60)
    delta_hours, delta_mins = divmod(delta_mins, 60)
    return {'hours': delta_hours, 'mins': delta_mins, 'secs': delta_secs}


def nextyear(dt):
    # http://stackoverflow.com/a/11206511
    try:
        return dt.replace(year=dt.year+1)
    except ValueError:
        # February 29th in a leap year
        # Add 365 days instead to arrive at March 1st
        return dt + timedelta(days=365)


# TODO: Use separate file for globals like these?
#       Should probably be stored in a configuration file along with other
#       user-modifiable settings.
year_lower_limit = datetime.strptime('1900', '%Y')
year_upper_limit = nextyear(datetime.today())


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
    # logging.debug('Checking probability of [{}] {}'.format(year, type(year)))
    if type(year) is not datetime:
        # Year is some other type.
        # Try to convert to integer, then from integer to datetime.
        try:
            year = int(year)
        except ValueError as ex:
            logging.warning('Got unexpected type "{}". '
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

        try:
            year = datetime.strptime(str(year), '%Y')
        except TypeError:
            logging.warning('Failed converting "{}" '
                            'to datetime-object.'.format(year))
            return False

    # Do date comparisons using datetime-objects.
    if year.year > year_upper_limit.year:
        # logging.debug('Skipping future date [{}]'.format(date))
        return False
    elif year.year < year_lower_limit.year:
        # logging.debug('Skipping non-probable (<{}) date '
        #               '[{}]'.format(year_lower_limit, date))
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
    # logging.debug('Checking probability of [{}] {}'.format(date, type(date)))
    if type(date) is not datetime:
        logging.warning('Got unexpected type "{}" '
                        '(expected datetime)'.format(type(date)))
        return False

    # Do date comparisons using datetime-objects.
    if date.year > year_upper_limit.year:
        # logging.debug('Skipping future date [{}]'.format(date))
        return False
    elif date.year < year_lower_limit.year:
        # logging.debug('Skipping non-probable (<{}) date '
        #               '[{}]'.format(year_lower_limit, date))
        return False
    else:
        # Date lies within window, assume it is OK.
        return True


def search_standard_formats(text, prefix):
    """
    Matches against standard formats.
    :param text: the text to extract information from
    :param prefix: prefix this to the resulting dictionary keys
    :return: a list of dictionaries containing datetime-objects.
    """
    # TODO: Implement ..
    pass


def regex_search_str(text):
    """
    Extracts date/time-information from a text string using regex searches.

    This is meant to be more "directed" than the bruteforce method.
    Return values (should) work the same as "bruteforce_str".

    :param text: the text to extract information from
    :return: list of any datetime-objects or None if nothing was found
    """

    # Create empty list to hold all results.
    results = []

    if type(text) is list:
        logging.warn('Converting list to string ..')
        text = ' '.join(text)

    DATE_SEP = "[:\-._ \/]?"
    TIME_SEP = "[T:\-. _]?"
    DATE_REGEX = '[12]\d{3}' + DATE_SEP + '[01]\d' + DATE_SEP + '[0123]\d'
    TIME_REGEX = TIME_SEP + '[012]\d' + TIME_SEP + '[012345]\d(.[012345]\d)?'
    DATETIME_REGEX = '(' + DATE_REGEX + '(' + TIME_REGEX + ')?)'

    dt_pattern_1 = re.compile(DATETIME_REGEX)

    matches = 0
    for m_date, m_time, m_time_ms in re.findall(dt_pattern_1, text):
        # Extract digits, skip if entries contain no digits.
        m_date = misc.extract_digits(m_date)
        m_time = misc.extract_digits(m_time)
        m_time_ms = misc.extract_digits(m_time_ms)

        if m_date is None or m_time is None:
            continue

        # Check if m_date is actually m_date *AND* m_date.
        if len(m_date) > 8 and m_date.endswith(m_time):
            # logging.debug('m_date contains m_date *AND* m_time')
            m_date = m_date.replace(m_time, '')

        if len(m_time) < 6:
            # logging.debug('len(m_time) < 6 .. m_time_ms is '
            #               '"{}"'.format(m_time_ms))
            pass

        # Skip matches with unexpected number of digits.
        if len(m_date) != 8 or len(m_time) != 6:
            continue

        logging.debug('m_date {:10} : {}'.format(type(m_date), m_date))
        logging.debug('m_time {:10} : {}'.format(type(m_time), m_time))
        logging.debug('m_time_ms {:10} : {}'.format(type(m_time_ms), m_time_ms))
        logging.debug('---')

        dt_fmt_1 = '%Y%m%d_%H%M%S'
        dt_str = (m_date + '_' + m_time).strip()
        try:
            logging.debug(
                'Trying to match [{:13}] to [{}] ..'.format(dt_fmt_1, dt_str))
            dt = datetime.strptime(dt_str, dt_fmt_1)
        except ValueError:
            pass
        else:
            if date_is_probable(dt):
                logging.debug('Extracted datetime from text: '
                              '[{}]'.format(dt))
                results += dt
                matches += 1

    # Expected date format:         2016:04:07
    dt_pattern_2 = re.compile('(\d{4}-[01]\d-[0123]\d)')
    dt_fmt_2 = '%Y-%m-%d'
    for dt_str in re.findall(dt_pattern_2, text):
        # logging.debug('DT STR IS "{}"'.format(dt_str))
        try:
            logging.debug('Trying to match [{}] to '
                          '[{}] ..'.format(dt_fmt_2, dt_str))
            dt = datetime.strptime(dt_str, dt_fmt_2)
        except ValueError:
            pass
        else:
            if date_is_probable(dt):
                logging.debug('Extracted datetime from text: '
                              '[{}]'.format(dt))
                results.append(dt)
                matches += 1

    # Matches '(C) 2014' and similar.
    dt_pattern_3 = re.compile('\( ?[Cc] ?\) ?([12]\d{3})')
    dt_fmt_3 = '%Y'
    for dt_str in re.findall(dt_pattern_3, text):
        try:
            logging.debug('Trying to match [{:12s}] to '
                          '[{}] ..'.format((dt_fmt_3, dt_str)))
            dt = datetime.strptime(dt_str, dt_fmt_3)
        except ValueError:
            pass
        else:
            if date_is_probable(dt):
                logging.debug('Extracted datetime from text: '
                              '[{}]'.format(dt))
                results += dt
                matches += 1

    logging.info('Regex matcher found [{:^3}] matches.'.format(matches))
    logging.info('Regex matcher returning list of [{:^3}] '
                 'results.'.format(len(results)))
    return results


def match_special_case(text):
    """
    PART #0   -- the very special case
    Very special case that is almost guaranteed to be correct.
    That is my personal favorite naming scheme: 1992-12-24_121314
    :param text: text to extract date/time from
    :return: datetime if found otherwise None
    """
    # TODO: Allow customizing personal preferences, using a configuration
    #       file or similar..
    try:
        logging.debug('Matching against very special case '
                      '"YYYY-mm-dd_HHMMSS" ..')
        dt = datetime.strptime(text[:17], '%Y-%m-%d_%H%M%S')
    except ValueError:
        logging.debug('Failed matching very special case.')
    else:
        if date_is_probable(dt):
            logging.info('Matched very special case: [{}]'.format(dt))
            return dt
    return None


def match_android_messenger_filename(text):
    """
    Test if text (file name) matches that of Android messenger.
    Example: received_10151287690965808.jpeg
    :param text: text (file name) to test
    :return: list of datetime-objects if matches were found, otherwise None
    """

    # TODO: Fix this! It currently does not seem to work, at all.
    # Some hints are in the Android Messenger source code:
    # .. /Messaging.git/src/com/android/messaging/datamodel/action/DownloadMmsAction.java

    # $ date --date='@1453473286' --rfc-3339=seconds
    #   2016-01-22 15:34:46+01:00
    # $ 1453473286723

    results = []
    logging.debug('Matching against Android Messenger file name ..')

    dt_pattern = re.compile('.*(received_)(\d{17})(\.jpe?g)?')
    for _, dt_str, _ in re.findall(dt_pattern, text):
        try:
            # dt_float = float(dt_str[:13])
            # dt_str = dt_str[:13]
            # dt = datetime.fromtimestamp(float(dt_str))
            # ms = int(dt_str[:13])
            ms = int(dt_str[13:])
            dt = datetime.utcfromtimestamp(ms // 1000).replace(microsecond=ms % 1000 * 1000)
            # dt = datetime.fromtimestamp(float(dt_str) / 1000.0)
        except ValueError as e:
            logging.warning('Unable to extract datetime from '
                            '[{}] - {}'.format(dt_str, e.message))
        else:
            if date_is_probable(dt):
                logging.debug('Extracted datetime from Android messenger file '
                              'name text: [{}]'.format(dt.isoformat()))
                results.append(dt)

    return results


def match_unix_timestamp(text):
    """
    Match text against UNIX "seconds since epoch" timestamp.
    :param text: text to extract date/time from
    :return: datetime if found otherwise None
    """
    if text is None:
        logging.error('Got NULL argument!')
        return None
    elif text.strip() is None:
        logging.error('Got empty string!')
        return None

    text = misc.extract_digits(text)
    if text is None or len(text) == 0:
        logging.warn('Text contains no digits from which to extract epoch.')
        return None

    # Example Android phone file name: 1461786010455.jpg
    # Remove last 3 digits to be able to convert using GNU date:
    # $ date --date ='@1461786010'
    #   ons 27 apr 2016 21:40:10 CEST
    if len(text) == 13:
        text = text[:10]

    text_float = float(text)
    try:
        logging.debug('Try matching seconds since 1970-01-01 00:00:00 UTC.')
        dt = datetime.fromtimestamp(text_float)
    except ValueError:
        logging.debug('Failed matching seconds since epoch.')
    else:
        if date_is_probable(dt):
            logging.info('Extracted UNIX timestamp from "{}": '
                         '[{}]'.format(text, dt))
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
    if text is None:
        logging.error('Got NULL argument!')
        return None
    elif text.strip() is None:
        logging.error('Got empty string!')
        return None

    bruteforce_str.matches = bruteforce_str.matches_total = 0

    # Internal function checks result, adds to list of results if OK.
    def validate_result(dt):
        if date_is_probable(dt):
            logging.debug('Extracted datetime from text: [{}]'.format(dt))
            results.append(dt)
            bruteforce_str.matches += 1
            bruteforce_str.matches_total += 1

    # (premature) optimization ..
    if len(text) < 4:
        logging.debug('Unable to continue, text is too short.')
        return None

    number_digits_in_text = sum(c.isdigit() for c in text)
    if number_digits_in_text < 4:
        logging.debug('Unable to continue -- text contains '
                      'insufficient number of digits.')
        return None

    # Strip all letters from the left.
    text = text.lstrip(string.letters)
    text = text.lstrip('_-[](){}')

    # Create empty list to hold all results.
    results = []

    # ----------------------------------------------------------------
    # PART #1   -- pattern matching
    # This part does basic pattern matching on a slightly modified version
    # of the text. A bunch of preset patterns are tried, all of which does
    # the matching from the beginning of the text.

    # Replace common separator characters.
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

    # Strip whitespace from both ends.
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
            logging.debug('Trying to match [{:17s}]to '
                          '[{}] ..'.format(fmt, text_strip))
            dt = datetime.strptime(text_strip, fmt)
        except ValueError:
            pass
        else:
            validate_result(dt)

    if results:
        logging.info('First matcher found  [{:>3}] matches after [{:>4}] '
                     'tries.'.format(bruteforce_str.matches, tries))
        return results
    else:
        logging.debug(
            'Gave up first approach after [{:>4}] tries.'.format(tries))

    # ----------------------------------------------------------------
    # PART #2   -- pattern matching on just the digits
    # This part works about the same as the previous one, except it
    # discards everything except digits in the text.

    # Try another approach, start by extracting all digits.
    logging.debug('Trying second approach.')
    digits_only = misc.extract_digits(text)

    if len(digits_only) < 4:
        logging.debug('Failed second approach -- not enough digits.')
        return results

    year_first = True
    digits = digits_only
    # Remove one number at a time from the front until first four digits
    # represent a probable year.
    while not _year_is_probable(int(digits[:4])) and year_first:
        logging.debug('"{}" is not a probable year. '
                      'Removing a digit.'.format(digits[:4]))
        digits = digits[1:]
        if len(digits) < 4:
            logging.debug('Failed second approach -- no leading year.')
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
        logging.debug('Assuming format with year first.')
        for chars, fmt in common_formats2:
            digits_strip = digits[:chars]
            tries += 1
            tries_total += 1
            try:
                logging.debug('Trying to match [{:12s}] to '
                              '[{}] ..'.format(fmt, digits_strip))
                dt = datetime.strptime(digits_strip, fmt)
            except ValueError:
                pass
            else:
                validate_result(dt)

        logging.debug('Gave up after %d tries ..'.format(tries))

    # TODO: Examine this here below hacky conditional. Why is it there?
    if True:
        digits = digits_only
        while len(str(digits)) > 2:
            logging.debug('Assuming format other than year first.')
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
                    logging.debug('Trying to match [{:12s}] to '
                                  '[{}] ..'.format(fmt, digits_strip))
                    dt = datetime.strptime(digits_strip, fmt)
                except ValueError:
                    pass
                else:
                    validate_result(dt)

            logging.debug('Gave up after {} tries ..'.format(tries))
            logging.debug('Removing leading number '
                          '({} --> {})'.format(digits, digits[1:]))
            digits = digits[1:]

    logging.info('Second matcher found [{:>3}] matches after [{:>4}] '
                 'tries.'.format(bruteforce_str.matches_total, tries_total))
    return results


def fuzzy_datetime(text, prefix):
    # Currently not used at all!
    # TODO: Finish this method ..
    dt = None
    try:
        try:
            dt = dateutil.parser.parse(text)
            print('Sharp {} -> {}'.format(text, dt))
        except ValueError:
            dt = dateutil.parser.parse(text, fuzzy=True)
            print('Fuzzy {} -> {}'.format(text, dt))
    except Exception as e:
        print('Try as I may, I cannot parse {} ({})'.format(text, e))

    return dt


def search_gmail(text, prefix):
    """
    Searches gmail content for date/time-information.
    :param text: the text to extract information from
    :param prefix: prefix this to the resulting dictionary keys
    :return: a list of dictionaries containing datetime-objects.
    """
    # Currently not used at all!
    # TODO: Is this necessary/sane/good practice? (NO!)
    if type(text) is list:
        logging.warn('Converting list to string ..')
        text = ' '.join(text)

    if not text.lower().find('gmail'):
        logging.debug('Text does not contains "gmail", might not be a Gmail?')
        return

    # Create empty dictionary to hold all results.
    results = {}

    # Expected date formats:         Fri, Jan 8, 2016 at 3:50 PM
    #                                1/11/2016
    SEP = '[, ]'
    REGEX_GMAIL_LONG = re.compile('(\w{3,8})' + SEP + '(\w{3,10})\ (\d{1,2})'
                                  + SEP + '([12]\d{3})' + '(\ at\ )?' +
                                  '(\d{1,2}:\d{1,2}\ [AP]M)')
    REGEX_GMAIL_SHORT = re.compile('\d{1,2}\/\d{2}\/[12]\d{3}')


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
    if text is None:
        logging.warning('Got NULL argument')
        return None
    if prefix == 'NULL':
        logging.warning('Result prefix not specified! Using default "NULL"')

    # TODO: Improve handlng of generalized "text" from any source.
    #       (currently plain text and pdf documents)
    if type(text) == list:
        text = ' '.join(text)

    # Create empty dictionary for storing the final result.
    results_all = {}
    # Create empty lists for storing any found date/time-objects.
    # Each search-method gets its own list for storing its own results.
    results_brute = []
    results_regex = []

    matches = 0
    text_split = text.split('\n')
    logging.debug('Try getting datetime from text split by newlines')
    for t in text_split:
        dt = bruteforce_str(t)
        if dt and dt is not None:
            # logging.info('Added result from contents: {0}'.format(dt))
            results_brute.append(dt)
            matches += 1

    if matches == 0:
        logging.debug('No matches. Trying with text split by whitespace')
        text_split = text.split()
        for t in text_split:
            dt = bruteforce_str(t)
            if dt and dt is not None:
                # logging.info('Added result from contents: {0}'.format(dt))
                results_brute.append(dt)
                matches += 1

    # TODO: Fix this here below. Looks completely broken.
    regex_match = 0
    dt_regex = regex_search_str(text)
    if dt_regex and dt_regex is not None:
        # logging.info('Added result from contents regex search: '
        #              '{0}'.format(dt_regex))
        results_regex.append(dt_regex)
        regex_match += 1

    # Collect all individual results and return.
    results_all['{}_contents_regex'.format(prefix)] = results_regex
    results_all['{}_contents_brute'.format(prefix)] = results_brute
    return results_all
