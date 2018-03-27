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

try:
    import chardet
except ImportError:
    chardet = None

import util
from core import constants as C
from extractors import ExtractorError
from extractors.text.common import (
    AbstractTextExtractor,
    decode_raw
)


class MarkdownTextExtractor(AbstractTextExtractor):
    HANDLES_MIME_TYPES = ['text/plain']
    IS_SLOW = False

    def extract_text(self, fileobject):
        return get_plaintext_from_markdown_file_with_pandoc(fileobject.abspath)

    @classmethod
    def can_handle(cls, fileobject):
        return bool(
            cls._evaluate_mime_type_glob(fileobject)
            and fileobject.basename_suffix in C.MARKDOWN_BASENAME_SUFFIXES
        )

    @classmethod
    def check_dependencies(cls):
        return util.is_executable('pandoc')


def get_plaintext_from_markdown_file_with_pandoc(filepath):
    # TODO: Convert non-UTF8 source text to UTF-8.
    #       pandoc does not handle non-UTF8 input.
    try:
        process = subprocess.Popen(
            ['pandoc', '--from', 'markdown', '--to', 'plain', '--', filepath],
            shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        stdout, stderr = process.communicate()
    except (OSError, ValueError, subprocess.SubprocessError) as e:
        raise ExtractorError(e)

    if process.returncode != 0:
        raise ExtractorError(
            'pandoc returned {!s} with STDERR: "{!s}"'.format(
                process.returncode, stderr)
        )

    # pandoc uses UTF-8 characters encoding for both input and output
    result = decode_raw(stdout)
    return result.strip() if result else ''
