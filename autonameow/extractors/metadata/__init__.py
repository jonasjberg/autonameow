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

from collections import namedtuple

from core import (
    exceptions,
    types
)
from extractors import BaseExtractor


# MetaInfo = namedtuple('MetaInfo', ['wrapper', 'fields'])

class AbstractMetadataExtractor(BaseExtractor):
    # Lookup table that maps extractor-specific field names to wrapper classes.
    tagname_type_lookup = {}

    def __init__(self, source):
        super(AbstractMetadataExtractor, self).__init__(source)

        self._raw_metadata = None
        self.metadata = None

    def execute(self, **kwargs):
        """
        Executes this extractor and returns all results.

        All fields are returned by default.
        The keyword argument "field" can be used to extract specific data.

        Keyword Args:
            field: Return only data matching this field.

        Returns:
            Data matching the given field or False if the extraction fails.
        """
        if not self.metadata:
            self.log.debug('{!s} starting initial extraction ..'.format(self))
            self._raw_metadata = self._perform_initial_extraction()

            if not self._raw_metadata:
                self.log.error('{!s}: extraction FAILED'.format(self))
                return None

            # Internal data format boundary.  Wrap "raw" data with type classes.
            self.metadata = self._to_internal_format(self._raw_metadata)

        if 'field' not in kwargs:
            self.log.debug('{!s} returning all extracted data'.format(self))
            return self.metadata
        else:
            field = kwargs.get('field')
            self.log.debug('{!s} returning data matching field: '
                           '"{!s}"'.format(self, field))
            return self.metadata.get(field)

    def _perform_initial_extraction(self):
        try:
            _raw_metadata = self._get_raw_metadata()
            return _raw_metadata
        except exceptions.ExtractorError as e:
            self.log.error(
                '{!s}: Initial extraction FAILED: {!s}'.format(self, e)
            )
            raise
        except NotImplementedError as e:
            self.log.debug('[WARNING] Called unimplemented code in {!s}: '
                           '{!s}'.format(self, e))
            raise exceptions.ExtractorError

    def _to_internal_format(self, raw_metadata):
        out = {}
        for tag_name, value in raw_metadata.items():
            try:
                out[tag_name] = self._wrap_raw(tag_name, value)
            except exceptions.AWTypeError as e:
                self.log.warning(str(e))
                continue
        return out

    def _wrap_raw(self, tag_name, value):
        if tag_name in self.tagname_type_lookup:
            # First check the extractor-specific lookup table.
            wrapper_class = self.tagname_type_lookup[tag_name][0]
            return wrapper_class(value)
        else:
            # Fall back automatic type detection if not found in lookup table.
            wrapped = types.try_wrap(value)
            if wrapped is not None:
                return wrapped
            else:
                self.log.critical(
                    'Unhandled wrapping of tag name "{}" (type: {!s} '
                    ' value: "{!s}")'.format(tag_name, type(value), value)
                )
                return value

    def _get_raw_metadata(self):
        raise NotImplementedError('Must be implemented by inheriting classes.')



from .pdf import PyPDFMetadataExtractor
from .exiftool import ExiftoolMetadataExtractor
