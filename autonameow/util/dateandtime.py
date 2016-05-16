#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import string
from datetime import datetime

import re

import dateutil

from util import misc


def date_is_probable(date):
    """
    Check if date is "probable", meaning greater than 1900 and
    not in the future, I.E. greater than the year of todays date.
    That is, simply:    1900 < date < today
    :param date: date to check
    :return: True if the date is probable, otherwise False
    """
    logging.debug('date_is_probable got {} : {}'.format(type(date), date))
    if type(date) is not datetime:
        probable_lower_limit = int(1900)
        probable_upper_limit = int(datetime.today().strftime('%Y'))

        date = int(date)
        # Check if number of digits is less than three,
        # I.E. we got something like '86' (1986) or maybe '08' (2008).
        if len(str(date)) < 3:
            # Test if adding 2000 would still be within the limit.
            if date + 2000 <= probable_upper_limit:
                date += 2000
            # Otherwise just assume this will fix it ..
            else:
                date += 1900

        if date > probable_upper_limit:
            logging.debug('Skipping future date [{}]'.format(date))
            return False
        elif date < probable_lower_limit:
            logging.debug('Skipping non-probable (<{}) date [{}]'.format(
                probable_lower_limit, date))
            return False
        else:
            return True

    else:
        probable_lower_limit = datetime.strptime('1900', '%Y')
        probable_upper_limit = datetime.today()
        if date.year > probable_upper_limit.year:
            logging.debug('Skipping future date [{}]'.format(date))
            return False
        elif date.year < probable_lower_limit.year:
            logging.debug('Skipping non-probable (<{}) date [{}]'.format(
                probable_lower_limit, date))
            return False
        else:
            return True

def search_standard_formats(text, prefix):
    """
    Matches against standard formats.
    :param text: the text to extract information from
    :param prefix: prefix this to the resulting dictionary keys
    :return: a list of dictionaries containing datetime-objects.
    """
    pass

def regex_search_str(text, prefix):
    """
    Extracts date/time-information from a text string using regex searches.

    This is meant to be more "directed" than the bruteforce method.
    Return values (should) work the same as "bruteforce_str".

    :param text: the text to extract information from
    :param prefix: prefix this to the resulting dictionary keys
    :return: a list of dictionaries containing datetime-objects.
    """

    # Create empty dictionary to hold all results.
    results = {}

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
            # logging.debug('len(m_time) < 6 .. m_time_ms is \"{}\"'.format(m_time_ms))
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
            logging.debug('Trying to match [{:13}] to [{}] ..'.format(dt_fmt_1, dt_str))
            dt = datetime.strptime(dt_str, dt_fmt_1)
        except ValueError:
            pass
        else:
            if date_is_probable(dt):
                logging.debug('Extracted datetime from text: '
                              '[%s]' % dt)
                new_key = '{0}_{1:02d}'.format(prefix, matches)
                results[new_key] = dt
                matches += 1

    # Expected date format:         2016:04:07
    dt_pattern_2 = re.compile('(\d{4}-[01]\d-[0123]\d)')
    dt_fmt_2 = '%Y-%m-%d'
    for dt_str in re.findall(dt_pattern_2, text):
        #logging.debug('DT STR IS \"{}\"'.format(dt_str))
        try:
            logging.debug('Trying to match [%-12.12s] to [%s] ..'
                          % (dt_fmt_2, dt_str))
            dt = datetime.strptime(dt_str, dt_fmt_2)
        except ValueError:
            pass
        else:
            if date_is_probable(dt):
                logging.debug('Extracted datetime from text: '
                              '[%s]' % dt)
                new_key = '{0}_{1:02d}'.format(prefix, matches)
                results[new_key] = dt
                matches += 1

    # Matches '(C) 2014' and similar.
    dt_pattern_3 = re.compile('\( ?[Cc] ?\) ?([12]\d{3})')
    dt_fmt_3 = '%Y'
    for dt_str in re.findall(dt_pattern_3, text):
        try:
            logging.debug('Trying to match [%-12.12s] to [%s] ..'
                          % (dt_fmt_3, dt_str))
            dt = datetime.strptime(dt_str, dt_fmt_3)
        except ValueError:
            pass
        else:
            if date_is_probable(dt):
                logging.debug('Extracted datetime from text: '
                              '[%s]' % dt)
                new_key = '{0}_{1:02d}'.format(prefix, matches)
                results[new_key] = dt
                matches += 1


    logging.info('Regex matcher found [{:^3}] matches.'.format(matches))
    logging.info('Regex matcher returning dict with [{:^3}] results.'.format(len(results)))
    return results

