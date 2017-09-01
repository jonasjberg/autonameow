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

from core import (
    exceptions,
    types,
    util
)
from core.util import textutils
from extractors import BaseExtractor


class AbstractTextExtractor(BaseExtractor):
    def __init__(self, source):
        super(AbstractTextExtractor, self).__init__(source)

        self._raw_text = None

    def execute(self, **kwargs):
        if not self._raw_text:
            try:
                self.log.debug('{!s} starting initial extraction'.format(self))
                self._perform_initial_extraction()
            except exceptions.ExtractorError as e:
                self.log.error('{!s}: extraction FAILED; {!s}'.format(self, e))
                raise
            except NotImplementedError as e:
                self.log.debug('[WARNING] Called unimplemented code in {!s}: '
                               '{!s}'.format(self, e))
                raise exceptions.ExtractorError

        if 'field' in kwargs:
            self.log.debug('{!s} ignoring field (returning all fields):'
                           ' "{!s}"'.format(self, kwargs.get('field')))

        self.log.debug('{!s} returning all extracted data'.format(self))
        return self._raw_text

    def _decode_raw(self, text):
        try:
            text = types.AW_STRING(text)
        except exceptions.AWTypeError:
            try:
                text = textutils.autodetect_decode(text)
            except ValueError:
                self.log.warning('{!s}: Unable to decode text'.format(self))
                return ''

        text = util.remove_nonbreaking_spaces(text)
        return text

    def _perform_initial_extraction(self):
        raw_text = self._get_raw_text()
        self._raw_text = self._decode_raw(raw_text)

    def _get_raw_text(self):
        raise NotImplementedError('Must be implemented by inheriting classes.')

    @classmethod
    def check_dependencies(cls):
        raise NotImplementedError('Must be implemented by inheriting classes.')


from .ocr import ImageOCRTextExtractor
from .epub import EpubTextExtractor
from .plain import PlainTextExtractor
from .pdf import PdfTextExtractor

