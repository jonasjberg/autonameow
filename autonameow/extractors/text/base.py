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

from core import constants as C
from core import persistence
from util import coercers
from util import encoding as enc
from util import sanity
from util.text import normalize_unicode
from util.text import normalize_horizontal_whitespace
from util.text import normalize_vertical_whitespace
from util.text import remove_ascii_control_characters
from util.text import remove_nonbreaking_spaces
from util.text import remove_zerowidth_spaces
from util.text import strip_single_space_lines


log = logging.getLogger(__name__)


class BaseTextExtractor(object):
    def __init__(self):
        """
        # NOTE: Call 'self.init_cache()' in subclasses init to enable caching.
        """
        self.log = logging.getLogger(
            '{!s}.{!s}'.format(__name__, self.__module__)
        )
        self.cache = None

    def extract_text(self, fileobject):
        text = self._check_cache_and_do_extraction(fileobject)
        sanity.check_internal_string(text)

        # TODO: [TD0173] Use 'pandoc' to extract information from documents.
        return text

    def _extract_text(self, fileobject):
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
    def dependencies_satisfied(cls):
        raise NotImplementedError('Must be implemented by inheriting classes.')

    @classmethod
    def can_handle(cls, fileobject):
        """
        Tests if a specific extractor class can handle a given file object.

        Inheriting extractor classes must override this method in order to
        determine if they can handle a given file object.

        Args:
            fileobject: The file to test as an instance of 'FileObject'.

        Returns:
            True if the extractor class can extract data from the given file,
            else False.
        """
        raise NotImplementedError('Must be implemented by inheriting classes.')

    def init_cache(self):
        """
        Called by subclasses to enable caching.
        """
        _cache = persistence.get_cache(
            str(self),
            max_filesize=C.TEXT_EXTRACTOR_CACHE_MAX_FILESIZE
        )
        if _cache:
            self.cache = _cache
        else:
            log.debug('Failed to initialize {!s} cache'.format(self))
            self.cache = None

    def _check_cache_and_do_extraction(self, fileobject):
        if self.cache:
            cached_text = self._get_cached_text(fileobject)
            if cached_text:
                return cached_text

        text = self._extract_text(fileobject)
        if not text:
            return ''

        clean_text = cleanup(text)

        if self.cache:
            self._set_cached_text(fileobject, clean_text)

        return clean_text

    def _get_cached_text(self, fileobject):
        try:
            cached_text = self.cache.get(fileobject)
        except persistence.PersistenceError as e:
            self.log.critical('Unable to read {!s} cache :: {!s}'.format(self, e))
        else:
            if cached_text:
                self.log.debug('Using cached text for: {!r}'.format(fileobject))
                return cached_text
        return None

    def _set_cached_text(self, fileobject, text):
        try:
            self.cache.set(fileobject, text)
        except persistence.PersistenceError as e:
            self.log.critical('Unable to write {!s} cache :: {!s}'.format(self, e))

    @classmethod
    def name(cls):
        # TODO: [TD0151] Fix inconsistent use of classes vs. class instances.
        return cls.__name__

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)


def decode_raw(raw_text):
    try:
        text = coercers.AW_STRING(raw_text)
    except coercers.AWTypeError:
        log.error('Text extractor "decode_raw()" failed to coerce raw text, '
                  'attempting auto-detection of text encoding..')
        try:
            text = enc.autodetect_decode(raw_text)
        except ValueError:
            log.warning('Unable to decode raw text by encoding auto-detection')
            return ''
    return text


def cleanup(raw_text):
    if not raw_text:
        return ''

    sanity.check_internal_string(raw_text)
    text = raw_text
    text = normalize_unicode(text)
    text = normalize_horizontal_whitespace(text)
    text = normalize_vertical_whitespace(text)
    text = strip_single_space_lines(text)
    text = remove_nonbreaking_spaces(text)
    text = remove_zerowidth_spaces(text)
    text = remove_ascii_control_characters(text)
    return text if text else ''
