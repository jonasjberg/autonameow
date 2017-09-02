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

from core import (
    exceptions,
    types
)
from extractors import (
    BaseExtractor,
    ExtractorError
)


log = logging.getLogger(__name__)


class Item(object):
    """
    Instances of this class wrap some extracted data with extra information.

    Extractors can specify which (if any) name template fields that the item
    is compatible with. For instance, date/time-information is could be used
    to populate the 'datetime' name template field.
    """
    def __init__(self, wrapper, fields=None):
        self.wrapper = wrapper

        if fields is not None:
            self.fields = fields
        else:
            self.fields = []

        self._value = None

    def __call__(self, raw_value):
        if self.wrapper:
            try:
                self._value = self.wrapper(raw_value)
            except exceptions.AWTypeError as e:
                pass
        else:
            # Fall back automatic type detection if 'wrapper' is unspecified.
            wrapped = types.try_wrap(raw_value)
            if wrapped is None:
                # log.critical(
                #     'Unhandled wrapping of tag name "{}" (type: {!s} '
                #     ' value: "{!s}")'.format(tag_name, type(value), value)
                # )
                self._value = raw_value
            else:
                self._value = wrapped

        return self

# 'EXIF:CreateDate': MetaInfo(
#     wrapper=types.AW_EXIFTOOLTIMEDATE,
#     fields=[
#         Weighted(name_template.datetime, probability=1),
#         Weighted(name_template.date, probability=1)
#     ]
# ),


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
        except ExtractorError as e:
            self.log.error(
                '{!s}: Initial extraction FAILED: {!s}'.format(self, e)
            )
            raise
        except NotImplementedError as e:
            self.log.debug('[WARNING] Called unimplemented code in {!s}: '
                           '{!s}'.format(self, e))
            raise ExtractorError

    def _to_internal_format(self, raw_metadata):
        out = {}

        for tag_name, value in raw_metadata.items():
            if tag_name in self.tagname_type_lookup:
                # Found a "template" 'Item' class.
                item = self.tagname_type_lookup[tag_name](value)
            else:
                # Use a default 'Item' class.
                item = Item(value)

            out[tag_name] = item

        return out

    def _get_raw_metadata(self):
        raise NotImplementedError('Must be implemented by inheriting classes.')

    @classmethod
    def check_dependencies(cls):
        raise NotImplementedError('Must be implemented by inheriting classes.')
