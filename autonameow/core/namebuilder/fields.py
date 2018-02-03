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

import datetime
import logging
import re

from core import (
    exceptions,
    types,
)
from util import (
    sanity,
    text
)


log = logging.getLogger(__name__)


class NameTemplateField(object):
    COMPATIBLE_TYPES = (None, )
    MULTIVALUED = None

    @classmethod
    def format(cls, data, *args, **kwargs):
        # TODO: Implement in inheriting classes ..
        log.warning('Called unimplemented "{!s}.format()"'.format(cls.__name__))

    @classmethod
    def as_placeholder(cls):
        return cls.__name__.lower()

    @classmethod
    def type_compatible(cls, type_class):
        if isinstance(type_class, types.MultipleTypes):
            if not cls.MULTIVALUED:
                return False
            return type_class.coercer in cls.COMPATIBLE_TYPES
        else:
            return type_class in cls.COMPATIBLE_TYPES

    def __str__(self):
        # TODO: [TD0140] str() method not working as intended.
        # These classes are mostly not instantiated and used as classes.
        # Calling str() on a class will not call this method, resulting in
        # for instance 'core.namebuilder.fields.Extension' and not 'Extension'.
        return self.__class__.__name__.lower()


class Title(NameTemplateField):
    COMPATIBLE_TYPES = (types.AW_PATHCOMPONENT,
                        types.AW_PATH,
                        types.AW_STRING,
                        types.AW_INTEGER)
    MULTIVALUED = False

    @classmethod
    def normalize(cls, data):
        data = data.strip(',.:;-_ ')
        data = data.replace('&', 'and')
        data = data.replace('&#8211;', '-')
        return data

    @classmethod
    def format(cls, data, *args, **kwargs):
        # TODO: [TD0036] Allow per-field replacements and customization.
        # TODO: [TD0129] Data validation at this point should be made redundant
        if data.get('coercer') in (types.AW_PATHCOMPONENT, types.AW_PATH):
            string = types.force_string(data.get('value'))
            if not string:
                raise exceptions.NameBuilderError(
                    'Unicode string conversion failed for "{!r}"'.format(data)
                )
        elif data.get('coercer') == types.AW_STRING:
            string = data.get('value')
        else:
            string = data.get('value')

        sanity.check_internal_string(string)
        return cls.normalize(string)


class Edition(NameTemplateField):
    COMPATIBLE_TYPES = (types.AW_PATHCOMPONENT,
                        types.AW_PATH,
                        types.AW_STRING,
                        types.AW_INTEGER)
    MULTIVALUED = False

    # TODO: Consolidate with similar in the 'FilenameAnalyzer'.
    REPLACE_ORDINALS = []
    for _find, _replace in (('1st', 'first'),
                            ('2nd', 'second'),
                            ('3rd', 'third'),
                            ('4th', 'fourth'),
                            ('5th', 'fifth'),
                            ('6th', 'sixth'),
                            ('7th', 'seventh'),
                            ('8th', 'eighth'),
                            ('9th', 'ninth'),
                            ('10th', 'tenth'),
                            ('11th', 'eleventh'),
                            ('12th', 'twelfth'),
                            ('13th', 'thirteenth'),
                            ('14th', 'fourteenth'),
                            ('15th', 'fifteenth'),
                            ('16th', 'sixteenth'),
                            ('17th', 'seventeenth'),
                            ('18th', 'eighteenth'),
                            ('19th', 'nineteenth'),
                            ('20th', 'twentieth')):
        REPLACE_ORDINALS.append((re.compile(_find, re.IGNORECASE), _replace))

    @classmethod
    def normalize(cls, edition):
        # TODO: Consolidate with similar in the 'FilenameAnalyzer'.

        # Normalize numeric titles to allow for later custom replacements.
        for _find, _replace in cls.REPLACE_ORDINALS:
            edition = _find.sub(_replace, edition)

        return edition

    @classmethod
    def format(cls, data, *args, **kwargs):
        # TODO: [TD0036] Allow per-field replacements and customization.
        # TODO: [TD0129] Data validation at this point should be made redundant
        if data.get('coercer') in (types.AW_PATHCOMPONENT, types.AW_PATH):
            string = types.force_string(data.get('value'))
            if not string:
                raise exceptions.NameBuilderError(
                    'Unicode string conversion failed for "{!r}"'.format(data)
                )
        elif data.get('coercer') in (types.AW_STRING, types.AW_INTEGER):
            string = types.force_string(data.get('value'))
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
    MULTIVALUED = False

    @classmethod
    def normalize(cls, data):
        pass

    @classmethod
    def format(cls, data, *args, **kwargs):
        # TODO: [TD0129] Data validation at this point should be made redundant
        value = data.get('value')
        coercer = data.get('coercer')
        if coercer:
            string = coercer.format(value)
        else:
            log.warning('{!s} coercer unknown for "{!s}"'.format(cls, value))
            string = types.force_string(value)

        if string is None:
            raise exceptions.NameBuilderError(
                'Unicode string conversion failed for "{!r}"'.format(data)
            )

        return string


