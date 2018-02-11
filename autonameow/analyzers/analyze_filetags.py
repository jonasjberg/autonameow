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

import re

from analyzers import BaseAnalyzer
from core import types
from core.model import WeightedMapping
from core.namebuilder import fields
from util import encoding as enc
from util import disk


# TODO: [TD0037] Allow further customizing of "filetags" options.
# TODO: [TD0043] Allow further customizing of "filetags" options.

DATE_SEP = rb'[:\-._ ]?'
TIME_SEP = rb'[:\-._ T]?'
DATE_REGEX = rb'[12]\d{3}' + DATE_SEP + rb'[01]\d' + DATE_SEP + rb'[0123]\d'
TIME_REGEX = (rb'[012]\d' + TIME_SEP + rb'[012345]\d' + TIME_SEP
              + rb'[012345]\d(.[012345]\d)?')
FILENAMEPART_TS_REGEX = re.compile(
    DATE_REGEX + rb'([T_ -]?' + TIME_REGEX + rb')?'
)


# TODO: [TD0043][TD0009] Fetch values from the active configuration.
# BETWEEN_TAG_SEPARATOR = enc.bytestring_path(
#     opts.options['FILETAGS_OPTIONS'].get('between_tag_separator')
# )
BETWEEN_TAG_SEPARATOR = enc.bytestring_path(' ')
# FILENAME_TAG_SEPARATOR = enc.bytestring_path(
#     opts.options['FILETAGS_OPTIONS'].get('filename_tag_separator')
# )
FILENAME_TAG_SEPARATOR = enc.bytestring_path(' -- ')


class FiletagsAnalyzer(BaseAnalyzer):
    RUN_QUEUE_PRIORITY = 0.5
    HANDLES_MIME_TYPES = ['*/*']

    # TODO: [TD0157] Look into analyzers 'FIELD_LOOKUP' attributes.
    FIELD_LOOKUP = {
        'datetime': {
            'coercer': types.AW_TIMEDATE,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=0.75),
            ],
            'generic_field': 'date_created'
        },
        'description': {
            'coercer': types.AW_STRING,
            'mapped_fields': [
                WeightedMapping(fields.Description, probability=1),
                WeightedMapping(fields.Title, probability=0.5),
            ],
            'generic_field': 'description'
        },
        'tags': {
            'coercer': types.AW_STRING,
            'multivalued': True,
            'mapped_fields': [
                WeightedMapping(fields.Tags, probability=1),
            ],
            'generic_field': 'tags'
        },
        'extension': {
            'coercer': types.AW_MIMETYPE,
            'mapped_fields': [
                WeightedMapping(fields.Extension, probability=1),
            ],
            'generic_field': 'mime_type'
        },
        'follows_filetags_convention': {
            'coercer': types.AW_BOOLEAN,
            'multivalued': False,
            'mapped_fields': None,
            'generic_field': None
        }
    }

    def __init__(self, fileobject, config, request_data_callback):
        super().__init__(fileobject, config, request_data_callback)

        self._timestamp = None
        self._description = None
        self._tags = None
        self._extension = None
        self._follows_filetags_convention = None

    def analyze(self):
        (_raw_timestamp, _raw_description, _raw_tags,
         _raw_extension) = partition_basename(self.fileobject.abspath)

        self._timestamp = self.coerce_field_value('datetime', _raw_timestamp)
        self._description = self.coerce_field_value('description', _raw_description)

        self._tags = []
        if _raw_tags:
            _coerced_tags = self.coerce_field_value('tags', _raw_tags)
            if _coerced_tags:
                self._tags = sorted(_coerced_tags)

        self._extension = self.coerce_field_value('extension', _raw_extension)

        _raw_follows_convention = self.follows_filetags_convention()
        self._follows_filetags_convention = self.coerce_field_value(
            'follows_filetags_convention', _raw_follows_convention
        )

        if self._timestamp:
            self._add_results('datetime', {
                'value': self._timestamp,
                'coercer': types.AW_TIMEDATE,
                'mapped_fields': [
                    WeightedMapping(fields.DateTime, probability=1),
                    WeightedMapping(fields.Date, probability=1),
                ],
                'generic_field': 'date_created'
            })
        if self._description:
            self._add_results('description', {
                'value': self._description,
                'coercer': types.AW_STRING,
                'mapped_fields': [
                    WeightedMapping(fields.Description, probability=1),
                ],
                'generic_field': 'description'
            })
        if self._tags:
            self._add_results('tags', {
                'value': self._tags,
                'coercer': types.listof(types.AW_STRING),
                'mapped_fields': [
                    WeightedMapping(fields.Tags, probability=1),
                ],
                'generic_field': 'tags'

            })
        if self._extension:
            self._add_results('extension', {
                'value': self._extension,
                'coercer': types.AW_MIMETYPE,
                'mapped_fields': [
                    WeightedMapping(fields.Extension, probability=1),
                ],
                'generic_field': 'mime_type'
            })
        self._add_results('follows_filetags_convention', {
            'value': self._follows_filetags_convention,
            'multivalued': False,
            'coercer': types.AW_BOOLEAN
        })

    def follows_filetags_convention(self):
        """
        Returns whether the file name is in the "filetags" format.

                                     .------------ FILENAME_TAG_SEPARATOR
                                    ||         .-- BETWEEN_TAG_SEPARATOR
                                    VV         V
          20160722 Descriptive name -- firsttag tagtwo.txt
          |______| |______________|    |_____________| |_|
             ts          base               tags       ext

        All filename parts; 'ts', 'base' and 'tags' must be present.

        Returns:
            True if the filename is in the "filetags" format.
            Otherwise False.
        """
        if self._timestamp and self._description and self._tags:
            return True
        return False

    @classmethod
    def can_handle(cls, fileobject):
        # Assume 'FileObject' has a path and a basename.
        return True

    @classmethod
    def check_dependencies(cls):
        return True


