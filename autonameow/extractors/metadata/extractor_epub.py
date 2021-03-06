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

try:
    import ebooklib
except ImportError:
    ebooklib = None

from extractors import ExtractorError
from extractors.metadata.base import BaseMetadataExtractor
from util import encoding as enc


class EpubMetadataExtractor(BaseMetadataExtractor):
    HANDLES_MIME_TYPES = ['application/epub+zip']
    IS_SLOW = False

    def extract(self, fileobject, **kwargs):
        return self._get_metadata(fileobject.abspath)

    def _get_metadata(self, filepath):
        raw_metadata = _get_epub_metadata(filepath)
        if not raw_metadata:
            return dict()

        metadata = self._to_internal_format(raw_metadata)
        return metadata

    def _to_internal_format(self, raw_metadata):
        # TODO: [TD0186] Re-implement epub metadata extractor
        return raw_metadata

    @classmethod
    def dependencies_satisfied(cls):
        # TODO: [TD0186] Re-implement epub metadata extractor
        return False


def _get_epub_metadata(filepath):
    assert ebooklib, 'Missing required module "ebooklib"'
    assert hasattr(ebooklib, 'epub')

    unicode_filepath = enc.decode_(filepath)
    assert isinstance(unicode_filepath, str)

    try:
        epub_book = ebooklib.epub.read_epub(unicode_filepath)
    except ebooklib.epub.EpubException as e:
        raise ExtractorError(e)

    raw_metadata = dict()

    all_namespaces = ebooklib.epub.NAMESPACES
    for namespace in all_namespaces:
        namespace_metadata = epub_book.metadata.get(namespace)
        if namespace_metadata:
            for field, value in namespace_metadata.items():
                absolute_key = '{!s}:{!s}'.format(namespace, field)
                raw_metadata[absolute_key] = value

    # TODO: [TD0186][incomplete] Re-implement epub metadata extractor
    return raw_metadata
