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

import logging as log

from core.exceptions import ExtractorError
from extractors import BaseExtractor


class AbstractTextExtractor(BaseExtractor):
    def __init__(self, source):
        super(AbstractTextExtractor, self).__init__(source)

        self._raw_text = None

    def query(self, field=None):
        # TODO: [TD0057] Will text extractors be queried for anything but text?
        if not self._raw_text:
            try:
                log.debug('{!s} received initial query ..'.format(self))
                self._perform_initial_extraction()
            except ExtractorError as e:
                log.error('{!s} query FAILED; Error: {!s}'.format(self, e))
                return False
            except NotImplementedError as e:
                log.debug('[WARNING] Called unimplemented code in {!s}: '
                          '{!s}'.format(self, e))
                return False

        if not field:
            # TODO: [TD0057] Fix this. Look over the entire 'query' method.
            log.debug('{!s} responding to query for all fields'.format(self))
            return self._raw_text
        else:
            log.debug('{!s} ignoring query for field (returning all fields):'
                      ' "{!s}"'.format(self, field))
            return self._raw_text

    def _perform_initial_extraction(self):
        self._raw_text = self._get_raw_text()

    def _get_raw_text(self):
        raise NotImplementedError('Must be implemented by inheriting classes.')


class PlainTextExtractor(AbstractTextExtractor):
    handles_mime_types = ['text/plain']
    data_query_string = 'contents.textual.raw_text'

    def __init__(self, source):
        super(PlainTextExtractor, self).__init__(source)

    def _get_raw_text(self):
        log.debug('Extracting raw text from plain text file ..')
        result = read_entire_text_file(self.source)
        return result


def read_entire_text_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf8') as fh:
            contents = fh.read().split('\n')
    except FileNotFoundError as e:
        log.debug('{!s}'.format(e))
        raise ExtractorError(e)

    if contents:
        log.debug('Successfully read {} lines from "{!s}"'.format(len(contents),
                                                                  file_path))
        # TODO: [TD0044][TD0004] Cleanup/normalize and ensure text encoding.
        return contents
    else:
        log.debug('Read NOTHING from file "{!s}"'.format(file_path))
        return ''
