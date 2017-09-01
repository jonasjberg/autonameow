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

import re

from collections import namedtuple


# Original Dublin Core Metadata Element Set Version 1.1
# Metadata Elements:
#
#   - Title
#   - Creator
#   - Subject
#   - Description
#   - Publisher
#   - Contributor
#   - Date
#   - Type
#   - Format
#   - Identifier
#   - Source
#   - Language
#   - Relation
#   - Coverage
#   - Rights


# TODO: [TD0049]` Think about defining legal "placeholder fields".
# Might be helpful to define all legal fields (such as `title`, `datetime`,
# `author`, etc.) somewhere and keep references to type coercion wrappers,
# maybe validation and/or formatting functionality; in the field definitions.
#
# NOTE(jonas): This should probably be done where both the Extraction data and
# the Analysis results data is "joined"; the sum total of data available for a
# given file.

Weighted = namedtuple('Weighted', ['field', 'probability'])


class NameTemplateField(object):
    def __init__(self, content):
        self._content = content


class Title(NameTemplateField):
    # TODO: Remove or implement ..

    def __init__(self, content):
        super(Title).__init__(content)

    @classmethod
    def normalize(cls, data):
        data = data.strip(',.:;-_ ')
        data = data.replace('&', 'and')
        data = data.replace("&#8211;", "-")
        return data


class Edition(NameTemplateField):
    # TODO: Remove or implement ..

    REPLACE_ORDINALS = []
    for _find, _replace in (
            ('1st', 'first'),        ('2nd', 'second'),
            ('3rd', 'third'),        ('4th', 'fourth'),
            ('5th', 'fifth'),        ('6th', 'sixth'),
            ('7th', 'seventh'),      ('8th', 'eighth'),
            ('9th', 'ninth'),        ('10th', 'tenth'),
            ('11th', 'eleventh'),    ('12th', 'twelfth'),
            ('13th', 'thirteenth'),  ('14th', 'fourteenth'),
            ('15th', 'fifteenth'),   ('16th', 'sixteenth'),
            ('17th', 'seventeenth'), ('18th', 'eighteenth'),
            ('19th', 'nineteenth'),  ('20th', 'twentieth')):
        REPLACE_ORDINALS.append((re.compile(_find, re.IGNORECASE), _replace))

    def __init__(self, content):
        super(Edition).__init__(content)

    @classmethod
    def normalize(cls, edition):
        # Normalize numeric titles to allow for later custom replacements.
        for _find, _replace in cls.REPLACE_ORDINALS:
            edition = _find.sub(_replace, edition)

        return edition


class Extension(NameTemplateField):
    # TODO: Remove or implement ..

    def __init__(self, content):
        super(Extension).__init__(content)

    @classmethod
    def normalize(cls, data):
        # Normalize numeric titles
        for _find, _replace in cls.ORDINALS:
            data = _find.sub(_replace, data)
        return data



class Author(NameTemplateField):
    pass


class DateTime(NameTemplateField):
    pass


class Date(NameTemplateField):
    pass


class Description(NameTemplateField):
    pass


class Publisher(NameTemplateField):
    pass


class Tags(NameTemplateField):
    pass


datetime = DateTime
publisher = Publisher
title = Title
tags = Tags
author = Author
date = Date
description = Description
edition = Edition
extension = Extension
