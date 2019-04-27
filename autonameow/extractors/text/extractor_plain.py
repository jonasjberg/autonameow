# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2019 Jonas Sjöberg <autonameow@jonasjberg.com>
#   Source repository: https://github.com/jonasjberg/autonameow
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

from core import constants as C
from extractors import ExtractorError
from extractors.text.base import BaseTextExtractor
from util import encoding as enc


log = logging.getLogger(__name__)


class PlainTextExtractor(BaseTextExtractor):
    def _extract_text(self, fileobject):
        return read_entire_text_file(fileobject.abspath)

    @classmethod
    def dependencies_satisfied(cls):
        return True

    @classmethod
    def can_handle(cls, fileobject):
        if fileobject.mime_type != 'text/plain':
            return False

        if fileobject.basename_suffix in C.MARKDOWN_BASENAME_SUFFIXES:
            # Prefer the 'MarkdownTextExtractor' to handle this file.
            from extractors.text.extractor_markdown import MarkdownTextExtractor
            if MarkdownTextExtractor.can_handle(fileobject):
                return False

        return True


def read_entire_text_file(filepath):
    contents = None
    try:
        with open(filepath, 'r', encoding=C.DEFAULT_ENCODING) as fh:
            contents = fh.readlines()
    except FileNotFoundError as e:
        raise ExtractorError(e)
    except UnicodeDecodeError as e:
        log.debug(str(e))
        log.debug(
            'Failed with text encoding %s. Attempting encoding detection.',
            C.DEFAULT_ENCODING
        )
        contents = _read_entire_text_file_autodetect_encoding(filepath)

    if not contents:
        log.debug('Read NOTHING from file "%s"', filepath)
        return ''

    log.debug('Read %s lines from file "%s"', len(contents), filepath)
    text = ''.join(contents)
    return text


def _read_entire_text_file_autodetect_encoding(filepath):
    detected_encoding = enc.detect_encoding(filepath)
    if detected_encoding:
        log.debug('Detected text encoding %s', detected_encoding)
        try:
            with open(filepath, 'r', encoding=detected_encoding) as fh:
                return fh.readlines()
        except (UnicodeDecodeError, ValueError) as e:
            raise ExtractorError(
                'Detected text encoding %s :: {!s}'.format(detected_encoding, e)
            )
    return None
