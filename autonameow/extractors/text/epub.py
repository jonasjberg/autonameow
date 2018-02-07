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

import logging
import zipfile

from thirdparty import epubzilla
from extractors.text.common import AbstractTextExtractor


log = logging.getLogger(__name__)


class EpubTextExtractor(AbstractTextExtractor):
    HANDLES_MIME_TYPES = ['application/epub+zip']
    IS_SLOW = False

    # TODO: [TD0028] Implement extractor for E-books (pdf/epub/mobi/..)

    def __init__(self):
        super(EpubTextExtractor, self).__init__()

    def extract_text(self, fileobject):
        self.log.debug('Extracting raw text from EPUB file ..')
        result = extract_text_with_epubzilla(fileobject.abspath)
        return result

    @classmethod
    def check_dependencies(cls):
        return epubzilla is not None


def extract_text_with_epubzilla(file_path):
    try:
        epub_file = epubzilla.Epub.from_file(file_path)
    except zipfile.BadZipFile:
        pass

    # TODO: [TD0028] FIX THIS!
    log.critical('The epub text extractor is still UNIMPLEMENTED! See [TD0028]')
    return ''
