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

        # TODO: Add more patterns to remove before trying to extract time/date.
        for s in ['IMG_', 'TODO..']:
            name = name.replace(s, '')

        # Strip all letters from the left, until the first non-letter.
        name = name.lstrip(string.letters)

        # Replace common separator characters.
        for char in ['/', '-', ',', '.', ':', '_']:
            name = name.replace(char, ' ')

        # Replace unknown "wildcard" parts, like '2016-02-xx', '2016-xx-xx', ..
        WILDCARDS = [[' xx ', ' 01 '],
                    [' xx', ' 01'],
                    ['xx', '01']]
        for u_old, u_new in WILDCARDS:
            name = name.replace(u_old, u_new)

        # Strip whitespace
        name = name.strip()

        # Create empty dictionary to hold results.
        results = {}

        #               Chars   Date/time format        Example
        #                  --   -----------------       -------------------
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
                          [8, '%y %m %d'],              # 92 12 24
                          [11, '%b %d %Y'],             # Dec 24 1992
                          [9, '%b %d %y'],              # Dec 24 92
                          [20, '%B %d %y'],             # December 24 92
                          [20, '%B %d %Y']]             # December 24 1992
        tries = match = 0
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
                logging.debug('Extracted datetime from filename: [%s]' % dt)
                if dt not in results:
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

        # Date/time format     Chars    Example
        # -----------------    -----    --------------
        # %Y%m%d%H%M%S         14       19921224121314
        # %Y%m%d%H%M           12       199212241213
        # %Y%m%d%H             10       1992122412
        # %Y%m%d               8        19921224
        # %Y%m                 6        199212
        # %Y                   4        1992
        common_formats2 = [[14, '%Y%m%d%H%M%S'],
                          [12, '%Y%m%d%H%M'],
                          [10, '%Y%m%d%H'],
                          [8, '%Y%m%d'],
                          [6, '%Y%m'],
                          [4, '%Y']]
        tries = match = 0
        for chars, fmt in common_formats2:
            digits_strip = digits[:chars]
            tries += 1
            try:
                logging.debug('Trying to match [%-12.12s] to [%s] ..' % (fmt, digits_strip))
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
