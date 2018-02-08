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

import util
from extractors import ExtractorError
from extractors.text.common import (
    AbstractTextExtractor,
    decode_raw
)


class RichTextFormatTextExtractor(AbstractTextExtractor):
    HANDLES_MIME_TYPES = ['text/rtf']
    IS_SLOW = False

    def extract_text(self, fileobject):
        self.log.debug('Calling unrtf')
        result = extract_text_with_unrtf(fileobject.abspath)
        return result

    @classmethod
    def check_dependencies(cls):
        return util.is_executable('unrtf')


def decode_ascii(string):
    try:
        return string.decode('ascii')
    except UnicodeError:
        return decode_raw(string)


def extract_text_with_unrtf(file_path):
    """
    Extract the plain text contents of a RTF document using "UnRTF".

    Args:
        file_path: The path to the RTF file to extract text from.

    Returns:
        Any textual content of the given RTF file, as Unicode strings.

    Raises:
        ExtractorError: The extraction failed and could not be completed.
    """
    # NOTE(jonas): UnRTF outputs plain ASCII with '--text'.
    try:
        process = subprocess.Popen(
            ['unrtf', '--text', file_path],
            shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        stdout, stderr = process.communicate()
    except (OSError, ValueError, subprocess.SubprocessError) as e:
        raise ExtractorError(e)

    decoded_output = decode_ascii(stdout)

    # First part is a header with UnRTF version and any metadata.
    # TODO: A rtf metadata extractor would duplicate this call!
    # Tells of underlying problem with arranging extractors by text, metadata?

    HEADER = '-' * 17 + '\n'
    # TODO: Do something with this metadata?
    meta = decoded_output.split(HEADER, 1)[0]
    text = decoded_output.split(HEADER, 1)[-1]
    return text
