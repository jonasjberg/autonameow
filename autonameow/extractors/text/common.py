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
import unicodedata

from core import (
    types,
    util
)
from core.util import textutils
from extractors import (
    BaseExtractor,
    ExtractorError,
    ExtractedData
)


log = logging.getLogger(__name__)


class AbstractTextExtractor(BaseExtractor):
    def __init__(self):
        super(AbstractTextExtractor, self).__init__()

    def execute(self, source, **kwargs):
        try:
            self.log.debug('{!s} starting initial extraction'.format(self))
            text = self._get_text(source)
        except ExtractorError as e:
            self.log.warning('{!s}: {!s}'.format(self, e))
            raise
        except NotImplementedError as e:
            self.log.debug('[WARNING] Called unimplemented code in {!s}: '
                           '{!s}'.format(self, e))
            raise ExtractorError

        assert(isinstance(text, str))

        self.log.debug('{!s} returning all extracted data'.format(self))
        return {'full': ExtractedData(wrapper=types.AW_STRING)(text)}

    def _get_text(self, source):
        raise NotImplementedError('Must be implemented by inheriting classes.')

    @classmethod
    def check_dependencies(cls):
        raise NotImplementedError('Must be implemented by inheriting classes.')


def decode_raw(raw_text):
    try:
        text = types.AW_STRING(raw_text)
    except types.AWTypeError:
        try:
            text = textutils.autodetect_decode(raw_text)
        except ValueError:
            log.warning('Unable to decode raw text')
            return ''

    if text:
        text = util.remove_nonbreaking_spaces(text)
        return text


def normalize_unicode(text):
    return unicodedata.normalize('NFKC', text)