class Author(NameTemplateField):
    COMPATIBLE_TYPES = (types.AW_PATHCOMPONENT,
                        types.AW_PATH,
                        types.AW_STRING)
    MULTIVALUED = True

    @classmethod
    def format(cls, data, *args, **kwargs):
        # TODO: [TD0036] Allow per-field replacements and customization.
        # TODO: [TD0129] Data validation at this point should be made redundant
        if isinstance(data.get('value'), list):
            # Multiple authors
            _formatted = []
            for d in data.get('value'):
                if data.get('coercer') in (types.AW_PATHCOMPONENT,
                                           types.AW_PATH):
                    string = types.force_string(d)
                    if not string:
                        raise exceptions.NameBuilderError(
                            'Unicode string conversion failed for '
                            '"{!r}"'.format(data)
                        )
                elif data.get('coercer') == types.AW_STRING:
                    string = d
                else:
                    raise exceptions.NameBuilderError(
                        'Got incompatible data: {!r}'.format(d)
                    )

                sanity.check_internal_string(string)
                _formatted.append(text.format_name(string))

            return ' '.join(sorted(_formatted))
        else:
            # One author
            if data.get('coercer') in (types.AW_PATHCOMPONENT, types.AW_PATH):
                string = types.force_string(data.get('value'))
                if not string:
                    raise exceptions.NameBuilderError(
                        'Unicode string conversion failed for '
                        '"{!r}"'.format(data)
                    )
            elif data.get('coercer') == types.AW_STRING:
                string = data.get('value')
            else:
                raise exceptions.NameBuilderError(
                    'Got incompatible data: {!r}'.format(data)
                )

            sanity.check_internal_string(string)
            return text.format_name(data.get('value'))


class Creator(NameTemplateField):
    COMPATIBLE_TYPES = (types.AW_PATHCOMPONENT,
                        types.AW_PATH,
                        types.AW_STRING,
                        types.AW_INTEGER,
                        types.AW_FLOAT)
    MULTIVALUED = True


class DateTime(NameTemplateField):
    COMPATIBLE_TYPES = (types.AW_DATE,
                        types.AW_TIMEDATE,
                        types.AW_EXIFTOOLTIMEDATE)
    MULTIVALUED = False

    @classmethod
    def format(cls, data, *args, **kwargs):
        # TODO: [TD0129] Data validation at this point should be made redundant
        _value = data.get('value')
        if not _value:
            raise exceptions.NameBuilderError(
                '{!s}.format() got empty data'.format(cls)
            )

        if not isinstance(_value, datetime.datetime):
            raise exceptions.NameBuilderError(
                '{!s}.format() expected data of type "datetime". '
                'Got "{!s}" with value "{!s}"'.format(cls, type(_value), _value)
            )

        c = kwargs.get('config')
        if c:
            _format = c.options['DATETIME_FORMAT']['datetime']
            return formatted_datetime(_value, _format)
        else:
            raise exceptions.NameBuilderError('Unknown "datetime" format')


