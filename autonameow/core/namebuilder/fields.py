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

from core import (
    exceptions,
    types,
)
from core.util import (
    sanity,
    textutils
)


class NameTemplateField(object):
    COMPATIBLE_TYPES = (None, )

    def __init__(self, content):
        self._content = content

        self._transforms = {
            Title: None,  # TODO: Function?
            Edition: None,  # TODO: Function?
        }

    def transform(self, target_field):
        # TODO: Implement transforming data between field types, if possible.
        # target_field_type = type(target_field)
        # result = self._transforms[target_field_type](self._content)
        pass

    @classmethod
    def format(cls, data):
        # TODO: Implement in inheriting classes ..
        pass

    @classmethod
    def as_placeholder(cls):
        return cls.__name__.lower()

    @classmethod
    def type_compatible(cls, type_class):
        return type_class in cls.COMPATIBLE_TYPES

    def __str__(self):
        return self.__class__.__name__.lower()


class Title(NameTemplateField):
    COMPATIBLE_TYPES = (types.AW_PATHCOMPONENT,
                        types.AW_PATH,
                        types.AW_STRING,
                        types.AW_INTEGER)

    def __init__(self, content):
        super(Title).__init__(content)

    @classmethod
    def normalize(cls, data):
        data = data.strip(',.:;-_ ')
        data = data.replace('&', 'and')
        data = data.replace('&#8211;', '-')
        data = data.replace(' - ', '')
        return data

    @classmethod
    def format(cls, data):
        # TODO: [TD0036] Allow per-field replacements and customization.
        if data.coercer in (types.AW_PATHCOMPONENT, types.AW_PATH):
            string = types.force_string(data.value)
            if not string:
                raise exceptions.NameBuilderError(
                    'Unicode string conversion failed for "{!r}"'
                )
        elif data.coercer == types.AW_STRING:
            string = data.value
        else:
            string = data.value

        sanity.check_internal_string(string)
        return cls.normalize(string)


class Edition(NameTemplateField):
    COMPATIBLE_TYPES = (types.AW_PATHCOMPONENT,
                        types.AW_PATH,
                        types.AW_STRING,
                        types.AW_INTEGER)

    # TODO: Consolidate with similar in the 'FilenameAnalyzer'.
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
        # TODO: Consolidate with similar in the 'FilenameAnalyzer'.

        # Normalize numeric titles to allow for later custom replacements.
        for _find, _replace in cls.REPLACE_ORDINALS:
            edition = _find.sub(_replace, edition)

        return edition

    @classmethod
    def format(cls, data):
        # TODO: [TD0036] Allow per-field replacements and customization.
        if data.coercer in (types.AW_PATHCOMPONENT, types.AW_PATH):
            string = types.force_string(data.value)
            if not string:
                raise exceptions.NameBuilderError(
                    'Unicode string conversion failed for "{!r}"'
                )
        elif data.coercer in (types.AW_STRING, types.AW_INTEGER):
            string = data.value
        else:
            raise exceptions.NameBuilderError(
                'Got incompatible data: {!r}'.format(data)
            )

        sanity.check_internal_string(string)
        return '{}E'.format(string)


class Extension(NameTemplateField):
    COMPATIBLE_TYPES = (types.AW_PATHCOMPONENT,
                        types.AW_PATH,
                        types.AW_STRING,
                        types.AW_MIMETYPE)

    def __init__(self, content):
        super(Extension).__init__(content)

    @classmethod
    def normalize(cls, data):
        pass


class Author(NameTemplateField):
    COMPATIBLE_TYPES = (types.AW_PATHCOMPONENT,
                        types.AW_PATH,
                        types.AW_STRING)

    @classmethod
    def format(cls, data):
        # TODO: [TD0036] Allow per-field replacements and customization.

        if isinstance(data, list):
            # Multiple authors
            _formatted = []
            for d in data:
                if d.coercer in (types.AW_PATHCOMPONENT, types.AW_PATH):
                    string = types.force_string(d.value)
                    if not string:
                        raise exceptions.NameBuilderError(
                            'Unicode string conversion failed for "{!r}"'
                        )
                elif d.coercer == types.AW_STRING:
                    string = d.value
                else:
                    raise exceptions.NameBuilderError(
                        'Got incompatible data: {!r}'.format(d)
                    )

                sanity.check_internal_string(string)
                _formatted.append(
                    textutils.format_name_lastname_initials(string)
                )

            return ' '.join(_formatted)
        else:
            # One author
            return textutils.format_name_lastname_initials(data.value)


