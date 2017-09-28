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

from core import util
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

    def _get_text(self, source):
        text = extract_pdf_content_with_pdftotext(source)
        if text and len(text) > 1:
            self.log.debug('Returning extracted text')
            return text
        else:
            self.log.debug('Unable to extract textual content from PDF')
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

    text = decode_raw(stdout)
    text = textutils.normalize_unicode(text)
    text = textutils.remove_nonbreaking_spaces(text)
    if text:
        sanity.check_internal_string(text)
        return text
    else:
        return ''
