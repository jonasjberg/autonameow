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
from extractors.text import AbstractTextExtractor


class PlainTextExtractor(AbstractTextExtractor):
    handles_mime_types = ['text/plain']
    data_query_string = 'contents.textual.raw_text'

    def __init__(self, source):
        super(PlainTextExtractor, self).__init__(source)

    def _get_raw_text(self):
        log.debug('Extracting raw text from plain text file ..')
        result = read_entire_text_file(self.source)
        return result

    @classmethod
    def check_dependencies(cls):
        return True


def read_entire_text_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf8') as fh:
            contents = fh.readlines()
    except (FileNotFoundError, UnicodeDecodeError) as e:
        log.debug('{!s}'.format(e))
        raise ExtractorError(e)

    if contents:
        log.debug('Successfully read {} lines from "{!s}"'.format(len(contents),
                                                                  file_path))
        # TODO: [TD0044][TD0004] Cleanup/normalize and ensure text encoding.
        contents = '\n'.join(contents)
        assert(isinstance(contents, str))
        return contents
    else:
        log.debug('Read NOTHING from file "{!s}"'.format(file_path))
        return ''
