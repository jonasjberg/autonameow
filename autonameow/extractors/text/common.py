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
import os

from core import (
    persistence,
    types,
)
from core import constants as C
from extractors import BaseExtractor
from util import encoding as enc
from util import sanity
from util.text import (
    collapse_whitespace,
    normalize_unicode,
    remove_blacklisted_lines,
    remove_blacklisted_re_lines,
    remove_nonbreaking_spaces,
    remove_zerowidth_spaces
)


log = logging.getLogger(__name__)


class AbstractTextExtractor(BaseExtractor):
    def __init__(self):
        """
        # NOTE: Call 'self.init_cache()' in subclasses init to enable caching.
        """
        super().__init__()

        self.cache = None
        self.BLACKLISTED_TEXTLINES = frozenset(list())
        self.BLACKLISTED_RE_TEXTLINES = frozenset(list())

    def extract(self, fileobject, **kwargs):
        text = self._get_text(fileobject)
        sanity.check_internal_string(text)

        # TODO: [TD0172] Extend the text extractors with additional fields.
        # TODO: [TD0173] Use 'pandoc' to extract information from documents.
        return {
            'full': text,
            # 'title': title
        }

    def shutdown(self):
        pass

    def _get_text(self, fileobject):
        cached_text = self._get_cached_text(fileobject)
        if cached_text:
            return cached_text

        text = self.extract_text(fileobject)
        if not text:
            return ''

        clean_text = self.cleanup(text)
        self._set_cached_text(fileobject, clean_text)
        return clean_text

    def _get_cached_text(self, fileobject):
        if not self.cache:
            return None
        try:
            cached_text = self.cache.get(fileobject)
        except persistence.PersistenceError as e:
            self.log.critical('Unable to read {!s} cache :: {!s}'.format(self, e))
        else:
            if cached_text:
                self.log.info('Using cached text for: {!r}'.format(fileobject))
                return cached_text
        return None

    def _set_cached_text(self, fileobject, text):
        if not self.cache:
            return
        try:
            self.cache.set(fileobject, text)
        except persistence.PersistenceError as e:
            self.log.critical('Unable to write {!s} cache :: {!s}'.format(self, e))

    @classmethod
    def python_source_filepath(cls):
        # NOTE(jonas): Subclasses of this class use a shared field meta yaml.
        return os.path.realpath(__file__)

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
        _cache = persistence.get_cache(
            str(self),
            max_filesize=C.TEXT_EXTRACTOR_CACHE_MAX_FILESIZE
        )
        if _cache:
            self.cache = _cache
        else:
            log.debug('Failed to initialize {!s} cache'.format(self))
            self.cache = None

    def cleanup(self, raw_text):
        if not raw_text:
            return ''

        sanity.check_internal_string(raw_text)
        text = raw_text
        text = normalize_unicode(text)
        # text = collapse_whitespace(text)
        text = remove_nonbreaking_spaces(text)
        text = remove_zerowidth_spaces(text)
        text = remove_blacklisted_lines(text, self.BLACKLISTED_TEXTLINES)
        text = remove_blacklisted_re_lines(text, self.BLACKLISTED_RE_TEXTLINES)
        return text if text else ''


def decode_raw(raw_text):
    try:
        text = types.AW_STRING(raw_text)
    except types.AWTypeError:
        try:
            text = enc.autodetect_decode(raw_text)
        except ValueError:
            log.warning('Unable to decode raw text')
            return ''
    return text
