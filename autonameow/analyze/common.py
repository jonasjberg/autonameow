import datetime
import logging
import os
import time


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

        results['Modified'] = datetime.datetime.fromtimestamp(mtime) if mtime else None
        results['Created'] = datetime.datetime.fromtimestamp(ctime) if ctime else None
        results['Accessed'] = datetime.datetime.fromtimestamp(atime) if atime else None

        logging.debug('Fetched timestamps: %s' % results)
        return results

    def get_datetime_from_name(self):
        name = self.file_object.basename_no_ext

        to_remove = ['IMG_', 'TODO']
        for s in to_remove:
            name = name.replace(s, '')

        # SEPARATOR_CHARS = ['/', '-', ',', '.', ':', '_']
        # for char in SEPARATOR_CHARS:
        #     name = name.replace(char, ' ')


        #
        # %Y-%m-%d %H:%M:%S     1992-12-24 12:13:14
        # %Y:%m:%d %H:%M:%S     1992:12:24 12:13:14
        # %Y-%m-%d_%H-%M-%S     1992-12-24_12-13-14
        # %Y-%m-%d_%H%M%S       1992-12-24_121314
        # %Y%m%d_%H%M%S         19921224_121314
        # %Y%m%d%H%M%S          19921224121314
        # %Y-%m-%d              1992-12-24

        common_formats = ['%Y-%m-%d %H:%M:%S', '%Y:%m:%d %H:%M:%S',
                          '%Y-%m-%d_%H-%M-%S', '%Y-%m-%d_%H%M%S',
                          '%Y%m%d_%H%M%S', '%Y%m%d%H%M%S', '%Y-%m-%d']
        tries = 0
        for fmt in common_formats:
            try:
                result = time.strptime(name, fmt)
                # return datetime.date(result.tm_year, result.tm_mon,
                #                      result.tm_mday)
            except ValueError:
                tries += 1
                pass
            else:
                logging.debug('Extracted datetime from filename: [%s]' % result)
                return result

        logging.debug('Giving up after %d tries ..' % tries)
        return None
