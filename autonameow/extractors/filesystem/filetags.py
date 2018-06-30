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

"""
Extracts information from file names following the "filetags" naming
convention.

Based on the work and original ideas expressed by Karl Voit.
Refer to his online resources for additional information:

  PhD thesis:  http://karl-voit.at/tagstore/downloads/Voit2012b.pdf
   Blog post:  http://karl-voit.at/managing-digital-photographs/
      GitHub:  https://github.com/novoid/

The original 'filetags' program is written by Karl Voit and is available
on his GitHub page:  https://github.com/novoid/filetags
This extractor is intended to extract information from files whose names
follow the naming convention proposed by Karl:

(<ISO date/time stamp>)? <descriptive file name> -- <list of tags separated by spaces>.<file extension>


The following is the standard used within autonameow.
A "filetags filename" is composed of the following parts:

  timestamp   Either a date ("YYYY-mm-dd") or a date with time ("YYYY-mm-ddTHHMMSS")
description   Descriptive file name
       tags   List of tags separated by 'BETWEEN_TAG_SEPARATOR'.
              A 'FILENAME_TAG_SEPARATOR' marks the start of tags.
  extension   The "compound file extension" or "basename suffix".
              E.G. the file name 'foo.tar.gz' extension is 'tar.gz',
              not just the conventional(/proper) extension 'gz'.
              A period following the tags marks the start of the extension.

Example with filename '20160722 Descriptive name -- firsttag tagtwo.txt':

                                .------------ FILENAME_TAG_SEPARATOR
                              .||.        .-- BETWEEN_TAG_SEPARATOR
                              ||||        |
     20160722 Descriptive name -- firsttag tagtwo.txt
     |______| |______________|    |_____________| |_|
    timestamp   description            tags       extension

File names that contain all 'timestamp', 'description' and 'tags' parts are
considered to follow the filetags convention, with 'extension' being optional.
"""

import re
from collections import namedtuple

from extractors.metadata.base import BaseMetadataExtractor
from util import disk
from util import encoding as enc
from util import sanity


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
                           'timestamp description tags extension')


class FiletagsExtractor(BaseMetadataExtractor):
    HANDLES_MIME_TYPES = ['*/*']
    IS_SLOW = False

    def __init__(self):
        super().__init__()

    def extract(self, fileobject, **kwargs):
        return self._get_metadata(fileobject.filename)

    def _get_metadata(self, file_basename):
        metadata = self._partition_filename(file_basename)

        if 'tags' in metadata:
            # NOTE(jonas): Assume that consistent output by sorting outweigh
            #              users that would like to keep the order unchanged ..
            metadata['tags'].sort()

        return metadata

    def _partition_filename(self, filename):
        parts = partition_basename(filename)
        follows_convention = follows_filetags_convention(parts)

        parts_dict = dict(parts._asdict())
        parts_dict['follows_filetags_convention'] = follows_convention

        # TODO: [hack] The 'timestamp' can be either only a date or a date AND
        #       time.. For now just copy the same value to both places and let
        #       the coercion fail for one of them ..
        parts_dict['date'] = parts_dict['timestamp']
        parts_dict['datetime'] = parts_dict['timestamp']
        result = self._to_internal_format(parts_dict)
        return result

    def _to_internal_format(self, raw_metadata):
        coerced_metadata = dict()

        for field, value in raw_metadata.items():
            if value is None:
                # Value of field "timestamp" is None if missing.
                continue

            coerced = self.coerce_field_value(field, value)
            if coerced is not None:
                coerced_metadata[field] = coerced

        return coerced_metadata

    @classmethod
    def can_handle(cls, fileobject):
        # File name should not be empty or only whitespace.
        return bool(fileobject.filename.strip())

    @classmethod
    def dependencies_satisfied(cls):
        return True


# TODO: [TD0037] Allow further customizing of "filetags" options.
# TODO: [TD0043] Allow further customizing of "filetags" options.


RE_FILENAMEPART_ISODATE = re.compile(rb'''
[12]\d{3}       # YYYY  year
[:\-._ ]?       # separator
[01]\d          # MM    months
[:\-._ ]?       # separator
[0123]\d        # DD    days

(               # Begin optional time group
[T_ -]?         # Separator between date and time
[012]\d         # HH    hours
[:\-._ T]?      # separator
[012345]\d      # MM    minutes
[:\-._ T]?      # separator
[012345]\d      # SS    seconds
(.[012345]\d)?  # ss    nanoseconds (?)
)?              # End optional time group
''', re.VERBOSE)


def partition_basename(filepath):
    """
    Splits a basename into parts as per the "filetags" naming convention.

    Args:
        filepath: Path whose basename to split, as an "internal bytestring".
    Returns:
        Any identified parts as a named tuple with 4 elements;
        'timestamp', 'description', 'tags', 'extension', where 'tags' is a
        list of Unicode strings, and the others are plain Unicode strings.
    """
    sanity.check_internal_bytestring(FILENAME_TAG_SEPARATOR)

    prefix, suffix = disk.split_basename(filepath)

    timestamp = RE_FILENAMEPART_ISODATE.match(prefix)
    if timestamp:
        timestamp = timestamp.group(0)
        prefix = prefix.lstrip(timestamp)

    if not re.findall(FILENAME_TAG_SEPARATOR, prefix):
        if prefix:
            description = prefix.strip()
        else:
            description = None
        tags = list()
    else:
        # NOTE: Handle case with multiple "BETWEEN_TAG_SEPARATOR" better?
        prefix_tags_list = re.split(FILENAME_TAG_SEPARATOR, prefix, 1)
        description = prefix_tags_list[0].strip()
        try:
            tags = prefix_tags_list[1].split(BETWEEN_TAG_SEPARATOR)
        except IndexError:
            tags = list()
        else:
            tags = [t.strip() for t in tags if t]

    # Encoding boundary;  Internal filename bytestring --> internal Unicode str
    def _decode_bytestring(bytestring_maybe):
        if bytestring_maybe:
            return enc.decode_(bytestring_maybe)
        return ''

    if timestamp:
        # Set timestamp to None instead of empty string here so that it can be
        # detected and skipped when converting values to the "internal format".
        # Coercing None with 'AW_TIMEDATE' raises a 'AWTypeError' exception,
        # which would happen for every file that do not have a "timestamp"
        # filetags part.
        timestamp = _decode_bytestring(timestamp)
    else:
        timestamp = None

    description = _decode_bytestring(description)
    tags = [_decode_bytestring(t) for t in tags]
    suffix = _decode_bytestring(suffix)

    return FiletagsParts(timestamp, description, tags, suffix)


def follows_filetags_convention(filetags_parts):
    """
    Checks if the given parts constitute a proper "filetags" name.

    Filename parts 'timestamp', 'description' and 'tags' must be present.

    Returns:
        Whether the name parts could make up a name following the "filetags"
        naming convention, as a boolean.
    """
    return bool(
        filetags_parts.timestamp and filetags_parts.description
        and filetags_parts.tags
    )
