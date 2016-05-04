import datetime
import logging
import os
import string
from datetime import datetime


# Analysis relevant to all files, regardless of file mime type.
# Examines:
#   * file names
#   * file system metadata (modified, created, ..)


class AnalyzerBase(object):
    def __init__(self, file_object):
        self.file_object = file_object

    def run(self):
        """
        Run the analysis.
        """

        fs_timestamps = self.get_datetime_from_filesystem()
        if fs_timestamps:
            self.file_object.add_datetime(fs_timestamps)

        fn_timestamps = self.get_datetime_from_name()
        if fn_timestamps:
            self.file_object.add_datetime(fn_timestamps)

    def get_datetime(self):
        # TODO: Get datetime from information common to all file types;
        #       file name, files in the same directory, name of directory, etc..
        pass

    def get_datetime_from_filesystem(self):
        """
        Extracts date and time information "from the file system", I.E.
        access-, modification- and creation-timestamps.
        NOTE: This is all very platform-specific.
        :return: Touple of datetime objects representing date and time.
        """
        filename = self.file_object.path
        results = {}

        logging.debug('Fetching file system timestamps ..')
        try:
            mtime = os.path.getmtime(filename)
            ctime = os.path.getctime(filename)
            atime = os.path.getatime(filename)
        except OSError:
            logging.critical('Exception OSError')

        results['Modified'] = datetime.fromtimestamp(mtime) if mtime else None
        results['Created'] = datetime.fromtimestamp(ctime) if ctime else None
        results['Accessed'] = datetime.fromtimestamp(atime) if atime else None

        logging.debug('Fetched timestamps: %s' % results)
        return results

    def get_datetime_from_name(self):
        name = self.file_object.basename_no_ext

        # (premature) optimization ..
        if len(name) < 4:
            logging.debug('Unable to continue, name is too short.')
            return None

        digits_in_name = sum(c.isdigit() for c in name)
        if digits_in_name < 4:
            logging.debug('Unable to continue, name contains '
                          'insufficient number of digits.')
            return None

        # Strip all letters from the left.
        name = name.lstrip(string.letters)

        # Create empty dictionary to hold results.
        results = {}

        # Very special case that is almost guaranteed to be correct.
        # This is my current personal favorite naming scheme.
        # TODO: Allow customizing personal preferences, using a configuration
        #       file or similar..
        try:
            logging.debug('Trying very special case ..')
            dt = datetime.strptime(name[:17], '%Y-%m-%d_%H%M%S')
        except ValueError:
            logging.debug('Very special case failed.')
            pass
        else:
            if self.year_is_probable(dt):
                logging.debug(
                    'Extracted (special case) datetime from filename: '
                    '[%s]' % dt)
                new_key = 'FilenameDateTime_{0:02d}'.format(0)
                results[new_key] = dt
                return results

        # Replace common separator characters.
        for char in ['/', '-', ',', '.', ':', '_']:
            name = name.replace(char, ' ')

        # Replace "wildcard" parts, like '2016-02-xx', '2016-xx-xx', ..
        WILDCARDS = [[' xx ', ' 01 '], [' XX ', ' 01 '], [' xx', ' 01'],
                     [' XX', ' 01'], ['xx ', '01 '], ['XX ', '01 '],
                     ['xx', '01'], ['XX', '01']]
        for u_old, u_new in WILDCARDS:
            name = name.replace(u_old, u_new)

        # Strip whitespace from both ends.
        name = name.strip()

        #               Chars   Date/time format        Example
        #                  --   -------------------     -------------------
        common_formats = [[19, '%Y %m %d %H %M %S'],    # 1992 12 24 12 13 14
                          [17, '%Y %m %d %H%M%S'],      # 1992 12 24 121314
                          [15, '%Y%m%d %H%M%S'],        # 19921224 121314
                          [14, '%Y%m%d%H%M%S'],         # 19921224121314
                          [10, '%Y %m %d'],             # 1992 12 24
                          [8, '%Y%m%d'],                # 19921224
                          [7, '%Y %m'],                 # 1992 12
                          [6, '%Y%m'],                  # 199212
                          [4, '%Y'],                    # 1992
                          [10, '%m %d %Y'],             # 12 24 1992
                          [8, '%m %d %y'],              # 12 24 92
                          [8, '%d %m %y'],              # 24 12 92
                          [8, '%y %m %d'],              # 92 12 24
                          [11, '%b %d %Y'],             # Dec 24 1992
                          [11, '%d %b %Y'],             # 24 Dec 1992
                          [9, '%b %d %y'],              # Dec 24 92
                          [9, '%d %b %y'],              # 24 Dec 92
                          [20, '%B %d %y'],             # December 24 92
                          [20, '%B %d %Y']]             # December 24 1992
        tries = match = 0
        probable_lower_limit = datetime.strptime('1900', '%Y')
        for chars, fmt in common_formats:
            if len(name) < chars:
                continue
            name_strip = name[:chars]

            tries += 1
            try:
                logging.debug('Trying to match [%-17.17s] to [%s] ..'
                              % (fmt, name_strip))
                dt = datetime.strptime(name_strip, fmt)
            except ValueError:
                pass
            else:
                if not self.year_is_probable(dt):
                    continue

                if dt not in results:
                    logging.debug('Extracted datetime from filename: [%s]' % dt)
                    new_key = 'FilenameDateTime_{0:02d}'.format(match)
                    results[new_key] = dt
                    match += 1

        if results:
            logging.debug('Found %d matches after %d tries.'
                          % (len(results), tries))
            return results
        else:
            logging.debug('Gave up first approach after %d tries ..' % tries)

        # Try another approach, start by extracting all digits.
        logging.debug('Trying second approach.')
        digits = ''
        for c in name:
            if c.isdigit():
                digits += c

        if len(digits) < 4:
            logging.debug('Second approach failed, not enough digits.')
            return results

        # Remove numbers until first four digits represent a "probable" year,
        # defined as to be greater than 1900 and not in the future.
        today_year = datetime.today().strftime('%Y')
        year_maybe = int(digits[:4])
        while year_maybe < 1900 or year_maybe > int(today_year):
            logging.debug('\"{}\" is not a probable year. '
                          'Removing a digit.'.format(year_maybe))
            digits = digits[1:]
            year_maybe = int(digits[:4])
            if len(digits) < 4:
                logging.debug('Second approach failed. No leading year.')
                return None

        #                Chars   Date/time format   Example
        #                   --   ----------------   --------------
        common_formats2 = [[14, '%Y%m%d%H%M%S'],    # 19921224121314
                           [12, '%Y%m%d%H%M'],      # 199212241213
                           [10, '%Y%m%d%H'],        # 1992122412
                           [8, '%Y%m%d'],           # 19921224
                           [6, '%Y%m'],             # 199212
                           [4, '%Y']]               # 1992
        tries = match = 0
        for chars, fmt in common_formats2:
            digits_strip = digits[:chars]
            tries += 1
            try:
                logging.debug('Trying to match [%-12.12s] to [%s] ..' % (
                fmt, digits_strip))
                dt = datetime.strptime(digits_strip, fmt)
            except ValueError:
                pass
            else:
                if dt not in results:
                    logging.debug('Extracted datetime from filename: [%s]' % dt)
                    new_key = 'FilenameDateTime_{0:02d}'.format(match)
                    results[new_key] = dt
                    match += 1

        logging.debug('Gave up after %d tries ..' % tries)

        return results

    def year_is_probable(self, date):
        """
        Check if year is "probable", where probable is greater than 1900 and
        not in the future, I.E. greater than the year of todays date.
        :param date: date to check
        :return: True if the year is probable, otherwise False
        """
        if type(date) is not datetime:
            date = datetime.strptime(date, '%Y')

        probable_lower_limit = datetime.strptime('1900', '%Y')
        probable_upper_limit = datetime.today()

        if date.year > probable_upper_limit.year:
            logging.debug('Skipping future date [{}]'.format(date))
            return False
        elif date.year < probable_lower_limit.year:
            logging.debug('Skipping non-probable date [{}]'.format(date))
            return False
        else:
            return True
