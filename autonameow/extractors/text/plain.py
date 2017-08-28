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

import logging

try:
    import chardet
except (ImportError, ModuleNotFoundError):
    chardet = None

from core.exceptions import ExtractorError
from core.util import textutils
from extractors.text import AbstractTextExtractor


log = logging.getLogger(__name__)

DEFAULT_ENCODING = 'utf8'


class PlainTextExtractor(AbstractTextExtractor):
    handles_mime_types = ['text/plain']
    meowuri_root = 'contents.textual.raw_text'

    def __init__(self, source):
        super(PlainTextExtractor, self).__init__(source)

    def _get_raw_text(self):
        self.log.debug('Extracting raw text from plain text file ..')
        result = read_entire_text_file(self.source)
        return self._decode_raw(result)

    @classmethod
    def check_dependencies(cls):
        return True


def read_entire_text_file(file_path):
    contents = None
    try:
        with open(file_path, 'r', encoding=DEFAULT_ENCODING) as fh:
            contents = fh.readlines()
    except FileNotFoundError as e:
        raise ExtractorError(e)
    except UnicodeDecodeError as e:
        log.debug(str(e))
        if chardet is not None:
            log.debug(
                'Unable to decode text with {} encoding. Reading as bytes and '
                'trying to auto-detect the encoding.'.format(DEFAULT_ENCODING)
            )
            contents = _read_entire_text_file_autodetect_encoding(file_path)

    if contents:
        log.debug('Successfully read {} lines from "{!s}"'.format(len(contents),
                                                                  file_path))
        contents = '\n'.join(contents)
        contents = textutils.remove_nonbreaking_spaces(contents)
        assert(isinstance(contents, str))
        return contents
    else:
        log.debug('Read NOTHING from file "{!s}"'.format(file_path))
        return ''


def _read_entire_text_file_autodetect_encoding(file_path):
    detected_encoding = chardet.detect(open(file_path, 'rb').read())
    if detected_encoding and 'encoding' in detected_encoding:
        log.debug('')
        try:
            with open(file_path, 'r',
                      encoding=detected_encoding['encoding']) as fh:
                return fh.readlines()
        except (UnicodeDecodeError, ValueError) as e:
            raise ExtractorError(
                'Unable to read with auto-detected encoding; {!s}'.format(e)
            )
