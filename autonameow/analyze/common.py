import datetime
import logging
import os
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
        results = {}

        # TODO: Add more patterns to remove before trying to extract time/date.
        to_remove = ['IMG_', 'TODO']
        for s in to_remove:
            name = name.replace(s, '')

        # Replace common separator characters.
        SEPARATOR_CHARS = ['/', '-', ',', '.', ':', '_']
        for char in SEPARATOR_CHARS:
            name = name.replace(char, ' ')

        # Date/time format     Chars    Example
        # -----------------    -----    -------------------
        # %Y %m %d %H %M %S    19       1992 12 24 12 13 14
        # %Y %m %d %H%M%S      17       1992 12 24 121314
        # %Y%m%d %H%M%S        15       19921224 121314
        # %Y%m%d%H%M%S         14       19921224121314
        # %Y %m %d             10       1992 12 24
        # %Y%m%d               8        19921224
        # %Y%m                 7        1992 12
        # %Y%m                 6        199212
        common_formats = [[19, '%Y %m %d %H %M %S'],
                          [17, '%Y %m %d %H%M%S'],
                          [15, '%Y%m%d %H%M%S'],
                          [14, '%Y%m%d%H%M%S'],
                          [10, '%Y %m %d'],
                          [8, '%Y%m%d'],
                          [7, '%Y %m'],
                          [6, '%Y%m']]
        tries = 0
        for chars, fmt in common_formats:
            name_strip = name[:chars]
            try:
                logging.debug('Trying to match [%-17.17s] to [%s] ..' % (fmt, name_strip))
                dt = datetime.strptime(name_strip, fmt)
                # return datetime.date(result.tm_year, result.tm_mon,
                #                      result.tm_mday)
            except ValueError:
                tries += 1
                pass
            else:
                logging.debug('Extracted datetime from filename: [%s]' % dt)
                if dt not in results:
                    results['FilenameDateTime'] = dt
                break

        logging.debug('Gave up after %d tries ..' % tries)

        if results:
            return results

        # Try another approach, start by extracting all digits.
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
        tries = 0
        for chars, fmt in common_formats2:
            digits_strip = digits[:chars]
            try:
                logging.debug('Trying to match [%-12.12s] to [%s] ..' % (fmt, digits_strip))
                dt = datetime.strptime(digits_strip, fmt)
            except ValueError:
                tries += 1
                pass
            else:
                logging.debug('Extracted datetime from filename: [%s]' % dt)
                if dt not in results:
                    results['FilenameDateTime'] = dt
                break

        logging.debug('Gave up after %d tries ..' % tries)

        return results
