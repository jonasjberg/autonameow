# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg <autonameow@jonasjberg.com>
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

import re


# TODO: [TD0191] Detect and extract subtitles from titles
# TODO: [TD0192] Detect and extract editions from titles


# TODO: Handle incorrect metadata with authors embedded in title;
#       Title   : Student Solutions Manual [To] Introduction To Statistics & Data Analysis, , Roxy Peck, Jay Devore
#       Authors : ['Roxy Peck', 'Michael Allwood', 'Jay L. Devore']


def unpack_field_value(todo):
    #
    #   URI:  extractor.metadata.exiftool.XMP:Rights
    # VALUE:  ""Copyright © 2012 "
    #
    # Should unpack to a "date_created" (or similar) with value 2012.
    #
    #   URI:  any title or maybe not specified?
    # VALUE:  "Python Data Science Essentials: Become an efficient data science practitioner by understanding Python's key concepts 2nd Edition.pdf"
    # Should unpack to unpacked = {
    #     'edition': '2',
    #     'title': 'Python Data Science Essentials',
    #     'subtitle': "Become an efficient data science practitioner by understanding Python's key concepts",
    # }
    #
    #   URI:  extractor.metadata.exiftool.XMP:Rights
    # VALUE:  "Copyright © 2018 by Gibson Publishing Inc."
    # Should unpack to unpacked = {
    #     'date_created': '2018',
    #     'publisher': 'Gibson Publishing Inc.',
    # }
    #
    #   URI:  extractor.metadata.exiftool.XMP:Title
    # VALUE:  "Essential K# 7.0, Sixth Edition"
    # Should unpack to unpacked = {
    #     'edition': '6',
    #     'title': 'Essential K# 7.0',
    # }
    #
    #   URI:  extractor.metadata.exiftool.XMP:Creator
    # VALUE:  ['Cats Publishing', 'Jamie Forests']
    # Should unpack to unpacked = {
    #     'author': 'Jamie Forests',
    #     'publisher': 'Cats Publishing',
    # }
    #
    #   URI:  extractor.metadata.exiftool.Palm:Rights
    # VALUE:  "Copyright &#169; 2017 Gibson Education, Inc."
    # Should unpack to unpacked = {
    #     'date_created': '2017',
    #     'publisher': 'Gibson',
    # }
    #
    #   URI:  Ebook Metadata Title
    # VALUE:  'Practical Kibble Sight With CatVision / Gibson Sjöberg, ... [Et Al.]'
    # Should unpack to unpacked = {
    #     'author': 'Gibson Sjöberg',
    #     'title': 'Practical Kibble Sight With CatVision',
    # }
    #
    pass


def split_title_subtitle(full_title):
    # TODO: Maybe allow multiple subtitles, stored in a list?
    assert isinstance(full_title, str)

    RE_SEPARATORS = r'[;:-]'
    RE_TRAILING_SEPARATORS = r'[;:-]$'

    parts = re.split(RE_SEPARATORS, full_title)
    stripped_parts = [p.strip() for p in parts]

    if len(stripped_parts) == 1:
        return stripped_parts[0], ''

    if len(stripped_parts) > 2:
        # Pluck the subtitle from 'stripped_parts'
        subtitle = stripped_parts[-1]
        del stripped_parts[-1]

        # Remove the subtitle from the full title and clean it up.
        title = full_title.replace(subtitle, '').strip()
        title_without_trailing_seps = re.sub(RE_TRAILING_SEPARATORS, '', title)

        return title_without_trailing_seps, subtitle

    return stripped_parts
