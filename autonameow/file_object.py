# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

import datetime
import logging
import magic
import os

# Match output from magic.ms
from util import diskutils

magic_type_lookup = {'mp4':   ['video/mp4'],
                     'ogg':   ['video/ogg'],
                     'jpg':   ['image/jpeg'],
                     'pdf':   ['application/pdf'],
                     'txt':   ['text/plain'],
                     'png':   ['image/png'],
                     'empty': ['inode/x-empty']}


class FileObject(object):
    def __init__(self, path):
        self.datetime_list = []

        if path is None:
            logging.critical('Got NULL path!')
            pass

        # Get full absolute path
        self.path = os.path.abspath(path)
        logging.debug('fileObject path: {}'.format(self.path))

        # Remains untouched, for use when renaming file
        self.originalfilename = os.path.basename(path)
        logging.debug('fileObject original file '
                      'name: {}'.format(self.originalfilename))

        # Extract parts of the file name.
        self.basename_no_ext = diskutils.file_base(self.path)
        self.extension = diskutils.file_suffix(self.path)

        # Figure out basic file type
        self.type = diskutils.filetype_magic(self.path)


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

    def _get_file_extension(self, make_lowercase=True):
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
