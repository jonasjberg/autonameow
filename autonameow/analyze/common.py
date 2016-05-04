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

        # SEPARATOR_CHARS = ['/', '-', ',', '.', ':', '_']
        # for char in SEPARATOR_CHARS:
        #     name = name.replace(char, ' ')


        # Datetime format      Chars    Example
        # -----------------    -----    -------------------
        # %Y-%m-%d %H:%M:%S    19       1992-12-24 12:13:14
        # %Y:%m:%d %H:%M:%S    19       1992:12:24 12:13:14
        # %Y-%m-%d_%H-%M-%S    19       1992-12-24_12-13-14
        # %Y-%m-%d_%H%M%S      17       1992-12-24_121314
        # %Y%m%d_%H%M%S        15       19921224_121314
        # %Y%m%d%H%M%S         14       19921224121314
        # %Y-%m-%d             10       1992-12-24
        # %Y%m%d               8        19921224
        common_formats = [[19, '%Y-%m-%d %H:%M:%S'],
                          [19, '%Y:%m:%d %H:%M:%S'],
                          [19, '%Y-%m-%d_%H-%M-%S'],
                          [17, '%Y-%m-%d_%H%M%S'],
                          [15, '%Y%m%d_%H%M%S'],
                          [14, '%Y%m%d%H%M%S'],
                          [10, '%Y-%m-%d'],
                          [8, '%Y%m%d']]
        tries = 0
        for chars_fmt in common_formats:
            chars, fmt = chars_fmt
            name_strip = name[:chars]
            try:
                dt = datetime.strptime(name_strip, fmt)
                # return datetime.date(result.tm_year, result.tm_mon,
                #                      result.tm_mday)
            except ValueError:
                tries += 1
                pass
            else:
                logging.debug('Extracted datetime from filename: [%s]' % dt)
                return dt

        logging.debug('Giving up after %3.3d tries ..' % tries)
        return None
