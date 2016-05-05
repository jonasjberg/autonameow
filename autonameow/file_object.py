import datetime
import logging
import magic
import os


class FileObject(object):
    def __init__(self, path):
        self.newName = None
        self.datetime_list = []
        self.description = None

        if path is None:
            logging.critical('Got NULL path!')
            pass

        # Remains untouched, for use when renaming file
        self.originalfilename = os.path.basename(path)
        logging.debug('fileObject original file name: {}'.format(
            self.originalfilename))

        # Get full absolute path
        self.path = os.path.abspath(path)
        logging.debug('fileObject path: {}'.format(self.path))

        # Extract parts of the file name.
        self.basename = os.path.basename(self.path)
        self.basename_no_ext = os.path.splitext(self.basename)[0]
        self.extension = self.get_file_extension()

        # Figure out basic file type
        self.type = self.get_type_from_magic()

    def get_type_from_magic(self):
        """
        Determine file type by reading "magic" header bytes.
        Similar to the 'find' command in *NIX environments.
        :return:
        """
        ms = magic.open(magic.MAGIC_NONE)
        ms.load()
        magic_type = ms.file(self.path)
        ms.close()
        # return type
        # logging.debug('Found magic file type: [{}]'.format(type.split()[0]))
        return magic_type.split()[0]

    def add_datetime(self, dt):
        """
        Add date/time-information dict to the list of all date/time-objects
        found for this FileObject.
        :param dt: date/time-information dict ('KEY' 'datetime') to add
        :return:
        """
        if dt is None:
            logging.warning('Got null argument')
            return
        elif type(dt) is not dict:
            logging.warning('Got non-dict argument')
            pass

        if dt not in self.datetime_list:
            # logging.debug('Adding datetime [%s] to list' % str(type(dt)))
            self.datetime_list.append(dt)

    def get_datetime_list(self):
        """
        Get the list of datetime-objects found for this FileObject.
        :return: date/time-information as a list of dicts
        """
        return self.datetime_list

    def get_oldest_datetime(self):
        """
        Get the oldest datetime-object in datetime_list.
        :return:
        """
        oldest_yet = datetime.datetime.max
        for dt_dict in self.datetime_list:
            for dt_key, dt_value in dt_dict.iteritems():
                try:
                    # For now, lets get the first filename datetime only.
                    if dt_key.startswith('FilenameDateTime_'):
                        if dt_key != 'FilenameDateTime_00':
                            continue
                    if dt_value < oldest_yet:
                        oldest_yet = dt_value
                except Exception:
                    pass

        return oldest_yet

    def get_file_extension(self, make_lowercase=True):
        """
        Get file extension.
        :param make_lowercase: make the extension lowercase, defaults to True
        :return: the file extension
        """
        base, ext = os.path.splitext(self.path)

        if ext.lower() in ['.z', '.gz', '.bz2']:
            ext = os.path.splitext(base)[1] + ext

        ext = ext.lstrip('.')

        if make_lowercase:
            ext = ext.lower()

        if ext and ext.strip():
            return ext
        else:
            return None

    # def get_file_name_noext(self):
    #     """
    #     Get the file name without extension.
    #     :return: file name without file extension
    #     """
    #     base = os.path.basename(self.path)
    #     name_noext = os.path.splitext(base)[0]
    #
    #     if name_noext and name_noext.strip():
    #         return name_noext
    #     else:
    #         return None
