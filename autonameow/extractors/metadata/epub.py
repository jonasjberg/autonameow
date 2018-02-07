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

import zipfile

from core import types
from core.model import WeightedMapping
from core.namebuilder import fields
from extractors import (
    BaseExtractor,
    ExtractorError
)

from thirdparty import epubzilla


class EpubMetadataExtractor(BaseExtractor):
    HANDLES_MIME_TYPES = ['application/epub+zip']
    IS_SLOW = False
    FIELD_LOOKUP = {
        'author': {
            'coercer': types.AW_STRING,
            'mapped_fields': [
                WeightedMapping(fields.Author, probability=1),
            ],
            'generic_field': 'author'
        },
        'title': {
            'coercer': types.AW_STRING,
            'mapped_fields': [
                WeightedMapping(fields.Title, probability=1),
            ],
            'generic_field': 'title'
        },
        'producer': {
            'coercer': types.AW_STRING,
            'mapped_fields': [
                WeightedMapping(fields.Author, probability=0.1),
            ],
            'generic_field': 'producer'
        }
    }

    def __init__(self):
        super(EpubMetadataExtractor, self).__init__()

    def extract(self, fileobject, **kwargs):
        # NOTE: epubzilla returns a class instance.
        _raw_metadata = _get_epub_metadata(fileobject.abspath)
        if _raw_metadata:
            # Internal data format boundary.  Wrap "raw" data with type classes.
            metadata = self._to_internal_format(_raw_metadata)
            return metadata

        return dict()

    def _to_internal_format(self, raw_metadata):
        coerced_metadata = dict()

        # NOTE: epubzilla returns a class instance.
        #       Can not use 'providers.ProviderMixin.coerce_field_value()'
        for tag_name in self.FIELD_LOOKUP.keys():
            _data = raw_metadata.get(tag_name)
            if _data is not None:
                coerced = self.coerce_field_value(tag_name, _data)
                if coerced is not None:
                    coerced_metadata[tag_name] = coerced

        return coerced_metadata

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
            return dict()
