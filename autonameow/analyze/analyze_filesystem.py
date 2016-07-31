# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

import datetime
import logging
import os
from datetime import datetime

from analyze.analyze_abstract import AbstractAnalyzer


class FilesystemAnalyzer(AbstractAnalyzer):

    def __init__(self, file_object, filters):
        super(FilesystemAnalyzer, self).__init__(file_object, filters)

    def get_datetime(self):
        result = []

        fs_timestamps = self._get_datetime_from_filesystem()
        if fs_timestamps:
            result += fs_timestamps

        return result

    def get_title(self):
        # TODO: Implement.
        pass

    def get_author(self):
        # TODO: Implement.
        pass

    def get_tags(self):
        # TODO: Implement.
        pass

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

        logging.debug('Got [{:^3}] timestamps from '
                      'filesystem.'.format(len(results)))
        return results