def partition_basename(file_path):
    """
    Splits a basename into parts as per the "filetags" naming convention.

    Does "filename partitioning" -- split the file name into four parts:

    * timestamp     Date-/timestamp.
    * description   Descriptive text.
    * tags          List of tags created within the "filetags" workflow.
    * extension     File extension (really the "compound suffix").

    Example basename '20160722 Descriptive name -- firsttag tagtwo.txt':

                                    .------------ FILENAME_TAG_SEPARATOR
                                   ||         .-- BETWEEN_TAG_SEPARATOR
                                   VV         V
         20160722 Descriptive name -- firsttag tagtwo.txt
         |______| |______________|    |_____________| |_|
        timestamp   description            tags       ext

    Args:
        file_path: Path whose basename to split, as an "internal bytestring".
    Returns:
        Any identified parts as a tuple of 4 elements (quad);
            'timestamp', 'description', 'tags', 'extension', where 'tags' is a
            list of Unicode strings, and the others are plain Unicode strings.
    """
    prefix, suffix = disk.split_basename(file_path)

    timestamp = FILENAMEPART_TS_REGEX.match(prefix)
    if timestamp:
        timestamp = timestamp.group(0)
        prefix = prefix.lstrip(timestamp)

    if not re.findall(FILENAME_TAG_SEPARATOR, prefix):
        if prefix:
            description = prefix.strip()
        else:
            description = None
        tags = []
    else:
        # NOTE: Handle case with multiple "BETWEEN_TAG_SEPARATOR" better?
        prefix_tags_list = re.split(FILENAME_TAG_SEPARATOR, prefix, 1)
        description = prefix_tags_list[0].strip()
        try:
            tags = prefix_tags_list[1].split(BETWEEN_TAG_SEPARATOR)
        except IndexError:
            tags = []
        else:
            tags = [t.strip() for t in tags if t]

    # Encoding boundary;  Internal filename bytestring --> internal Unicode str
    def decode_if_not_none_or_empty(bytestring_maybe):
        if bytestring_maybe:
            return enc.decode_(bytestring_maybe)
        return None

    timestamp = decode_if_not_none_or_empty(timestamp)
    description = decode_if_not_none_or_empty(description)
    tags = [decode_if_not_none_or_empty(t) for t in tags]
    suffix = decode_if_not_none_or_empty(suffix)

    return timestamp, description, tags or [], suffix
