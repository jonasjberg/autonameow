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

import datetime
import logging

from core import exceptions
from util import coercers
from util import sanity
from util import text


log = logging.getLogger(__name__)


# TODO: [TD0154] Add "incrementing counter" placeholder field
# TODO: [TD0191] Add new 'subtitle' placeholder field.
# TODO: [TD0196] Allow user to define maximum lengths for new names.
# TODO: [TD0197] Template field-specific length limits and trimming.


class NameTemplateField(object):
    COMPATIBLE_TYPES = (None, )
    MULTIVALUED = None

    @classmethod
    def format(cls, data, *args, **kwargs):
        # TODO: Implement in inheriting classes ..
        log.warning('Called unimplemented "%s.format()"', cls.__name__)

    @classmethod
    def type_compatible(cls, coercer, multivalued):
        assert not isinstance(coercer, coercers.MultipleTypes), (
            'Used in confused old (incomplete) implementation'
        )
        return bool(
            multivalued == cls.MULTIVALUED
            and coercer in cls.COMPATIBLE_TYPES
        )

    def as_placeholder(self):
        return self.__class__.__name__.lower().lstrip('_')

    def __str__(self):
        return '{{{}}}'.format(self.as_placeholder())

    def __repr__(self):
        return 'NameTemplateField<{}>'.format(self.__class__.__name__.lstrip('_'))

    def __eq__(self, other):
        return self.__class__ == other.__class__

    def __hash__(self):
        return hash(self.__class__)


class _Title(NameTemplateField):
    COMPATIBLE_TYPES = (coercers.AW_PATHCOMPONENT,
                        coercers.AW_PATH,
                        coercers.AW_STRING,
                        coercers.AW_INTEGER)
    MULTIVALUED = False

    @classmethod
    def format(cls, databundle, *args, **kwargs):
        # TODO: [TD0129] Data validation at this point should be made redundant
        value = databundle.value
        coercer = databundle.coercer
        sanity.check_isinstance(coercer, coercers.BaseCoercer)

        if coercer in (coercers.AW_PATHCOMPONENT, coercers.AW_PATH):
            str_value = coercers.force_string(value)
            if not str_value:
                raise exceptions.NameBuilderError(
                    'Unicode string conversion failed for "{!r}"'.format(databundle)
                )
        elif coercer == coercers.AW_STRING:
            str_value = value
        else:
            str_value = value

        sanity.check_internal_string(str_value)
        formatted_value = str_value.strip(',.:;-_ ')
        # TODO: [TD0036] Allow per-field replacements and customization.
        return formatted_value


class _Edition(NameTemplateField):
    COMPATIBLE_TYPES = (coercers.AW_PATHCOMPONENT,
                        coercers.AW_PATH,
                        coercers.AW_STRING,
                        coercers.AW_INTEGER)
    MULTIVALUED = False

    @classmethod
    def format(cls, databundle, *args, **kwargs):
        # TODO: [TD0129] Data validation at this point should be made redundant
        value = databundle.value
        coercer = databundle.coercer
        sanity.check_isinstance(coercer, coercers.BaseCoercer)

        if coercer in (coercers.AW_PATHCOMPONENT, coercers.AW_PATH):
            str_value = coercers.force_string(value)
            if not str_value:
                raise exceptions.NameBuilderError(
                    'Unicode string conversion failed for "{!r}"'.format(databundle)
                )
        elif coercer in (coercers.AW_STRING, coercers.AW_INTEGER):
            str_value = coercers.force_string(value)
        else:
            raise exceptions.NameBuilderError(
                'Got incompatible data: {!r}'.format(databundle)
            )

        sanity.check_internal_string(str_value)
        # TODO: [TD0036] Allow per-field replacements and customization.
        formatted_value = '{}E'.format(str_value)
        return formatted_value


class _Extension(NameTemplateField):
    COMPATIBLE_TYPES = (coercers.AW_PATHCOMPONENT,
                        coercers.AW_PATH,
                        coercers.AW_STRING,
                        coercers.AW_MIMETYPE)
    MULTIVALUED = False

    @classmethod
    def format(cls, databundle, *args, **kwargs):
        # TODO: [TD0129] Data validation at this point should be made redundant
        value = databundle.value
        coercer = databundle.coercer
        sanity.check_isinstance(coercer, coercers.BaseCoercer)

        if not value:
            # Might be 'NullMIMEType', which evaluates False here.
            return ''

        if coercer:
            formatted_value = coercer.format(value)
        else:
            log.warning('%s coercer unknown for "%s"', cls, value)
            formatted_value = coercers.force_string(value)

        if formatted_value is None:
            raise exceptions.NameBuilderError(
                'Unicode string conversion failed for "{!r}"'.format(databundle)
            )
        return formatted_value


