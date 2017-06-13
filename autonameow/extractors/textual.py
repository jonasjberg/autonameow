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

import PyPDF2
from PyPDF2.utils import (
    PyPdfError,
    PdfReadError
)


def extract_pdf_content_with_pdftotext(pdf_file):
    """
    Extract the plain text contents of a PDF document using pdftotext.

    Returns:
        False or PDF content as string
    """
    try:
        pipe = subprocess.Popen(['pdftotext', '-nopgbrk', '-enc', 'UTF-8',
                                 pdf_file, '-'], shell=False,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
    except ValueError:
        logging.warning(
            '"subprocess.Popen" was called with invalid arguments.')
        return False

    stdout, stderr = pipe.communicate()
    if pipe.returncode != 0:
        logging.warning('subprocess returned [{}] - STDERROR: '
                        '{}'.format(pipe.returncode, stderr))
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
        logging.error('Unable to read PDF file content.')
        # TODO:
        return False

    try:
        num_pages = pdff.getNumPages()
    except PdfReadError:
        # NOTE: This now wholly determines whether a pdf is readable.
        #       Possible to not getNumPages but still be able to read the text?
        logging.error('PDF document might be encrypted with restrictions '
                      'preventing reading.')
        # TODO: Raise exception instead?
        raise
    else:
        logging.debug('Number of pdf pages: {}'.format(num_pages))

    # Start by extracting a limited range of pages.
    # TODO: Relevant info is more likely to be within some range of pages?
    logging.debug('Extracting page #1')
    content = pdff.pages[0].extractText()
    if len(content) == 0:
        logging.debug('Textual content of page #1 is empty.')
        pass

    # Collect more until a preset arbitrary limit is reached.
    for i in range(1, num_pages):
        if len(content) > 50000:
            logging.debug('Extraction hit content size limit.')
            break
        logging.debug('Extracting page {:<4} of {:<4} ..'.format(i + 1,
                                                                 num_pages))
        content += pdff.getPage(i).extractText()

    if content:
        return content
    else:
        logging.debug('Unable to extract text with PyPDF2 ..')
        return False