# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2019 Jonas Sjöberg <autonameow@jonasjberg.com>
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
considered to follow the filetags convention. The 'extension' is optional.
"""

import re
from collections import namedtuple

from extractors.base import BaseMetadataExtractor
from util import coercers


# TODO: [TD0043] Fetch values from the active configuration.
BETWEEN_TAG_SEPARATOR = ' '
FILENAME_TAG_SEPARATOR = ' -- '


FiletagsParts = namedtuple('FiletagsParts', 'timestamp description tags')


class FiletagsExtractor(BaseMetadataExtractor):
    HANDLES_MIME_TYPES = ['*/*']
    IS_SLOW = False

    def __init__(self):
        super().__init__()

    def extract(self, fileobject, **kwargs):
        return self._get_metadata(fileobject)

    def _get_metadata(self, fileobject):
        prefix = coercers.force_string(fileobject.basename_prefix)
        raw_metadata = self._get_raw_metadata(prefix)

        suffix = coercers.force_string(fileobject.basename_suffix)
        raw_metadata['extension'] = suffix

        metadata = self._to_internal_format(raw_metadata)
        if 'tags' in metadata:
            # NOTE(jonas): Assume that consistent output by sorting outweigh
            #              users that would like to keep the order unchanged ..
            metadata['tags'].sort()

        return metadata

    def _get_raw_metadata(self, basename_prefix):
        parts = split_basename_prefix_into_filetags_parts(basename_prefix)
        follows_convention = follows_filetags_convention(parts)

        raw_metadata = dict(parts._asdict())
        raw_metadata['follows_filetags_convention'] = follows_convention

        # TODO: [hack] The 'timestamp' can be either only a date or a date AND
        #       time.. For now just copy the same value to both places and let
        #       the coercion fail for one of them ..
        if 'timestamp' in raw_metadata:
            raw_metadata['date'] = raw_metadata['timestamp']
            raw_metadata['datetime'] = raw_metadata['timestamp']
            del raw_metadata['timestamp']

        return raw_metadata

    def _to_internal_format(self, raw_metadata):
        coerced_metadata = dict()

        for field, value in raw_metadata.items():
            if value is None:
                # Values of 'timestamp' and 'description' are None if missing.
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


RE_FILENAMEPART_ISODATE = re.compile(r'''
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


def split_basename_prefix_into_filetags_parts(
        basename_prefix,
        sep_between_tags=BETWEEN_TAG_SEPARATOR,
        sep_tags_start=FILENAME_TAG_SEPARATOR
    ):
    """
    Splits a "basename prefix" into "filetags" parts.

    Args:
        basename_prefix (str): Basename without any file extensions.
        sep_between_tags (str): Separator between individual tags.
        sep_tags_start (str): Separator between description and tags.

    Returns:
        Any identified parts as a named tuple with 4 elements;
        'timestamp', 'description', 'tags', where 'tags' is a
        list of Unicode strings, others plain Unicode strings.
    """
    assert isinstance(basename_prefix, str)
    assert isinstance(sep_tags_start, str)
    assert isinstance(sep_between_tags, str)

    # This is the filename *WITHOUT* any file extension(s).
    filename = basename_prefix.strip()

    # Set timestamp to None instead of empty string here so that it can be
    # detected and skipped when converting values to the "internal format".
    # Coercing None with 'AW_TIMEDATE' raises a 'AWTypeError' exception,
    # which would happen for every file that do not have a "timestamp"
    # filetags part.
    timestamp = None
    tags = list()
    description = ''

    matched_isodate_part = RE_FILENAMEPART_ISODATE.match(filename)
    if matched_isodate_part:
        timestamp = matched_isodate_part.group(0)
        filename = filename.lstrip(timestamp)

    if re.findall(sep_tags_start, filename):
        # TODO(jonas): Handle case with multiple "sep_between_tags" better?
        split_by_sep_tags_start = re.split(sep_tags_start, filename, 1)
        description = split_by_sep_tags_start[0].strip()
        try:
            tags_part = split_by_sep_tags_start[1]
        except IndexError:
            pass
        else:
            tags = [t.strip() for t in tags_part.split(sep_between_tags) if t]
    else:
        # Did not find any tag separator.
        if filename:
            description = filename.strip()

    return FiletagsParts(timestamp, description, tags)


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
