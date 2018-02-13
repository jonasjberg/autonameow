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

import subprocess

from extractors import ExtractorError
from extractors.text.common import (
    AbstractTextExtractor,
    decode_raw
)
import util


class PdfTextExtractor(AbstractTextExtractor):
    HANDLES_MIME_TYPES = ['application/pdf']
    IS_SLOW = False

    def __init__(self):
        super().__init__()

        self.init_cache()

    def extract_text(self, fileobject):
        self.log.debug('Calling pdftotext')
        result = extract_pdf_content_with_pdftotext(fileobject.abspath)
        return result

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
    return result.strip() if result else ''
