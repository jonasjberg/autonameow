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

import logging as log
import subprocess

import PyPDF2
from PyPDF2.utils import (
    PyPdfError,
    PdfReadError
)

from core.exceptions import ExtractorError
from core.util import textutils
from extractors.extractor import Extractor


class TextExtractor(Extractor):
    handles_mime_types = None
    data_query_string = None

    def __init__(self, source):
        super(TextExtractor, self).__init__(source)

        self._raw_text = None

    def query(self, field=None):
        if not self._raw_text:
            try:
                log.debug('TextExtractor received initial query ..')
                self._raw_text = self._get_raw_text()
            except ExtractorError as e:
                log.error('TextExtractor query FAILED: {!s}'.format(e))
                return False
            except NotImplementedError as e:
                log.debug('[WARNING] Called unimplemented code in {!s}: '
                          '{!s}'.format(self, e))
                return False

        if not field:
            log.debug('TextExtractor responding to query for all fields')
            return self._raw_text
        else:
            log.debug('MetadataExtractor responding to query for field: '
                      '"{!s}"'.format(field))
            return self._raw_text.get(field, False)

    def _get_raw_text(self):
        raise NotImplementedError('Must be implemented by inheriting classes.')


class PdfTextExtractor(TextExtractor):
    handles_mime_types = ['application/pdf']
    data_query_string = 'contents.textual.raw_text'

    def __init__(self, source):
        super(PdfTextExtractor, self).__init__(source)
        self._raw_text = None
        self._data = None

    def _get_raw_text(self):
        """
        Extracts the plain text contents of a PDF document.

        Returns:
            The textual contents of the PDF document or None.
        """
        pdf_text = None
        text_extractors = [extract_pdf_content_with_pdftotext,
                           extract_pdf_content_with_pypdf]
        for i, extractor in enumerate(text_extractors):
            log.debug('Running PDF text extractor {}/{}: '
                      '{!s}'.format(i + 1, len(text_extractors), extractor))
            pdf_text = extractor(self.source)
            if pdf_text and len(pdf_text) > 1:
                log.debug('Extracted text with: {}'.format(extractor.__name__))
                # TODO: Fix up post-processing extracted text.
                pdf_text = textutils.sanitize_text(pdf_text)
                break

        if pdf_text:
            log.debug('Extracted {} bytes of text'.format(len(pdf_text)))
            return pdf_text
        else:
            log.debug('Unable to extract textual content from PDF')
            raise ExtractorError

    def _get_data(self):
        pass


def extract_pdf_content_with_pdftotext(pdf_file):
    """
    Extract the plain text contents of a PDF document using pdftotext.

    Returns:
        False or PDF content as string
    """
    process = subprocess.Popen(
        ['pdftotext', '-nopgbrk', '-enc', 'UTF-8', pdf_file, '-'],
        shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        log.warning('pdftotext returned {!s}'.format(process.returncode))
        log.warning('pdftotext stderr: {!s}'.format(stderr))
        # TODO: Raise exception instead?
        return False
    else:
        return stdout.decode('utf-8', errors='replace')


def extract_pdf_content_with_pypdf(pdf_file):
    """
    Extract the plain text contents of a PDF document using PyPDF2.

    Returns:
        False or the PDF text contents as strings.
    """
    try:
        pdff = PyPDF2.PdfFileReader(open(pdf_file, 'rb'))
    except (IOError, PyPdfError):
        log.error('Unable to read PDF file content.')
        # TODO: Raise exception instead?
        return False

    try:
        num_pages = pdff.getNumPages()
    except PdfReadError:
        # NOTE: This now wholly determines whether a pdf is readable.
        #       Possible to not getNumPages but still be able to read the text?
        log.error('PDF document might be encrypted with restrictions '
                      'preventing reading.')
        # TODO: Raise exception instead?
        raise
    else:
        log.debug('Number of pdf pages: {}'.format(num_pages))

    # Start by extracting a limited range of pages.
    # TODO: Relevant info is more likely to be within some range of pages?
    log.debug('Extracting page #1')
    content = pdff.pages[0].extractText()
    if len(content) == 0:
        log.debug('Textual content of page #1 is empty.')
        pass

    # Collect more until a preset arbitrary limit is reached.
    for i in range(1, num_pages):
        if len(content) > 50000:
            log.debug('Extraction hit content size limit.')
            break
        log.debug('Extracting page {:<4} of {:<4} ..'.format(i + 1,
                                                                 num_pages))
        content += pdff.getPage(i).extractText()

    if content:
        return content
    else:
        log.debug('Unable to extract text with PyPDF2 ..')
        return False