class Date(NameTemplateField):
    COMPATIBLE_TYPES = (types.AW_DATE,
                        types.AW_TIMEDATE,
                        types.AW_EXIFTOOLTIMEDATE)
    MULTIVALUED = False

    @classmethod
    def format(cls, data, *args, **kwargs):
        # TODO: [TD0129] Data validation at this point should be made redundant
        _value = data.get('value')
        if not _value:
            raise exceptions.NameBuilderError(
                '{!s}.format() got empty data'.format(cls)
            )

        if not isinstance(_value, datetime.datetime):
            raise exceptions.NameBuilderError(
                '{!s}.format() expected data of type "datetime". '
                'Got "{!s}" with value "{!s}"'.format(cls, type(_value), _value)
            )

        c = kwargs.get('config')
        if c:
            datetime_format = c.options['DATETIME_FORMAT']['date']
            return formatted_datetime(_value, datetime_format)
        else:
            raise exceptions.NameBuilderError('Unknown "date" format')


class Description(NameTemplateField):
    COMPATIBLE_TYPES = (types.AW_PATHCOMPONENT,
                        types.AW_PATH,
                        types.AW_STRING,
                        types.AW_INTEGER,
                        types.AW_FLOAT)
    MULTIVALUED = False

    @classmethod
    def format(cls, data, *args, **kwargs):
        value = data.get('value')
        return types.force_string(value)


class Publisher(NameTemplateField):
    COMPATIBLE_TYPES = (types.AW_PATHCOMPONENT,
                        types.AW_PATH,
                        types.AW_STRING,
                        types.AW_INTEGER)
    MULTIVALUED = False

    @classmethod
    def format(cls, data, *args, **kwargs):
        # TODO: [TD0036] Allow per-field replacements and customization.

        _candidates = dict()

        c = kwargs.get('config')
        if c:
            _options = c.get(['NAME_TEMPLATE_FIELDS', 'publisher'])
            if _options:
                _candidates = _options.get('candidates', {})

        # TODO: [TD0152] Fix too many replacements applied? Stop after first?
        _formatted = data.get('value')
        for repl, patterns in _candidates.items():
            for pattern in patterns:
                _formatted = pattern.sub(repl, _formatted)

        return _formatted


class Tags(NameTemplateField):
    COMPATIBLE_TYPES = (types.AW_PATHCOMPONENT,
                        types.AW_PATH,
                        types.AW_STRING,
                        types.AW_INTEGER)
    MULTIVALUED = True

    @classmethod
    def format(cls, data, *args, **kwargs):
        _value = data.get('value')
        _tag_list = types.listof(types.AW_STRING)(_value)

        # TODO: [TD0129] Is this kind of double-double-check really necessary..?
        sanity.check_isinstance(_tag_list, list)
        for t in _tag_list:
            sanity.check_isinstance(t, str)

        if len(_tag_list) == 1:
            # Single tag doesn't need to be joined.
            return _tag_list[0]

        c = kwargs.get('config')
        if c:
            sep = c.options['FILETAGS_OPTIONS']['between_tag_separator']
            sanity.check_internal_string(sep)
            return sep.join(_tag_list)
        else:
            raise exceptions.NameBuilderError('Unknown "between_tag_separator"')


class Time(NameTemplateField):
    COMPATIBLE_TYPES = (types.AW_TIMEDATE,
                        types.AW_EXIFTOOLTIMEDATE)
    MULTIVALUED = False

    @classmethod
    def format(cls, data, *args, **kwargs):
        _value = data.get('value')
        c = kwargs.get('config')
        if c:
            datetime_format = c.options['DATETIME_FORMAT']['time']
            return formatted_datetime(_value, datetime_format)
        else:
            raise exceptions.NameBuilderError('Unknown "time" format')


class Year(NameTemplateField):
    COMPATIBLE_TYPES = (types.AW_DATE,
                        types.AW_TIMEDATE,
                        types.AW_EXIFTOOLTIMEDATE)
    MULTIVALUED = False

    @classmethod
    def format(cls, data, *args, **kwargs):
        datetime_format = '%Y'
        return formatted_datetime(data.get('value'), datetime_format)


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


def formatted_datetime(datetime_object, format_string):
    sanity.check_isinstance(datetime_object, datetime.datetime)
    return datetime_object.strftime(format_string)
