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
    pass


def split_title_subtitle(full_title):
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
