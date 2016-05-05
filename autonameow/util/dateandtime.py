#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import string
from datetime import datetime

import re


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


def regex_search_str(text, prefix):
    results = {}
    matches = 0

    # Expected date format:         2016:04:07 18:47:30
    dt_pattern_1 = re.compile('(\d{4}[: -][01]\d[: -][0123]\d[: -][012]\d[: -][012345]\d[: -][012345]\d)')
    dt_fmt_1 = '%Y%m%d%H%M%S'
    for dt_str in dt_pattern_1.findall(text):
    # for dt_str in re.findall(dt_pattern_1, text):
        logging.info('dt_str : {}'.format(dt_str))
        for remove in [':', '-', ',', '.', '_']:
            dt_str.replace(remove, '')
        try:
            logging.debug('Trying to match [%-12.12s] to [%s] ..'
                          % (dt_fmt_1, dt_str))
            dt = datetime.strptime(dt_str, dt_fmt_1)
        except ValueError:
            pass
        else:
            if date_is_probable(dt) and dt not in results:
                logging.debug('Extracted datetime from text: '
                              '[%s]' % dt)
                new_key = '{0}_{1:02d}'.format(prefix, matches)
                results[new_key] = dt
                matches += 1

        return results

    # Expected date format:         2016:04:07
    dt_pattern_2 = re.compile('(\d{4}-[01]\d-[0123]\d)')
    dt_fmt_2 = '%Y-%m-%d'
    for dt_str in re.findall(dt_pattern_2, text):
        logging.info('DT STR IS \"{}\"'.format(dt_str))
        try:
            logging.debug('Trying to match [%-12.12s] to [%s] ..'
                          % (dt_fmt_2, dt_str))
            dt = datetime.strptime(dt_str, dt_fmt_2)
        except ValueError:
            pass
        else:
            if date_is_probable(dt) and dt not in results:
                logging.debug('Extracted datetime from text: '
                              '[%s]' % dt)
                new_key = '{0}_{1:02d}'.format(prefix, matches)
                results[new_key] = dt
                matches += 1

    # Matches '(C) 2014' and similar.
    dt_pattern_3 = re.compile('\( ?[Cc] ?\) ?([12]\d{3})')
    dt_fmt_3 = '%Y'
    for dt_str in re.findall(dt_pattern_3, text):
        logging.info('DT STR IS \"{}\"'.format(dt_str))
        try:
            logging.debug('Trying to match [%-12.12s] to [%s] ..'
                          % (dt_fmt_3, dt_str))
            dt = datetime.strptime(dt_str, dt_fmt_3)
        except ValueError:
            pass
        else:
            if date_is_probable(dt) and dt not in results:
                logging.debug('Extracted datetime from text: '
                              '[%s]' % dt)
                new_key = '{0}_{1:02d}'.format(prefix, matches)
                results[new_key] = dt
                matches += 1

    return results

def bruteforce_str(text, prefix):
    """
    Extracts date/time-information from a text string.
    Does a brute force extraction, trying a lot of different combinations.
    The result is a list of dicts, with keys named "prefix_000",
    "prefix_001", etc, after the order in which they were found.
    Some bad date/time-information is bound to be picked up.
    :text: the text to extract information from
    :prefix: prefix this to the resulting dictionary keys
    :return: a list of dictionaries containing datetime-objects.
    """
    if text is None:
        logging.error('Got NULL argument!')
        return None

    # (premature) optimization ..
    if len(text) < 4:
        logging.debug('Unable to continue, text is too short.')
        return None

    digits_in_text = sum(c.isdigit() for c in text)
    if digits_in_text < 4:
        logging.debug('Unable to continue, text contains '
                      'insufficient number of digits.')
        return None

    # Strip all letters from the left.
    text = text.lstrip(string.letters)

    # Create empty dictionary to hold results.
    results = {}

    # Very special case that is almost guaranteed to be correct.
    # This is my current personal favorite naming scheme.
    # TODO: Allow customizing personal preferences, using a configuration
    #       file or similar..
    try:
        logging.debug('Trying very special case ..')
        dt = datetime.strptime(text[:17], '%Y-%m-%d_%H%M%S')
    except ValueError:
        logging.debug('Very special case failed.')
        pass
    else:
        if date_is_probable(dt):
            logging.debug(
                'Extracted (special case) datetime from text: '
                '[%s]' % dt)
            new_key = '{0}_{1:02d}'.format(prefix, 0)
            results[new_key] = dt
            return results

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
            if date_is_probable(dt) and dt not in results:
                logging.debug('Extracted datetime from text: [%s]' % dt)
                new_key = '{0}_{1:02d}'.format(prefix, matches)
                results[new_key] = dt
                matches += 1
                matches_total += 1

    if results:
        logging.debug('Found %d matches after %d tries.'
                      % (len(results), tries))
        return results
    else:
        logging.debug('Gave up first approach after %d tries ..' % tries)

    # Try another approach, start by extracting all digits.
    logging.debug('Trying second approach.')
    digits_only = ''
    for c in text:
        if c.isdigit():
            digits_only += c

    if len(digits_only) < 4:
        logging.debug('Second approach failed, not enough digits.')
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
            logging.debug('Second approach failed. No leading year.')
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
                if date_is_probable(dt) and dt not in results:
                    logging.debug('Extracted datetime from text: '
                                  '[%s]' % dt)
                    new_key = '{0}_{1:02d}'.format(prefix, matches)
                    results[new_key] = dt
                    matches += 1
                    matches_total += 1

        logging.debug('Gave up after %d tries ..' % tries)

    else:
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
                    if date_is_probable(dt) and dt not in results:
                        logging.debug('Extracted datetime from text: '
                                      '[%s]' % dt)
                        new_key = '{0}_{1:02d}'.format(prefix, matches)
                        results[new_key] = dt
                        matches += 1
                        matches_total += 1

            logging.debug('Gave up after %d tries ..' % tries)
            logging.debug('Removing leading number ..')
            logging.debug('Removing leading number ({} --> {})'.format(digits, digits[:1]))
            digits = digits[1:]

    logging.info('Found [{:^3}] matches from [{:^4}] tries.'.format(matches_total, tries_total))
    return results