class Creator(NameTemplateField):
    COMPATIBLE_TYPES = (types.AW_PATHCOMPONENT,
                        types.AW_PATH,
                        types.AW_STRING,
                        types.AW_INTEGER,
                        types.AW_FLOAT)


class DateTime(NameTemplateField):
    COMPATIBLE_TYPES = (types.AW_DATE,
                        types.AW_TIMEDATE,
                        types.AW_EXIFTOOLTIMEDATE,
                        types.AW_PYPDFTIMEDATE)
    pass


class Date(NameTemplateField):
    COMPATIBLE_TYPES = (types.AW_DATE,
                        types.AW_TIMEDATE,
                        types.AW_EXIFTOOLTIMEDATE,
                        types.AW_PYPDFTIMEDATE)
    pass


class Description(NameTemplateField):
    COMPATIBLE_TYPES = (types.AW_PATHCOMPONENT,
                        types.AW_PATH,
                        types.AW_STRING,
                        types.AW_INTEGER,
                        types.AW_FLOAT)
    pass


class Publisher(NameTemplateField):
    COMPATIBLE_TYPES = (types.AW_PATHCOMPONENT,
                        types.AW_PATH,
                        types.AW_STRING,
                        types.AW_INTEGER)

    @classmethod
    def format(cls, data):
        # TODO: [TD0036] Allow per-field replacements and customization.
        pass


class Tags(NameTemplateField):
    COMPATIBLE_TYPES = (types.AW_PATHCOMPONENT,
                        types.AW_PATH,
                        types.AW_STRING,
                        types.AW_INTEGER)
    pass


def format_string_placeholders(format_string):
    """
    Gets the format string placeholder fields from a text string.

    The text "{foo} mjao baz {bar}" would return ['foo', 'bar'].

    Args:
        format_string: Format string to get placeholders from.

    Returns:
        Any format string placeholder fields as a list of unicode strings.
    """
    if not isinstance(format_string, str):
        raise TypeError('Expected "format_string" to be of type str')
    if not format_string.strip():
        return []

    return re.findall(r'{(\w+)}', format_string)


def available_nametemplatefield_classes():
    """
    Returns: All available name template field classes as a list of classes.
    """
    return [k for k in globals()['NameTemplateField'].__subclasses__()]


NAMETEMPLATEFIELD_CLASS_STRING_LOOKUP = {
    k.as_placeholder(): k for k in available_nametemplatefield_classes()
}

# This defines legal name template fields.
NAMETEMPLATEFIELD_PLACEHOLDER_STRINGS = [
    f.as_placeholder() for f in available_nametemplatefield_classes()
]


def is_valid_template_field(template_field):
    """
    Checks whether the given string is a legal name template placeholder field.

    Args:
        template_field: The field to test as type str.

    Returns:
        True if the given string is a legal name template field, else False.
    """
    return nametemplatefield_class_from_string(template_field) is not None


def nametemplatefield_class_from_string(string):
    """
    Get a name template field class from a Unicode string.

    Provides mapping strings used in user-defined format strings to classes.
    String examples:  "title", "author", etc.

    Args:
        string: The string representation of the name template field class.

    Returns: The associated name template field class or None.
    """
    if string and isinstance(string, str):
        s = string.lower().strip()
        return NAMETEMPLATEFIELD_CLASS_STRING_LOOKUP.get(s, None)
    return None


def nametemplatefield_classes_in_formatstring(format_string):
    """
    Gets any name template field classes from format string.

    Args:
        format_string: The format string to search as a Unicode string.
                       Example: "[{datetime}] foo -- {author} bar.{extension}"

    Returns:
        Any name template field classes contained in the string as a list of
        classes, or an empty list if none are found.
    """
    if not format_string or not isinstance(format_string, str):
        return []
    if not format_string.strip():
        return []

    placeholders = format_string_placeholders(format_string)
    return [nametemplatefield_class_from_string(p) for p in placeholders]
