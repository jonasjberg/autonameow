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
from collections import namedtuple

from extractors import BaseExtractor
from util import encoding as enc
from util import (
    disk,
    sanity
)


# TODO: [TD0043] Fetch values from the active configuration.
# BETWEEN_TAG_SEPARATOR = enc.bytestring_path(
#     opts.options['FILETAGS_OPTIONS'].get('between_tag_separator')
# )
BETWEEN_TAG_SEPARATOR = enc.bytestring_path(' ')
# FILENAME_TAG_SEPARATOR = enc.bytestring_path(
#     opts.options['FILETAGS_OPTIONS'].get('filename_tag_separator')
# )
FILENAME_TAG_SEPARATOR = enc.bytestring_path(' -- ')


FiletagsParts = namedtuple('FiletagsParts',
                           'datetime description tags extension')


class FiletagsExtractor(BaseExtractor):
    HANDLES_MIME_TYPES = ['*/*']
    IS_SLOW = False
    # TODO: [TD0178] Store only strings in 'FIELD_LOOKUP'.
    FIELD_LOOKUP = {
        'datetime': {
            'coercer': 'aw_timedate',
            'multivalued': False,
            'mapped_fields': [
                {'WeightedMapping': {'field': 'DateTime', 'probability': 1}},
                {'WeightedMapping': {'field': 'Date', 'probability': 1}},
            ],
            'generic_field': 'date_created'
        },
        'description': {
            'coercer': 'aw_string',
            'multivalued': False,
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Description', 'probability': 1}},
                {'WeightedMapping': {'field': 'Title', 'probability': 0.5}},
            ],
            'generic_field': 'description'
        },
        'tags': {
            'coercer': 'aw_string',
            'multivalued': True,
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Tags', 'probability': 1}},
            ],
            'generic_field': 'tags'
        },
        'extension': {
            'coercer': 'aw_string',
            'multivalued': False,
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Extension', 'probability': 1}},
            ],
        },
        'follows_filetags_convention': {
            'coercer': 'aw_boolean',
            'multivalued': False,
        }
    }

    def __init__(self):
        super().__init__()

        self._timestamp = None
        self._description = None
        self._tags = None
        self._extension = None
        self._follows_filetags_convention = None

    def extract(self, fileobject, **kwargs):
        result = self._partition_filename(fileobject.filename)

        if 'tags' in result:
            # NOTE(jonas): Assume that consistent output by sorting outweigh
            #              users that would like to keep the order unchanged ..
            result['tags'].sort()

        return result

    def _partition_filename(self, filename):
        parts = partition_basename(filename)
        follows_convention = follows_filetags_convention(parts)

        parts_dict = dict(parts._asdict())
        parts_dict['follows_filetags_convention'] = follows_convention
        result = self._to_internal_format(parts_dict)
        return result

    def _to_internal_format(self, raw_metadata):
        coerced_metadata = dict()

        for tag_name, value in raw_metadata.items():
            coerced = self.coerce_field_value(tag_name, value)
            if coerced is not None:
                coerced_metadata[tag_name] = coerced

        return coerced_metadata

    @classmethod
    def can_handle(cls, fileobject):
        # Assume 'FileObject' has a basename.
        return True

    @classmethod
    def check_dependencies(cls):
        return True


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
    sanity.check_internal_bytestring(FILENAME_TAG_SEPARATOR)

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

    # return timestamp, description, tags or [], suffix
    return FiletagsParts(timestamp, description, tags, suffix)


def follows_filetags_convention(filetags_parts):
    """
    Check if given parts indicate that a filename is in "filetags format".

                                 .------------ FILENAME_TAG_SEPARATOR
                                ||         .-- BETWEEN_TAG_SEPARATOR
                                VV         V
      20160722 Descriptive name -- firsttag tagtwo.txt
      |______| |______________|    |_____________| |_|
        date     description            tags       ext

    Filename parts 'date', 'description' and 'tags' must be present.

    Returns:
        True if the parts probably came from a file name in the "filetags"
        format. Otherwise False.
    """
    return bool(
        filetags_parts.datetime and filetags_parts.description
        and filetags_parts.tags
    )
