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

from core import (
    persistence,
    types,
    util
)
from core.model import genericfields as gf
from core.util import (
    sanity,
    textutils
)
from extractors import (
    BaseExtractor,
    ExtractorError
)


log = logging.getLogger(__name__)


class AbstractTextExtractor(BaseExtractor):
    FIELD_LOOKUP = {
        'full': {
            'coercer': types.AW_STRING,
            'multiple': False,
            'mapped_fields': None,
            'generic_field': gf.GenericText
        }
    }

    def __init__(self):
        super(AbstractTextExtractor, self).__init__()

        self.cache = None
        # NOTE(jonas): Call 'self.init_cache()' in subclass init to use caching.

    def extract(self, fileobject, **kwargs):
        text = self._get_text(fileobject)
        sanity.check_internal_string(text)

        self.log.debug('{!s} returning all extracted data'.format(self))
        metainfo = dict(self.FIELD_LOOKUP.get('full', {}))
        metainfo.update({'value': text})
        return metainfo

    def _get_text(self, fileobject):
        # Read cached text
        if self.cache:
            _cached = self.cache.get(fileobject)
            if _cached is not None:
                self.log.info('Using cached text for: {!r}'.format(fileobject))
                return _cached

        try:
            self.log.debug('{!s} starting initial extraction'.format(self))
            text = self.extract_text(fileobject)
        except ExtractorError as e:
            self.log.warning('{!s}: {!s}'.format(self, e))
            raise
        except NotImplementedError as e:
            self.log.debug('[WARNING] Called unimplemented code in {!s}: '
                           '{!s}'.format(self, e))
            raise ExtractorError

        # Store text to cache
        if text and self.cache:
            self.cache.set(fileobject, text)

        return text

    def extract_text(self, fileobject):
        """
        Extracts any unstructured textual contents from the given file.

        NOTE: Should return an Unicode str or raise an exception.
              DO NOT return None! Instead, return an empty string.

        Args:
            fileobject: The instance of 'FileObject' to extract text from.

        Returns:
            Any textual contents of the file as an "internal" Unicode str.
            An empty string is returned if no text is found.

        Raises:
            ExtractorError: An error occurred during extraction.
        """
        raise NotImplementedError('Must be implemented by inheriting classes.')

    @classmethod
    def check_dependencies(cls):
        raise NotImplementedError('Must be implemented by inheriting classes.')

    def init_cache(self):
        _cache = persistence.get_cache(str(self))
        if _cache:
            self.cache = _cache
        else:
            self.cache = None


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


