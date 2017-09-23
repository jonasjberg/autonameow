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

from core import constants as C


# TODO: [TD0049] Think about defining legal "placeholder fields".
# Might be helpful to define all legal fields (such as `title`, `datetime`,
# `author`, etc.) somewhere and keep references to type coercion wrappers,
# maybe validation and/or formatting functionality; in the field definitions.
#
# NOTE(jonas): This should probably be done where both the Extraction data and
# the Analysis results data is "joined"; the sum total of data available for a
# given file.

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


WeightedMapping = namedtuple('WeightedMapping', ['field', 'probability'])


def todo_func(foo):
    pass


class GenericField(object):
    meowuri_root = C.UNDEFINED_MEOWURI_PART
    meowuri_node = C.MEOWURI_NODE_GENERIC
    meowuri_leaf = C.UNDEFINED_MEOWURI_PART

    @classmethod
    def uri(cls):
        return '{}.{}.{}'.format(cls.meowuri_root.lower(),
                                 cls.meowuri_node.lower(),
                                 cls.meowuri_leaf.lower())

    @classmethod
    def evaluation_function(cls):
        raise NotImplementedError('Must be implemented by inheriting classes.')


# TODO: [TD0090] Complete initial implementation of "generic" fields.
class GenericAuthor(GenericField):
    meowuri_root = 'metadata'
    meowuri_leaf = 'Author'

    @classmethod
    def evaluation_function(cls):
        pass


class GenericCreator(GenericField):
    meowuri_root = 'metadata'
    meowuri_leaf = 'Creator'

    @classmethod
    def evaluation_function(cls):
        pass


class GenericDescription(GenericField):
    meowuri_root = 'metadata'
    meowuri_leaf = 'Description'

    @classmethod
    def evaluation_function(cls):
        pass


class GenericDateCreated(GenericField):
    meowuri_root = 'metadata'
    meowuri_leaf = 'Date_Created'

    @classmethod
    def evaluation_function(cls):
        pass


class GenericDateModified(GenericField):
    meowuri_root = 'metadata'
    meowuri_leaf = 'Date_Modified'

    @classmethod
    def evaluation_function(cls):
        pass


class GenericMimeType(GenericField):
    meowuri_root = 'contents'
    meowuri_leaf = 'Mime_Type'

    @classmethod
    def evaluation_function(cls):
        pass


class GenericProducer(GenericField):
    meowuri_root = 'metadata'
    meowuri_leaf = 'Producer'

    @classmethod
    def evaluation_function(cls):
        pass


class GenericSubject(GenericField):
    meowuri_root = 'metadata'
    meowuri_leaf = 'Subject'

    @classmethod
    def evaluation_function(cls):
        pass


class GenericTags(GenericField):
    meowuri_root = 'metadata'
    meowuri_leaf = 'Tags'

    @classmethod
    def evaluation_function(cls):
        pass


def meowuri_genericfield_map():
    return {klass.uri(): klass
            for klass in GenericField.__subclasses__()}


class NameTemplateField(object):
    # TODO: [TD0049] Remove or implement ..
    def __init__(self, content):
        self._content = content

        self._transforms = {
            Title: todo_func,
            Edition: todo_func
        }

    def transform(self, target_field):
        # TODO: Implement transforming data between field types, if possible.
        target_field_type = type(target_field)
        result = self._transforms[target_field_type](self._content)


class Title(NameTemplateField):
    # TODO: [TD0049] Remove or implement ..

    def __init__(self, content):
        super(Title).__init__(content)

    @classmethod
    def normalize(cls, data):
        data = data.strip(',.:;-_ ')
        data = data.replace('&', 'and')
        data = data.replace("&#8211;", "-")
        return data


class Edition(NameTemplateField):
    # TODO: [TD0049] Remove or implement ..

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
        pass


class Author(NameTemplateField):
    # TODO: [TD0049] Remove or implement ..
    pass


class Creator(NameTemplateField):
    # TODO: [TD0049] Remove or implement ..
    pass


class DateTime(NameTemplateField):
    # TODO: [TD0049] Remove or implement ..
    pass


class Date(NameTemplateField):
    # TODO: [TD0049] Remove or implement ..
    pass


class Description(NameTemplateField):
    # TODO: [TD0049] Remove or implement ..
    pass


class Publisher(NameTemplateField):
    # TODO: [TD0049] Remove or implement ..
    pass


class Tags(NameTemplateField):
    # TODO: [TD0049] Remove or implement ..
    pass


author = Author
date = Date
datetime = DateTime
description = Description
edition = Edition
extension = Extension
publisher = Publisher
tags = Tags
title = Title
