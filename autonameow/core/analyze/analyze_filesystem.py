# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

import datetime
import logging
import os

from datetime import datetime

from core.analyze.analyze_abstract import AbstractAnalyzer


class FilesystemAnalyzer(AbstractAnalyzer):
    """
    FilesystemAnalyzer -- Gets information about files from the filesystem.

    Currently has only the very most basic functionality; retrieves timestamps
    for file creation, modification and access using "os.path.getXtime".

    The other implemented superclass methods always returns None for now.

    Extending this to properly implement all superclass methods will most
    likely require separate solutions for each operating system and/or
    filesystem. Needs more research into any available wrappers, etc.
    And as I personally don't use filesystem metadata for my own metadata
    storage, all further exploration will have to wait.

    References:
    http://en.wikipedia.org/wiki/Extended_file_attributes
    http://www.freedesktop.org/wiki/CommonExtendedAttributes
    http://timgolden.me.uk/python/win32_how_do_i/get-document-summary-info.html
    """

    def __init__(self, file_object):
        super(FilesystemAnalyzer, self).__init__(file_object)
        self.applies_to_mime = None

    def run(self):
        pass

    def get_datetime(self):
        result = []

        fs_timestamps = self._get_datetime_from_filesystem()
        if fs_timestamps:
            result += fs_timestamps

        return result

    def get_title(self):
        # Currently not relevant to this analyzer.
        # Future support for reading filesystem metadata could implement this.
        return None

    def get_author(self):
        # Currently not relevant to this analyzer.
        # Future support for reading filesystem metadata could implement this.
        return None

    def get_tags(self):
        # Currently not relevant to this analyzer.
        # Future support for reading filesystem metadata could implement this.
        return None

    def _get_datetime_from_filesystem(self):
        """
        Extracts date and time information "from the file system", I.E.
        access-, modification- and creation-timestamps.
        NOTE: This is all very platform-specific, I think.
        NOTE #2: Microseconds are simply zeroed out.
        :return: list of dictionaries on the form:
                 [ { 'value': datetime.datetime(2016, 6, 5, 16, ..),
                     'source' : "Create date",
                     'weight'  : 1
                   }, .. ]
        """
        filename = self.file_object.path
        results = []

        logging.debug('Fetching file system timestamps ..')
        try:
            mtime = os.path.getmtime(filename)
            ctime = os.path.getctime(filename)
            atime = os.path.getatime(filename)
        except OSError as e:
            logging.critical('Failed extracting date/time-information '
                             'from file system -- OSError: {}'.format(e))
        else:
            def dt_fts(t):
                return datetime.fromtimestamp(t).replace(microsecond=0)

            results.append({'value': dt_fts(mtime),
                            'source': 'modified',
                            'weight': 1})
            results.append({'value': dt_fts(ctime),
                            'source': 'created',
                            'weight': 1})
            results.append({'value': dt_fts(atime),
                            'source': 'accessed',
                            'weight': 0.25})

        logging.debug('Got [{:^3}] timestamps from the '
                      'filesystem.'.format(len(results)))
        return results

