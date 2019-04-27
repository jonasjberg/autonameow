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

from functools import lru_cache

from core import constants as C
from core.model import MeowURI


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


class GenericField(object):
    meowuri_root = C.MEOWURI_ROOT_GENERIC
    meowuri_child = C.MEOWURI_UNDEFINED_PART
    meowuri_leaf = C.MEOWURI_UNDEFINED_PART

    @classmethod
    def uri(cls):
        assert not isinstance(cls.meowuri_child, list)
        _uri = '{}.{}.{}'.format(cls.meowuri_root.lower(),
                                 cls.meowuri_child.lower(),
                                 cls.meowuri_leaf.lower())
        return MeowURI(_uri)


class GenericAuthor(GenericField):
    meowuri_child = 'metadata'
    meowuri_leaf = 'Author'


class GenericCreator(GenericField):
    meowuri_child = 'metadata'
    meowuri_leaf = 'Creator'


class GenericDescription(GenericField):
    meowuri_child = 'metadata'
    meowuri_leaf = 'Description'


class GenericDateCreated(GenericField):
    meowuri_child = 'metadata'
    meowuri_leaf = 'Date_Created'


class GenericDateModified(GenericField):
    meowuri_child = 'metadata'
    meowuri_leaf = 'Date_Modified'


class GenericEdition(GenericField):
    meowuri_child = 'metadata'
    meowuri_leaf = 'Edition'


class GenericHealth(GenericField):
    """
    Measure of file corruption/integrity/"health" as a float in range 0-1.
    Where 0 is severely corrupted and 1 is a seemingly valid, intact file.
    """
    meowuri_child = 'contents'
    meowuri_leaf = 'health'


class GenericIdentifier(GenericField):
    """
    Unique identifiers like CID, CRID, DOI, GUID, ISBN, ISRC, ISWC, .., etc.
    """
    meowuri_child = 'metadata'
    meowuri_leaf = 'identifier'


class GenericLanguage(GenericField):
    meowuri_child = 'metadata'
    meowuri_leaf = 'language'


class GenericMimeType(GenericField):
    meowuri_child = 'contents'
    meowuri_leaf = 'Mime_Type'


class GenericProducer(GenericField):
    meowuri_child = 'metadata'
    meowuri_leaf = 'Producer'


class GenericPublisher(GenericField):
    meowuri_child = 'metadata'
    meowuri_leaf = 'Publisher'


class GenericSubject(GenericField):
    meowuri_child = 'metadata'
    meowuri_leaf = 'Subject'


class GenericTags(GenericField):
    meowuri_child = 'metadata'
    meowuri_leaf = 'Tags'


class GenericText(GenericField):
    meowuri_child = 'contents'
    meowuri_leaf = 'text'


class GenericTitle(GenericField):
    meowuri_child = 'metadata'
    meowuri_leaf = 'Title'


def get_all_generic_field_klasses():
    return set(GenericField.__subclasses__())


def get_datetime_fields():
    return [
        GenericDateModified, GenericDateCreated
    ]


def get_string_fields():
    return [
        GenericSubject, GenericText, GenericProducer, GenericDescription,
        GenericCreator, GenericAuthor, GenericPublisher, GenericTitle,
        GenericLanguage,
    ]


@lru_cache(maxsize=1)
def _build_field_uri_leaf_to_klass_mapping():
    return {
        klass.uri().leaf: klass
        for klass in get_all_generic_field_klasses()
    }


def get_field_for_uri_leaf(string):
    leaf_to_klass_map = _build_field_uri_leaf_to_klass_mapping()
    return leaf_to_klass_map.get(string)


def get_all_generic_field_uri_leaves():
    """Returns a list of all generic field URI leaves as strings."""
    return [klass.uri().leaf for klass in get_all_generic_field_klasses()]