class _Author(NameTemplateField):
    COMPATIBLE_TYPES = (coercers.AW_PATHCOMPONENT,
                        coercers.AW_PATH,
                        coercers.AW_STRING)
    MULTIVALUED = True

    @classmethod
    def format(cls, databundle, *args, **kwargs):
        # TODO: [TD0036] Allow per-field replacements and customization.
        value = databundle.value
        coercer = databundle.coercer
        sanity.check_isinstance(coercer, coercers.BaseCoercer)

        # TODO: Coercer references that are passed around are class INSTANCES!
        # TODO: [hack] Fix 'coercers.listof()' expects classes!
        coercer = coercers.listof(coercer)
        str_list_value = coercer(value)
        sanity.check_isinstance(str_list_value, list)

        # TODO: [TD0129] Data validation at this point should be made redundant
        if any(not s.strip() for s in str_list_value):
            raise exceptions.NameBuilderError(
                'Unicode string coercion resulted in empty (or whitespace) '
                'string for data "{!r}"'.format(databundle)
            )
        formatted_names = list()
        for author in str_list_value:
            sanity.check_internal_string(author)
            formatted_names.append(text.format_name(author))

        formatted_value = ' '.join(sorted(formatted_names))
        return formatted_value


class _Creator(NameTemplateField):
    COMPATIBLE_TYPES = (coercers.AW_PATHCOMPONENT,
                        coercers.AW_PATH,
                        coercers.AW_STRING,
                        coercers.AW_INTEGER,
                        coercers.AW_FLOAT)
    MULTIVALUED = True


class _DateTime(NameTemplateField):
    COMPATIBLE_TYPES = (coercers.AW_DATE,
                        coercers.AW_TIMEDATE,
                        coercers.AW_EXIFTOOLTIMEDATE)
    MULTIVALUED = False

    @classmethod
    def format(cls, databundle, *args, **kwargs):
        # TODO: [TD0129] Data validation at this point should be made redundant
        value = databundle.value
        if not value:
            raise exceptions.NameBuilderError(
                '{!s}.format() got empty data'.format(cls)
            )

        if not isinstance(value, datetime.datetime):
            raise exceptions.NameBuilderError(
                '{!s}.format() expected data of type "datetime". '
                'Got "{!s}" with value "{!s}"'.format(cls, type(value), value)
            )

        c = kwargs.get('config')
        if c:
            datetime_format = c.options['DATETIME_FORMAT']['datetime']
            formatted_value = formatted_datetime(value, datetime_format)
            return formatted_value
        else:
            raise exceptions.NameBuilderError('Unknown "datetime" format')


class _Date(NameTemplateField):
    COMPATIBLE_TYPES = (coercers.AW_DATE,
                        coercers.AW_TIMEDATE,
                        coercers.AW_EXIFTOOLTIMEDATE)
    MULTIVALUED = False

    @classmethod
    def format(cls, databundle, *args, **kwargs):
        # TODO: [TD0129] Data validation at this point should be made redundant
        value = databundle.value
        if not value:
            raise exceptions.NameBuilderError(
                '{!s}.format() got empty data'.format(cls)
            )

        if not isinstance(value, datetime.datetime):
            raise exceptions.NameBuilderError(
                '{!s}.format() expected data of type "datetime". '
                'Got "{!s}" with value "{!s}"'.format(cls, type(value), value)
            )

        c = kwargs.get('config')
        if c:
            datetime_format = c.options['DATETIME_FORMAT']['date']
            formatted_value = formatted_datetime(value, datetime_format)
            return formatted_value
        else:
            raise exceptions.NameBuilderError('Unknown "date" format')


class _Description(NameTemplateField):
    COMPATIBLE_TYPES = (coercers.AW_PATHCOMPONENT,
                        coercers.AW_PATH,
                        coercers.AW_STRING,
                        coercers.AW_INTEGER,
                        coercers.AW_FLOAT)
    MULTIVALUED = False

    @classmethod
    def format(cls, databundle, *args, **kwargs):
        value = databundle.value
        formatted_value = coercers.force_string(value)
        return formatted_value


