# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg
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

from core import constants as C
from extractors import ExtractorError
from extractors.text.common import AbstractTextExtractor
from util import sanity


log = logging.getLogger(__name__)


class PlainTextExtractor(AbstractTextExtractor):
    HANDLES_MIME_TYPES = ['text/plain']
    IS_SLOW = False

    def extract_text(self, fileobject):
        return read_entire_text_file(fileobject.abspath)

    @classmethod
    def check_dependencies(cls):
        return True


def read_entire_text_file(file_path):
    contents = None
    try:
        with open(file_path, 'r', encoding=C.DEFAULT_ENCODING) as fh:
            contents = fh.readlines()
    except FileNotFoundError as e:
        raise ExtractorError(e)
    except UnicodeDecodeError as e:
        log.debug(str(e))
        if chardet is not None:
            log.debug(
                'Unable to decode text with {} encoding. Reading as bytes and '
                'trying to auto-detect the encoding.'.format(C.DEFAULT_ENCODING)
            )
            contents = _read_entire_text_file_autodetect_encoding(file_path)

    if not contents:
        log.debug('Read NOTHING from file "{!s}"'.format(file_path))
        return ''

    log.debug('Read {} bytes from "{!s}"'.format(len(contents), file_path))
    text = ''.join(contents)
    sanity.check_internal_string(text)
    return text


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
    return None


def autodetect_encoding(file_path):
    assert chardet, 'Missing required module "chardet"'
    try:
        with open(file_path, 'rb') as fh:
            detected_encoding = chardet.detect(fh.read())
    except (OSError, TypeError) as e:
        log.error('Error while auto-detecting encoding; {!s}'.format(e))
        return None
    else:
        return detected_encoding.get('encoding', None)
