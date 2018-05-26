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

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

try:
    from ebooklib import epub
except ImportError:
    epub = None

from extractors import ExtractorError
from extractors.text.common import AbstractTextExtractor
from util import encoding as enc
from util import sanity


class EpubTextExtractor(AbstractTextExtractor):
    HANDLES_MIME_TYPES = ['application/epub+zip']
    IS_SLOW = False

    def __init__(self):
        super().__init__()

        self.init_cache()

    def extract_text(self, fileobject):
        return extract_text_with_ebooklib(fileobject.abspath)

    @classmethod
    def dependencies_satisfied(cls):
        return all(m is not None for m in (epub, BeautifulSoup))


def extract_text_with_ebooklib(filepath):
    assert epub, 'Missing required module "epub"'
    assert BeautifulSoup, 'Missing required module "BeautifulSoup"'

    unicode_filepath = enc.decode_(filepath)
    sanity.check_internal_string(unicode_filepath)

    try:
        book = epub.read_epub(unicode_filepath)
    except epub.EpubException as e:
        raise ExtractorError(e)
    except KeyError as e:
        raise ExtractorError('Unhandled exception in "ebooklib": {!s}'.format(e))

    # TODO: The epub text extractor repeats a lot of text.
    # NOTE: Books produced by 'calibre' are messy. Seems to use tables for
    # formatting and classes "calibreN" with N being just about any number..
    text_lines = list()
    for id_, _ in book.spine:
        item = book.get_item_with_id(id_)
        soup = BeautifulSoup(item.content, 'lxml')
        for child in soup.find_all(['div', 'h1', 'h2', 'h3', 'h4', 'title', 'p', 'td']):
            child_text = child.text
            child_text = child_text.strip()
            if child_text:
                text_lines.append(child_text)

    result = '\n'.join(text_lines)
    return result
