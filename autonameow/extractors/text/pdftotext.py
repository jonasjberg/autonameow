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
    cache,
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


class PdftotextTextExtractor(AbstractTextExtractor):
    HANDLES_MIME_TYPES = ['application/pdf']

    def __init__(self):
        super(PdftotextTextExtractor, self).__init__()

        self.cache = cache.get_cache(str(self))
        try:
            self._cached_text = self.cache.get('text')
        except (KeyError, cache.CacheError):
            self._cached_text = {}

    def _cache_read(self, source):
        if source in self._cached_text:
            _dp = util.displayable_path(source)
            self.log.info('Using cached text from source: {!s}'.format(_dp))
            return self._cached_text.get(source)
        return None

    def _cache_write(self):
        try:
            self.cache.set('text', self._cached_text)
        except cache.CacheError:
            pass

    def _get_text(self, source):
        _cached = self._cache_read(source)
        if _cached is not None:
            return _cached

        result = extract_pdf_content_with_pdftotext(source)
        if not result:
            return ''

        sanity.check_internal_string(result)
        text = result
        text = textutils.normalize_unicode(text)
        text = textutils.remove_nonbreaking_spaces(text)
        if text:
            # TODO: [TD0098] Use checksums as keys for cached data, not paths.
            #       .. I.E. use a more robust identifier as "source" below.
            self._cached_text.update({source: text})
            self._cache_write()
            return text
        else:
            return ''

    @classmethod
    def check_dependencies(cls):
        return util.is_executable('pdftotext')


def extract_pdf_content_with_pdftotext(pdf_file):
    """
    Extract the plain text contents of a PDF document using "pdftotext".

    Returns:
        Any textual content of the given PDF file, as Unicode strings.
    Raises:
        ExtractorError: The extraction failed and could not be completed.
    """
    try:
        process = subprocess.Popen(
            ['pdftotext', '-nopgbrk', '-enc', 'UTF-8', pdf_file, '-'],
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

