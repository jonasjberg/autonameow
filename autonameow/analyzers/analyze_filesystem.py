# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2017 Jonas Sjöberg
#   Personal site:   http://www.jonasjberg.com
#   GitHub:          https://github.com/jonasjberg
#   University mail: js224eh[a]student.lnu.se
#
#   This file is part of autonameow.
#
#   autonameow is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation.
#
#   autonameow is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with autonameow.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import logging
import os
from datetime import datetime

from analyzers.analyze_abstract import AbstractAnalyzer


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
    # @Overrides attribute in AbstractAnalyzer
    run_queue_priority = 1

    def __init__(self, file_object):
        super(FilesystemAnalyzer, self).__init__(file_object)
        self.applies_to_mime = 'MIME_ALL'

    # @Overrides method in AbstractAnalyzer
    def run(self):
        pass

    # @Overrides method in AbstractAnalyzer
    def get_datetime(self):
        result = []

        fs_timestamps = self._get_datetime_from_filesystem()
        if fs_timestamps:
            result += fs_timestamps

        return result

    # @Overrides method in AbstractAnalyzer
    def get_title(self):
        # Currently not relevant to this analyzer.
        # Future support for reading filesystem metadata could implement this.
        raise NotImplementedError('Get "title" from FilesystemAnalyzer')

    # @Overrides method in AbstractAnalyzer
    def get_author(self):
        # Currently not relevant to this analyzer.
        # Future support for reading filesystem metadata could implement this.
        raise NotImplementedError('Get "author" from FilesystemAnalyzer')

    # @Overrides method in AbstractAnalyzer
    def get_tags(self):
        # Currently not relevant to this analyzer.
        # Future support for reading filesystem metadata could implement this.
        raise NotImplementedError('Get "tags" from FilesystemAnalyzer')

    # @Overrides method in AbstractAnalyzer
    def get_publisher(self):
        raise NotImplementedError('Get "publisher" from FilesystemAnalyzer')

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

        logging.debug('Got {} timestamps from the filesystem.'.format(
            len(results)))
        return results
