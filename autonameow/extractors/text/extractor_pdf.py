# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg <autonameow@jonasjberg.com>
#   Source repository: https://github.com/jonasjberg/autonameow
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

import re

from extractors import ExtractorError
from extractors.text.base import BaseTextExtractor
from extractors.text.base import decode_raw
from util import process


# TODO: [TD0194] Handle (seemingly empty) pdfs without "overlay" text


class PdfTextExtractor(BaseTextExtractor):
    def __init__(self):
        super().__init__()

        self.init_cache()

    def _extract_text(self, fileobject):
        return extract_pdf_content_with_pdftotext(fileobject.abspath)

    @classmethod
    def dependencies_satisfied(cls):
        return process.is_executable('pdftotext')

    @classmethod
    def can_handle(cls, fileobject):
        return fileobject.mime_type == 'application/pdf'


def extract_pdf_content_with_pdftotext(filepath):
    """
    Extract the plain text contents of a PDF document using "pdftotext".

    Args:
        filepath: The path to the PDF file to extract text from.

    Returns:
        Any textual content of the given PDF file, as Unicode strings.
    Raises:
        ExtractorError: The extraction failed and could not be completed.
    """
    try:
        stdout = process.blocking_read_stdout(
            'pdftotext', '-q', '-nopgbrk', '-enc', 'UTF-8', filepath, '-'
        )
    except process.ChildProcessError as e:
        raise ExtractorError(e)

    result = decode_raw(stdout)
    return result.strip() if result else ''


def remove_intercharacter_spaces(s):
    assert isinstance(s, str)

    match = re.match(r'(\S\s){5}', s)
    if match:
        matched_string = match.group(0)
        fixed_matched_string = ''.join(matched_string.split())
        return fixed_matched_string

    return s
