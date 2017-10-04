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
except ImportError:
    chardet = None

from core import util
from core.util import (
    sanity,
    textutils
)
from extractors import ExtractorError
from extractors.text.common import AbstractTextExtractor


log = logging.getLogger(__name__)


DEFAULT_ENCODING = 'utf8'


class PlainTextExtractor(AbstractTextExtractor):
    HANDLES_MIME_TYPES = ['text/plain']

    def __init__(self):
        super(PlainTextExtractor, self).__init__()

    def _get_text(self, source):
        self.log.debug('Extracting raw text from plain text file ..')
        result = read_entire_text_file(source)
        if not result:
            return ''

        sanity.check_internal_string(result)
        text = result
        text = textutils.normalize_unicode(text)
        text = textutils.remove_nonbreaking_spaces(text)
        if text:
            return text
        else:
            return ''

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
        text = ''.join(contents)
        sanity.check_internal_string(text)
        return text
    else:
        log.debug('Read NOTHING from file "{!s}"'.format(file_path))
        return ''


def _read_entire_text_file_autodetect_encoding(file_path):
    _encoding = autodetect_encoding(file_path)
    if _encoding:
        log.debug('Auto-detected encoding: {!s}'.format(_encoding))
        try:
            with open(file_path, 'r', encoding=_encoding) as fh:
                return fh.readlines()
        except (UnicodeDecodeError, ValueError) as e:
            raise ExtractorError(
                'Unable to use auto-detected encoding; {!s}'.format(e)
            )


def autodetect_encoding(file_path):
    try:
        with open(file_path, 'rb') as fh:
            detected_encoding = chardet.detect(fh.read())
    except (OSError, TypeError) as e:
        log.error('Error while auto-detecting encoding; {!s}'.format(e))
        return None
    else:
        return detected_encoding.get('encoding', None)
