# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

import datetime
import logging
import magic
import os

# Match output from magic.ms
magic_type_lookup = {'MP4':   ['video/mp4'],
                     'OGG':   ['video/ogg'],
                     'JPG':   ['image/jpeg'],
                     'PDF':   ['application/pdf'],
                     'TXT':   ['text/plain'],
                     'PNG':   ['image/png'],
                     'EMPTY': ['inode/x-empty']}


class MetadataBlock(object):
    def __init__(self, title, author, date, publisher, edition, tags):
        self.title = title
        self.author = author
        self.date = date
        self.publisher = publisher
        self.edition = edition
        self.tags = tags


class FileObject(object):
    def __init__(self, path):
        self.newName = None
        self.datetime_list = []
        self.metadata = MetadataBlock(None, None, None, None, None, None)

        if path is None:
            logging.critical('Got NULL path!')
            pass

        # Remains untouched, for use when renaming file
        self.originalfilename = os.path.basename(path)
        logging.debug('fileObject original file '
                      'name: {}'.format(self.originalfilename))

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
        ms = magic.open(magic.MAGIC_MIME_TYPE)
        ms.load()
        mt = ms.file(self.path)
        ms.close()

        if not mt:
            return 'EMPTY'

        # http://stackoverflow.com/a/16588375
        def find_key(input_dict, value):
            return next((k for k, v in input_dict.items() if v == value), None)

        try:
            return find_key(magic_type_lookup, mt.split()[:2])
        except KeyError:
            logging.warn('Unable to determine file type. Magic: {}'.format(mt))
            return 'EMPTY'

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
            return

        # Arbitrary maximum amount of date/time entries to hold.
        LIST_MAX_LEN = 200
        if len(self.datetime_list) >= LIST_MAX_LEN:
            logging.info('Date/time list hit limit ({})'.format(LIST_MAX_LEN))
            return

        # TODO: Should duplicate entries be allowed?
        # if dt not in self.datetime_list:
        if True:
            logging.debug('Adding datetime [%s] to list' % str(type(dt)))
            self.datetime_list.append(dt)

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
