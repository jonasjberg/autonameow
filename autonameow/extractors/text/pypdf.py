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
    import PyPDF2
    from PyPDF2.utils import (
        PyPdfError,
        PdfReadError
    )
except ImportError:
    PyPDF2 = None
    PyPdfError = None
    PdfReadError = None

from core import (
    cache,
    util
)
from core.util import sanity
from extractors import ExtractorError
from extractors.text.common import AbstractTextExtractor


log = logging.getLogger(__name__)


class PyPDFTextExtractor(AbstractTextExtractor):
    HANDLES_MIME_TYPES = ['application/pdf']

    def __init__(self):
        super(PyPDFTextExtractor, self).__init__()

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

        text = extract_pdf_content_with_pypdf(source)
        if text and len(text) > 1:
            # TODO: [TD0098] Use checksums as keys for cached data, not paths.
            #       .. I.E. use a more robust identifier as "source" below.
            self._cached_text.update({source: text})
            self._cache_write()
            return text
        else:
            self.log.debug('Unable to extract textual content from PDF')
            return ''

    @classmethod
    def check_dependencies(cls):
        # PyPDF2 strips all whitespace, or does not insert spaces when the PDF
        # does not contain printable spaces. This a apparently a known issue.

        # Skip for now.
        # TODO: Remove PyPDF2?
        # return PyPDF2 is not None
        return False


def extract_pdf_content_with_pypdf(pdf_file):
    """
    Extract the plain text contents of a PDF document using PyPDF2.

    Returns:
        Any textual content of the given PDF file, as Unicode strings.
    Raises:
        ExtractorError: The extraction failed and could not be completed.
    """
    try:
        file_reader = PyPDF2.PdfFileReader(util.decode_(pdf_file), 'rb')
    except (OSError, PyPdfError, UnicodeDecodeError) as e:
        raise ExtractorError(e)

    try:
        num_pages = file_reader.getNumPages()
    except PdfReadError as e:
        # NOTE: This now wholly determines whether a pdf is readable.
        #       Possible to not getNumPages but still be able to read the text?
        log.warning('PDF document might be encrypted and/or has restrictions'
                    ' that prevent reading')
        raise ExtractorError('PyPDF2.PdfReadError: "{!s}"'.format(e))

    # NOTE(jonas): From the PyPDF2 documentation:
    # https://pythonhosted.org/PyPDF2/PageObject.html#PyPDF2.pdf.PageObject
    #
    # extractText()
    # Locate all text drawing commands, in the order they are provided in the
    # content stream, and extract the text. This works well for some PDF files,
    # but poorly for others, depending on the generator used. This will be
    # refined in the future. Do not rely on the order of text coming out of
    # this function, as it will change if this function is made more
    # sophisticated.
    # Returns: a unicode string object.

    content = file_reader.pages[0].extractText()
    for i in range(1, num_pages):
        try:
            content += file_reader.getPage(i).extractText()
        except KeyError:
            pass

    if content:
        sanity.check_internal_string(content)
        return content
    else:
        log.debug('Unable to extract text with PyPDF2 ..')
        return ''
