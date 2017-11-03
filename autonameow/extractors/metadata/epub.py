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

import zipfile

from core import types
from core.model import (
    ExtractedData,
    WeightedMapping
)
from core.model import genericfields as gf
from core.namebuilder import fields
from extractors import (
    BaseExtractor,
    ExtractorError
)

from thirdparty import epubzilla


class EpubMetadataExtractor(BaseExtractor):
    HANDLES_MIME_TYPES = ['application/epub+zip']
    is_slow = False

    def __init__(self):
        super(EpubMetadataExtractor, self).__init__()

    def metainfo(self, *args, **kwargs):
        _metainfo = {
            'author': ExtractedData(
                coercer=types.AW_STRING,
                mapped_fields=[
                    WeightedMapping(fields.Author, probability=1),
                ],
                generic_field=gf.GenericAuthor
            ),
            'title': ExtractedData(
                coercer=types.AW_STRING,
                mapped_fields=[
                    WeightedMapping(fields.Title, probability=1),
                ],
                generic_field=gf.GenericTitle
            ),
            'producer': ExtractedData(
                coercer=types.AW_STRING,
                mapped_fields=[
                    WeightedMapping(fields.Author, probability=0.1),
                ],
                generic_field=gf.GenericProducer
            )
        }
        return _metainfo

    def extract(self, fileobject, **kwargs):
        _raw_metadata = _get_epub_metadata(fileobject.abspath)
        if _raw_metadata:
            return self._coerce(_raw_metadata)

    def _coerce(self, raw_metadata):
        out = {}

        _author_maybe = raw_metadata.get('author')
        if _author_maybe:
            try:
                out['author'] = types.AW_STRING(_author_maybe)
            except types.AWTypeError:
                pass

        _title_maybe = raw_metadata.get('title')
        if _title_maybe:
            try:
                out['title'] = types.AW_STRING(_title_maybe)
            except types.AWTypeError:
                pass

        _producer_maybe = raw_metadata.get('producer')
        if _producer_maybe:
            try:
                out['producer'] = types.AW_STRING(_producer_maybe)
            except types.AWTypeError:
                pass

        return out

    @classmethod
    def check_dependencies(cls):
        return epubzilla is not None


def _get_epub_metadata(source):
    try:
        epub_file = epubzilla.Epub.from_file(source)
    except (zipfile.BadZipFile, OSError) as e:
        raise ExtractorError('Unable to open epub file; "{!s}"'.format(e))
    else:
        try:
            return epub_file.metadata
        except AttributeError:
            return {}