class _Publisher(NameTemplateField):
    COMPATIBLE_TYPES = (coercers.AW_PATHCOMPONENT,
                        coercers.AW_PATH,
                        coercers.AW_STRING,
                        coercers.AW_INTEGER)
    MULTIVALUED = False

    @classmethod
    def format(cls, databundle, *args, **kwargs):
        # TODO: [TD0036] Allow per-field replacements and customization.

        candidates = dict()

        # TODO: [TD0174] Don't do field value replacements here!
        c = kwargs.get('config')
        if c:
            name_template_field_options = c.get(['NAME_TEMPLATE_FIELDS', 'publisher'])
            if name_template_field_options:
                candidates = name_template_field_options.get('candidates', {})

        # TODO: [TD0152] Fix too many replacements applied? Stop after first?
        value = databundle.value
        sanity.check_internal_string(value)

        formatted_value = value
        for replacement, patterns in candidates.items():
            for pattern in patterns:
                formatted_value = pattern.sub(replacement, formatted_value)

        return formatted_value


class _Tags(NameTemplateField):
    COMPATIBLE_TYPES = (coercers.AW_PATHCOMPONENT,
                        coercers.AW_PATH,
                        coercers.AW_STRING,
                        coercers.AW_INTEGER)
    MULTIVALUED = True

    @classmethod
    def format(cls, databundle, *args, **kwargs):
        value = databundle.value
        str_list_value = coercers.listof(coercers.AW_STRING)(value)

        # TODO: [TD0129] Is this kind of double-double-check really necessary..?
        sanity.check_isinstance(str_list_value, list)
        for t in str_list_value:
            sanity.check_isinstance(t, str)

        if len(str_list_value) == 1:
            # Single tag doesn't need to be joined.
            return str_list_value[0]

        c = kwargs.get('config')
        if c:
            sep = c.options['FILETAGS_OPTIONS']['between_tag_separator']
            sanity.check_internal_string(sep)
            formatted_value = sep.join(str_list_value)
            return formatted_value
        else:
            raise exceptions.NameBuilderError('Unknown "between_tag_separator"')


class _Time(NameTemplateField):
    COMPATIBLE_TYPES = (coercers.AW_TIMEDATE,
                        coercers.AW_EXIFTOOLTIMEDATE)
    MULTIVALUED = False

    @classmethod
    def format(cls, databundle, *args, **kwargs):
        value = databundle.value
        c = kwargs.get('config')
        if c:
            datetime_format = c.options['DATETIME_FORMAT']['time']
            formatted_value = formatted_datetime(value, datetime_format)
            return formatted_value
        else:
            raise exceptions.NameBuilderError('Unknown "time" format')


class _Year(NameTemplateField):
    COMPATIBLE_TYPES = (coercers.AW_DATE,
                        coercers.AW_TIMEDATE,
                        coercers.AW_EXIFTOOLTIMEDATE)
    MULTIVALUED = False

    @classmethod
    def format(cls, databundle, *args, **kwargs):
        datetime_format = '%Y'
        value = databundle.value
        formatted_value = formatted_datetime(value, datetime_format)
        return formatted_value


def available_nametemplatefield_classes():
    """
    Returns: All available name template field classes as a list of classes.
    """
    # NOTE(jonas): Classes are instantiated here.
    return [k() for k in globals()['NameTemplateField'].__subclasses__()]


NAMETEMPLATEFIELD_CLASS_STRING_LOOKUP = {
    k.as_placeholder(): k for k in available_nametemplatefield_classes()
}

# This defines legal name template fields.
NAMETEMPLATEFIELD_PLACEHOLDER_STRINGS = [
    f.as_placeholder() for f in available_nametemplatefield_classes()
]


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


def is_valid_template_field(template_field):
    """
    Checks whether the given string is a legal name template placeholder field.

    Args:
        template_field: The field to test as type str.

    Returns:
        True if the given string is a legal name template field, else False.
    """
    return nametemplatefield_class_from_string(template_field) is not None


def formatted_datetime(datetime_object, format_string):
    sanity.check_isinstance(datetime_object, datetime.datetime)
    return datetime_object.strftime(format_string)


# Singletons for actual use.
Author = _Author()
Creator = _Creator()
Date = _Date()
DateTime = _DateTime()
Description = _Description()
Edition = _Edition()
Extension = _Extension()
Publisher = _Publisher()
Tags = _Tags()
Title = _Title()
Time = _Time()
