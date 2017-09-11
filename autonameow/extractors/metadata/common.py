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

from extractors import (
    BaseExtractor,
    ExtractedData,
    ExtractorError
)


log = logging.getLogger(__name__)


class AbstractMetadataExtractor(BaseExtractor):
    # Lookup table that maps extractor-specific field names to wrapper classes.
    tagname_type_lookup = {}

    def __init__(self):
        super(AbstractMetadataExtractor, self).__init__()

    def execute(self, source, **kwargs):
        self.log.debug('{!s} starting initial extraction ..'.format(self))

        try:
            _raw_metadata = self._get_raw_metadata(source)
        except ExtractorError as e:
            self.log.error(
                '{!s}: extraction FAILED: {!s}'.format(self, e)
            )
            raise
        except NotImplementedError as e:
            self.log.debug('[WARNING] Called unimplemented code in {!s}: '
                           '{!s}'.format(self, e))
            raise ExtractorError

        # Internal data format boundary.  Wrap "raw" data with type classes.
        # TODO: [TD0087] Clean up messy (and duplicated) wrapping of "raw" data.
        metadata = self._to_internal_format(_raw_metadata)

        self.log.debug('{!s} returning all extracted data'.format(self))
        return metadata

    def _to_internal_format(self, raw_metadata):
        out = {}

        for tag_name, value in raw_metadata.items():
            if tag_name in self.tagname_type_lookup:
                # Found a "template" 'Item' class.
                wrapper = self.tagname_type_lookup[tag_name]
            else:
                # Use a default 'Item' class.
                wrapper = ExtractedData(wrapper=None, mapped_fields=None)

            item = wrapper(value)
            if item:
                out[tag_name] = item

        return out

    def _get_raw_metadata(self, source):
        raise NotImplementedError('Must be implemented by inheriting classes.')

    @classmethod
    def check_dependencies(cls):
        raise NotImplementedError('Must be implemented by inheriting classes.')
