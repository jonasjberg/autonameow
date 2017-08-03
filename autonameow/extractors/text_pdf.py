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

from core import util
from extractors.textual import AbstractTextExtractor


class PdfTextExtractor(AbstractTextExtractor):
    handles_mime_types = ['application/pdf']
    data_query_string = 'contents.textual.raw_text'

    def __init__(self, source):
        super(PdfTextExtractor, self).__init__(source)

    def _get_raw_text(self):
        """
        Extracts the plain text contents of a PDF document.

        Returns:
            The textual contents of the PDF document as a unicode string.
        Raises:
            ExtractorError: The extraction failed.
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

                # TODO: [TD0044] Fix up post-processing extracted text.
                # pdf_text = textutils.sanitize_text(pdf_text)
                break

        if pdf_text:
            return pdf_text
        else:
            log.debug('Unable to extract textual content from PDF')
            return ''


def extract_pdf_content_with_pdftotext(pdf_file):
    """
    Extract the plain text contents of a PDF document using pdftotext.

    Returns:
        False or PDF content as a Unicode string (internal format)
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
        log.debug('pdftotext returned {} bytes of text'.format(len(stdout)))
        return util.decode_(stdout)


def extract_pdf_content_with_pypdf(pdf_file):
    """
    Extract the plain text contents of a PDF document using PyPDF2.

    Returns:
        False or the PDF text contents as Unicode strings (internal format)
    """
    try:
        file_reader = PyPDF2.PdfFileReader(util.decode_(pdf_file), 'rb')
    except (IOError, PyPdfError):
        log.error('Unable to read PDF file content.')
        # TODO: Raise exception instead?
        return False

    try:
        num_pages = file_reader.getNumPages()
    except PdfReadError:
        # NOTE: This now wholly determines whether a pdf is readable.
        #       Possible to not getNumPages but still be able to read the text?
        log.error('PDF document might be encrypted with restrictions '
                  'preventing reading.')
        return False

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
        content += file_reader.getPage(i).extractText()

    if content:
        assert(isinstance(content, str))
        return content
    else:
        log.debug('Unable to extract text with PyPDF2 ..')
        return False