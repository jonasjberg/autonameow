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
import subprocess

from core import (
    persistence,
    util
)
from core.util import (
    sanity,
    textutils
)
from extractors import ExtractorError
from extractors.text.common import (
    AbstractTextExtractor,
    decode_raw
)


log = logging.getLogger(__name__)


CACHE_KEY = 'text'


class PdftotextTextExtractor(AbstractTextExtractor):
    HANDLES_MIME_TYPES = ['application/pdf']

    def __init__(self):
        super(PdftotextTextExtractor, self).__init__()

        self._cached_text = {}

        _cache = persistence.get_cache(str(self))
        if _cache:
            self.cache = _cache
            try:
                self._cached_text = self.cache.get(CACHE_KEY)
            except (KeyError, persistence.CacheError):
                pass
        else:
            self.cache = None

    def _cache_read(self, fileobject):
        if self._cached_text and fileobject in self._cached_text:
            return self._cached_text.get(fileobject)
        return None

    def _cache_write(self):
        if not self.cache:
            return

        try:
            self.cache.set(CACHE_KEY, self._cached_text)
        except persistence.CacheError:
            pass

    def _get_text(self, fileobject):
        _cached = self.cache.get(fileobject)
        if _cached is not None:
            self.log.info('Using cached text for: {!r}'.format(fileobject))
            return _cached

        result = extract_pdf_content_with_pdftotext(fileobject.abspath)
        if not result:
            return ''

        sanity.check_internal_string(result)
        text = result
        text = textutils.normalize_unicode(text)
        text = textutils.remove_nonbreaking_spaces(text)
        if text:
            self._cached_text.update({fileobject: text})
            self._cache_write()
            return text
        else:
            return ''

    @classmethod
    def check_dependencies(cls):
        return util.is_executable('pdftotext')


def extract_pdf_content_with_pdftotext(file_path):
    """
    Extract the plain text contents of a PDF document using "pdftotext".

    Args:
        file_path: The path to the PDF file to extract text from.

    Returns:
        Any textual content of the given PDF file, as Unicode strings.
    Raises:
        ExtractorError: The extraction failed and could not be completed.
    """
    try:
        process = subprocess.Popen(
            ['pdftotext', '-nopgbrk', '-enc', 'UTF-8', file_path, '-'],
            shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        stdout, stderr = process.communicate()
    except (OSError, ValueError, subprocess.SubprocessError) as e:
        raise ExtractorError(e)

    if process.returncode != 0:
        raise ExtractorError(
            'pdftotext returned {!s} with STDERR: "{!s}"'.format(
                process.returncode, stderr)
        )

    result = decode_raw(stdout)
    if not result:
        return ''
    return result

