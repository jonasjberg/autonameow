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

try:
    from thirdparty import epubzilla
except ImportError:
    epubzilla = None

from extractors.text.common import AbstractTextExtractor


log = logging.getLogger(__name__)


class EpubTextExtractor(AbstractTextExtractor):
    handles_mime_types = ['application/epub+zip']
    meowuri_root = 'contents.textual.text'

    # TODO: [TD0028] Implement extractor for E-books (pdf/epub/mobi/..)

    def __init__(self):
        super(EpubTextExtractor, self).__init__()

    def _get_text(self, source):
        self.log.debug('Extracting raw text from EPUB file ..')
        result = extract_text_with_epubzilla(source)
        return result

    @classmethod
    def check_dependencies(cls):
        return epubzilla is not None


def extract_text_with_epubzilla(file_path):
    epub_file = epubzilla.Epub.from_file(file_path)
    # TODO: [TD0028] FIX THIS!
    log.critical('The epub text extractor is still UNIMPLEMENTED! See [TD0028]')
    return ''