def bruteforce_str(text, prefix):
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
    :param prefix: prefix this to the resulting dictionary keys
    :return: a list of dictionaries containing datetime-objects.
    """
    if text is None:
        logging.error('Got NULL argument!')
        return None

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

    # Create empty dictionary to hold all results.
    results = {}

    # ----------------------------------------------------------------
    # PART #-1   -- "unix" timestamp
    # If the text is all digits after above modifications, then check
    # if text represent seconds since 1970-01-01 00:00:00 UTC.
    #
    if text.isdigit():
        # print('text {} is all digits'.format(text))
        text_float = float(text)
        try:
            logging.debug('Try matching seconds since 1970-01-01 00:00:00 UTC.')
            dt = datetime.fromtimestamp(text_float)
        except ValueError:
            logging.debug('Failed matching seconds since epoch.')
        else:
            if date_is_probable(dt):
                logging.info('Extracted (seconds since epoch) datetime from {}: [{}]'.format(prefix, dt))
                new_key = '{0}_{1:02d}'.format(prefix, 0)
                results[new_key] = dt
                return results

    # ----------------------------------------------------------------
    # PART #0   -- the very special case
    # Very special case that is almost guaranteed to be correct.
    # That is my personal favorite naming scheme: 1992-12-24_121314
    # TODO: Allow customizing personal preferences, using a configuration
    #       file or similar..
    try:
        logging.debug('Trying very special case ..')
        dt = datetime.strptime(text[:17], '%Y-%m-%d_%H%M%S')
    except ValueError:
        logging.debug('Failed matching very special case.')
        pass
    else:
        if date_is_probable(dt):
            logging.info('Extracted (special case) datetime from {}: [{}]'.format(prefix, dt))
            new_key = '{0}_{1:02d}'.format(prefix, 0)
            results[new_key] = dt
            return results

    # ----------------------------------------------------------------
    # PART #1   -- pattern matching
    # This part does basic pattern matching on a slightly modified version
    # of the text. A bunch of preset patterns are tried, all of which does
    # the matching from the beginning of the text.

    # Replace common separator characters.
    for char in ['/', '-', ',', '.', ':', '_']:
        text = text.replace(char, '')

    # Replace "wildcard" parts, like '2016-02-xx', '2016-xx-xx', ..
    WILDCARDS = [['xx', '01'],
                 ['XX', '01'],
                 ['0x', '01'],
                 ['0X', '01'],
                 ['20xx', '2000'],
                 ['19XX', '1901']]
    for u_old, u_new in WILDCARDS:
        text = text.replace(u_old, u_new)

    # Strip whitespace from both ends.
    text = text.strip()
    text = text.replace(' ', '')

    #               Chars   Date/time format        Example
    #                  --   -------------------     -------------------
    common_formats = [[14, '%Y%m%d%H%M%S'],         # 19921224121314
                      [8, '%Y%m%d'],                # 19921224
                      [6, '%Y%m'],                  # 199212
                      [4, '%Y'],                    # 1992
                      [10, '%m%d%Y'],               # 12241992
                      [8, '%m%d%y'],                # 122492
                      [8, '%d%m%y'],                # 241292
                      [8, '%y%m%d'],                # 921224
                      [11, '%b%d%Y'],               # Dec241992
                      [11, '%d%b%Y'],               # 24Dec1992
                      [9, '%b%d%y'],                # Dec2492
                      [9, '%d%b%y'],                # 24Dec92
                      [20, '%B%d%y'],               # December2492
                      [20, '%B%d%Y']]               # December241992
    tries = matches = matches_total = tries_total = 0
    for chars, fmt in common_formats:
        if len(text) < chars:
            continue

        text_strip = text[:chars]
        tries += 1
        tries_total += 1
        try:
            logging.debug('Trying to match [%-17.17s] to [%s] ..'
                          % (fmt, text_strip))
            dt = datetime.strptime(text_strip, fmt)
        except ValueError:
            pass
        else:
            if date_is_probable(dt):
                logging.debug('Extracted datetime from text: [%s]' % dt)
                new_key = '{0}_{1:02d}'.format(prefix, matches)
                results[new_key] = dt
                matches += 1
                matches_total += 1

    if results:
        logging.info('First matcher found  [{:>3}] matches after [{:>4}] tries.'.format(len(results), tries))
        return results
    else:
        logging.debug('Gave up first approach after [{:>4}] tries.'.format(tries))

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
    while not date_is_probable(int(digits[:4])):
        logging.debug('\"{}\" is not a probable year. '
                      'Removing a digit.'.format(digits[:4]))
        digits = digits[1:]
        if len(digits) < 4:
            logging.debug('Failed second approach -- no leading year.')
            year_first = False

    if year_first:
        #                Chars   Date/time format   Example
        #                   --   ----------------   --------------
        common_formats2 = [[14, '%Y%m%d%H%M%S'],    # 19921224121314
                           [12, '%Y%m%d%H%M'],      # 199212241213
                           [10, '%Y%m%d%H'],        # 1992122412
                           [8, '%Y%m%d'],           # 19921224
                           [6, '%Y%m'],             # 199212
                           [4, '%Y']]               # 1992
        tries = 0
        logging.debug('Assuming format with year first.')
        for chars, fmt in common_formats2:
            digits_strip = digits[:chars]
            tries += 1
            tries_total += 1
            try:
                logging.debug('Trying to match [%-12.12s] to [%s] ..'
                              % (fmt, digits_strip))
                dt = datetime.strptime(digits_strip, fmt)
            except ValueError:
                pass
            else:
                if date_is_probable(dt):
                    logging.debug('Extracted datetime from text: '
                                  '[%s]' % dt)
                    new_key = '{0}_{1:02d}'.format(prefix, matches)
                    results[new_key] = dt
                    matches += 1
                    matches_total += 1

        logging.debug('Gave up after %d tries ..' % tries)

    if True:
        digits = digits_only
        while len(str(digits)) > 2:
            logging.debug('Assuming format other than year first.')
            #                Chars   Date/time format   Example
            #                   --   ----------------   --------------
            common_formats3 = [[8, '%d%m%Y'],           # 24121992
                               [6, '%d%m%y'],           # 241292
                               [8, '%m%d%Y'],           # 12241992
                               [6, '%m%d%y'],           # 122492
                               [6, '%d%m%y'],           # 241292
                               [6, '%y%m%d'],           # 921224
                               [6, '%Y%m'],             # 199212
                               [4, '%Y'],               # 1992
                               [2, '%y']]               # 92
            tries = 0
            for chars, fmt in common_formats3:
                digits_strip = digits[:chars]
                tries += 1
                tries_total += 1
                try:
                    logging.debug('Trying to match [%-12.12s] to [%s] ..'
                                  % (fmt, digits_strip))
                    dt = datetime.strptime(digits_strip, fmt)
                except ValueError:
                    pass
                else:
                    if date_is_probable(dt):
                        logging.debug('Extracted datetime from text: '
                                      '[%s]' % dt)
                        new_key = '{0}_{1:02d}'.format(prefix, matches)
                        results[new_key] = dt
                        matches += 1
                        matches_total += 1

            logging.debug('Gave up after %d tries ..' % tries)
            logging.debug('Removing leading number ..')
            logging.debug('Removing leading number ({} --> {})'.format(digits, digits[1:]))
            digits = digits[1:]

    logging.info('Second matcher found [{:>3}] matches after [{:>4}] tries.'.format(matches_total, tries_total))
    return results

def fuzzy_datetime(text, prefix):
    # TODO: Finish this method ..
    dt = None
    try:
        try:
            dt = dateutil.parser.parse(text)
            print('Sharp %r -> %s' % (text, dt))
        except ValueError:
            dt = dateutil.parser.parse(text, fuzzy=True)
            print('Fuzzy %r -> %s' % (text, dt))
    except Exception as e:
        print('Try as I may, I cannot parse %r (%s)' % (text, e))

    return dt

def search_gmail(text, prefix):
    """
    Searches gmail content for date/time-information.
    :param text: the text to extract information from
    :param prefix: prefix this to the resulting dictionary keys
    :return: a list of dictionaries containing datetime-objects.
    """
    # TODO: Is this necessary/sane/good practice? (NO!)
    if type(text) is list:
        logging.warn('Converting list to string ..')
        text = ' '.join(text)

    # Create empty dictionary to hold all results.
    results = {}

    # Expected date formats:         Fri, Jan 8, 2016 at 3:50 PM
    #                                1/11/2016
    SEP = '[, ]'
    REGEX_GMAIL_LONG = re.compile('(\w{3,8})' + SEP + '(\w{3,10})\ (\d{1,2})' + SEP + '([12]\d{3})' + '(\ at\ )?' + '(\d{1,2}:\d{1,2}\ [AP]M)')
    # REGEX_GMAIL_LONG = re.compile('\w{3,5},\ \w{3,5}\ \d{1,2},\ [12]\d{3}\ at\ \d{1,2}:\d{1,2}\ [AP]M')
    REGEX_GMAIL_SHORT = re.compile('\d{1,2}\/\d{2}\/[12]\d{3}')

    # DATE_SEP = "[:\-._ \/]?"
    # TIME_SEP = "[T:\-. _]?"
    # DATE_REGEX = '[12]\d{3}' + DATE_SEP + '[01]\d' + DATE_SEP + '[0123]\d'
    # TIME_REGEX = TIME_SEP + '[012]\d' + TIME_SEP + '[012345]\d(.[012345]\d)?'
    # DATETIME_REGEX = '(' + DATE_REGEX + '(' + TIME_REGEX + ')?)'
    #
    # dt_pattern_1 = re.compile(DATETIME_REGEX)
    #
    # matches = 0
    # for m_date, m_time, m_time_ms in re.findall(dt_pattern_1, text):
    #     # Extract digits, skip if entries contain no digits.
    #     m_date = misc.extract_digits(m_date)
    #     m_time = misc.extract_digits(m_time)
    #     m_time_ms = misc.extract_digits(m_time_ms)
    #
    #     if m_date is None or m_time is None:
    #         continue
    #
    #     # Check if m_date is actually m_date *AND* m_date.
    #     if len(m_date) > 8 and m_date.endswith(m_time):
    #         # logging.debug('m_date contains m_date *AND* m_time')
    #         m_date = m_date.replace(m_time, '')
    #
    #     if len(m_time) < 6:
    #         # logging.debug('len(m_time) < 6 .. m_time_ms is \"{}\"'.format(m_time_ms))
    #         pass
    #
    #     # Skip matches with unexpected number of digits.
    #     if len(m_date) != 8 or len(m_time) != 6:
    #         continue
    #
    #     logging.debug('m_date {:10} : {}'.format(type(m_date), m_date))
    #     logging.debug('m_time {:10} : {}'.format(type(m_time), m_time))
    #     logging.debug('m_time_ms {:10} : {}'.format(type(m_time_ms), m_time_ms))
    #     logging.debug('---')
    #
    #     dt_fmt_1 = '%Y%m%d_%H%M%S'
    #     dt_str = (m_date + '_' + m_time).strip()
    #     try:
    #         logging.debug('Trying to match [{:13}] to [{}] ..'.format(dt_fmt_1, dt_str))
    #         dt = datetime.strptime(dt_str, dt_fmt_1)
    #     except ValueError:
    #         pass
    #     else:
    #         if date_is_probable(dt):
    #             logging.debug('Extracted datetime from text: '
    #                           '[%s]' % dt)
    #             new_key = '{0}_{1:02d}'.format(prefix, matches)
    #             results[new_key] = dt
    #             matches += 1
    #
    # logging.info('Regex matcher found [{:^3}] matches.'.format(matches))
    # logging.info('Regex matcher returning dict with [{:^3}] results.'.format(len(results)))
    # return results
