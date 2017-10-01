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


from core import constants as C


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
    meowuri_node = C.UNDEFINED_MEOWURI_PART
    meowuri_leaf = C.UNDEFINED_MEOWURI_PART

    @classmethod
    def uri(cls):
        return '{}.{}.{}'.format(cls.meowuri_root.lower(),
                                 cls.meowuri_node.lower(),
                                 cls.meowuri_leaf.lower())

    @classmethod
    def evaluation_function(cls):
        raise NotImplementedError('Must be implemented by inheriting classes.')


class GenericAuthor(GenericField):
    meowuri_node = 'metadata'
    meowuri_leaf = 'Author'

    @classmethod
    def evaluation_function(cls):
        pass


class GenericCreator(GenericField):
    meowuri_node = 'metadata'
    meowuri_leaf = 'Creator'

    @classmethod
    def evaluation_function(cls):
        pass


class GenericDescription(GenericField):
    meowuri_node = 'metadata'
    meowuri_leaf = 'Description'

    @classmethod
    def evaluation_function(cls):
        pass


class GenericDateCreated(GenericField):
    meowuri_node = 'metadata'
    meowuri_leaf = 'Date_Created'

    @classmethod
    def evaluation_function(cls):
        pass


class GenericDateModified(GenericField):
    meowuri_node = 'metadata'
    meowuri_leaf = 'Date_Modified'

    @classmethod
    def evaluation_function(cls):
        pass


class GenericHealth(GenericField):
    """
    Measure of file corruption/integrity/"health" as a float in range 0-1.
    Where 0 is severely corrupted and 1 is a seemingly valid, intact file.
    """
    meowuri_node = 'contents'
    meowuri_leaf = 'health'

    @classmethod
    def evaluation_function(cls):
        pass


class GenericMimeType(GenericField):
    meowuri_node = 'contents'
    meowuri_leaf = 'Mime_Type'

    @classmethod
    def evaluation_function(cls):
        pass


class GenericProducer(GenericField):
    meowuri_node = 'metadata'
    meowuri_leaf = 'Producer'

    @classmethod
    def evaluation_function(cls):
        pass


class GenericPublisher(GenericField):
    meowuri_node = 'metadata'
    meowuri_leaf = 'Publisher'

    @classmethod
    def evaluation_function(cls):
        pass


class GenericSubject(GenericField):
    meowuri_node = 'metadata'
    meowuri_leaf = 'Subject'

    @classmethod
    def evaluation_function(cls):
        pass


class GenericTags(GenericField):
    meowuri_node = 'metadata'
    meowuri_leaf = 'Tags'

    @classmethod
    def evaluation_function(cls):
        pass


class GenericText(GenericField):
    meowuri_node = 'contents'
    meowuri_leaf = 'text'

    @classmethod
    def evaluation_function(cls):
        pass


class GenericTitle(GenericField):
    meowuri_node = 'metadata'
    meowuri_leaf = 'Title'

    @classmethod
    def evaluation_function(cls):
        pass


def meowuri_genericfield_map():
    return {klass.uri(): klass
            for klass in GenericField.__subclasses__()}
