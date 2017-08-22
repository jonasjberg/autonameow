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

try:
    from thirdparty import epubzilla
except ImportError:
    epubzilla = None

from extractors.text import AbstractTextExtractor


class EpubTextExtractor(AbstractTextExtractor):
    handles_mime_types = ['application/epub+zip']
    data_meowuri = 'contents.textual.raw_text'

    # TODO: [TD0028] Implement extractor for E-books (pdf/epub/mobi/..)

    def __init__(self, source):
        super(EpubTextExtractor, self).__init__(source)

    def _get_raw_text(self):
        log.debug('Extracting raw text from EPUB file ..')
        result = extract_text_with_epubzilla(self.source)

    @classmethod
    def check_dependencies(cls):
        return epubzilla is not None


def extract_text_with_epubzilla(file_path):
    epub_file = epubzilla.Epub.from_file(file_path)
    print(epub_file)
    return epub_file
