# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2020 Jonas Sjöberg <autonameow@jonasjberg.com>
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

from core import constants as C
from extractors import ExtractorError
from extractors.text.base import BaseTextExtractor
from extractors.text.base import decode_raw
from util import process


class MarkdownTextExtractor(BaseTextExtractor):
    def _extract_text(self, fileobject):
        return get_plaintext_from_markdown_file_with_pandoc(fileobject.abspath)

    @classmethod
    def dependencies_satisfied(cls):
        return process.is_executable('pandoc')

    @classmethod
    def can_handle(cls, fileobject):
        return bool(
            fileobject.mime_type == 'text/plain'
            and fileobject.basename_suffix in C.MARKDOWN_BASENAME_SUFFIXES
        )


def get_plaintext_from_markdown_file_with_pandoc(filepath):
    # TODO: Convert non-UTF8 source text to UTF-8.
    #       pandoc does not handle non-UTF8 input.
    try:
        stdout = process.blocking_read_stdout(
            'pandoc', '--from', 'markdown', '--to', 'plain', '--', filepath
        )
    except process.ChildProcessFailure as e:
        raise ExtractorError(e)

    # NOTE(jonas): pandoc uses UTF-8 encoding for both input and output
    result = decode_raw(stdout)
    return result.strip() if result else ''
