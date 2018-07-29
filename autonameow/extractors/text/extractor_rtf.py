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

from extractors import ExtractorError
from extractors.text.base import BaseTextExtractor
from extractors.text.base import decode_raw
from util import process


class RichTextFormatTextExtractor(BaseTextExtractor):
    def _extract_text(self, fileobject):
        return extract_text_with_unrtf(fileobject.abspath)

    @classmethod
    def dependencies_satisfied(cls):
        return process.is_executable('unrtf')

    @classmethod
    def can_handle(cls, fileobject):
        return fileobject.mime_type == 'text/rtf'


def decode_ascii(string):
    try:
        return string.decode('ascii')
    except UnicodeError:
        return decode_raw(string)


def extract_text_with_unrtf(filepath):
    """
    Extract the plain text contents of a RTF document using "UnRTF".

    Args:
        filepath: The path to the RTF file to extract text from.

    Returns:
        Any textual content of the given RTF file, as Unicode strings.

    Raises:
        ExtractorError: The extraction failed and could not be completed.
    """
    try:
        stdout = process.blocking_read_stdout(
            'unrtf', '--text', filepath
        )
    except process.ChildProcessError as e:
        raise ExtractorError(e)

    # NOTE(jonas): UnRTF outputs plain ASCII with '--text'.
    decoded_output = decode_ascii(stdout)

    # First part is a header with UnRTF version and any metadata.
    # TODO: A rtf metadata extractor would duplicate this call!
    # Tells of underlying problem with arranging extractors by text, metadata?

    HEADER = '-' * 17 + '\n'
    # TODO: Do something with this metadata?
    meta = decoded_output.split(HEADER, 1)[0]
    text = decoded_output.split(HEADER, 1)[-1]
    return text
