import logging
import magic
import os


class FileObject(object):
    def __init__(self, path):
        self.newName = None
        self.datetime_list = []
        self.description = None

        if path is not None:
            # Remains untouched, for use when renaming file
            self.originalfilename = os.path.basename(path)
            logging.debug('fileObject original file name: {}'.format(
                self.originalfilename))

            # Get full absolute path
            self.path = os.path.abspath(path)
            logging.debug('fileObject path: {}'.format(self.path))

        # Figure out basic file type
        self.type = self.read_magic_header_bytes()

        if not self.type:
            self.type = None

    def get_path(self):
        return self.path

    def get_type(self):
        return self.type

    def read_magic_header_bytes(self):
        """
        Determine file type by reading "magic" header bytes.
        Similar to the 'find' command in *NIX environments.
        :return:
        """
        ms = magic.open(magic.MAGIC_NONE)
        ms.load()
        type = ms.file(self.path)
        ms.close()
        # return type
        return type.split()[0]

    def assembleNewName(self):
        # TODO: Construct a new file name.
        #       Maybe a separate class should handle it?
        pass

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

        if not dt in self.datetime_list:
            # logging.debug('Adding datetime-object [%s] to list' % str(type(dt)))
            self.datetime_list.append(dt)

    def get_datetime_list(self):
        """
        Get the list of datetime-objects found for this FileObject.
        :return: date/time-information as a list of dicts
        """
        return self.datetime_list
