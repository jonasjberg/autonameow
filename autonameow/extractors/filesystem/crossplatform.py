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

import os
from datetime import datetime

from core import types
from core.model import WeightedMapping
from core.namebuilder import fields
from extractors import BaseExtractor


class CrossPlatformFileSystemExtractor(BaseExtractor):
    HANDLES_MIME_TYPES = ['*/*']
    MEOWURI_LEAF = 'xplat'
    IS_SLOW = False

    FIELD_LOOKUP = {
        'abspath.full': {'coercer': types.AW_PATH, 'multivalued': False},
        'basename.full': {
            'coercer': types.AW_PATHCOMPONENT,
            'multivalued': False
        },
        'basename.extension': {
            'coercer': types.AW_PATHCOMPONENT,
            'multivalued': False,
            'mapped_fields': [
                WeightedMapping(fields.Extension, probability=1),
            ],
        },
        'basename.suffix': {
            'coercer': types.AW_PATHCOMPONENT,
            'multivalued': False,
            'mapped_fields': [
                WeightedMapping(fields.Extension, probability=1),
            ]
        },
        'basename.prefix': {
            'coercer': types.AW_PATHCOMPONENT,
            'multivalued': False,
        },
        'pathname.full': {'coercer': types.AW_PATH, 'multivalued': False},
        'pathname.parent': {'coercer': types.AW_PATH, 'multivalued': False},
        'contents.mime_type': {
            'coercer': types.AW_MIMETYPE,
            'multivalued': False,
            'mapped_fields': [
                WeightedMapping(fields.Extension, probability=1),
            ],
            'generic_field': 'mime_type'
        },
        'date_accessed': {
            'coercer': types.AW_TIMEDATE,
            'multivalued': False,
            'mapped_fields': [
                WeightedMapping(fields.Date, probability=0.1),
                WeightedMapping(fields.DateTime, probability=0.1),
            ]
        },
        'date_created': {
            'coercer': types.AW_TIMEDATE,
            'multivalued': False,
            'mapped_fields': [
                WeightedMapping(fields.Date, probability=1),
                WeightedMapping(fields.DateTime, probability=1),
            ],
            'generic_field': 'date_created'
        },
        'date_modified': {
            'coercer': types.AW_TIMEDATE,
            'multivalued': False,
            'mapped_fields': [
                WeightedMapping(fields.Date, probability=0.25),
                WeightedMapping(fields.DateTime, probability=0.25),
            ],
            'generic_field': 'date_modified'
        }
    }

    def __init__(self):
        super(CrossPlatformFileSystemExtractor, self).__init__()

    def extract(self, fileobject, **kwargs):
        _datasources = [
            ('abspath.full', fileobject.abspath),
            ('basename.full', fileobject.filename),
            ('basename.extension', fileobject.basename_suffix),
            ('basename.suffix', fileobject.basename_suffix),
            ('basename.prefix', fileobject.basename_prefix),
            ('pathname.full', fileobject.pathname),
            ('pathname.parent', fileobject.pathparent),
            ('contents.mime_type', fileobject.mime_type)
        ]

        out = dict()
        for _uri, _source in _datasources:
            _coerced_data = self.coerce_field_value(_uri, _source)
            if _coerced_data is not None:
                out[_uri] = _coerced_data

        try:
            access_time = _get_access_time(fileobject.abspath)
            create_time = _get_create_time(fileobject.abspath)
            modify_time = _get_modify_time(fileobject.abspath)
        except OSError as e:
            self.log.error('Unable to get timestamps from filesystem:'
                           ' {!s}'.format(e))
        else:
            _coerced_access_time = self.coerce_field_value('date_accessed',
                                                           access_time)
            if _coerced_access_time:
                out['date_accessed'] = _coerced_access_time

            _coerced_create_time = self.coerce_field_value('date_created',
                                                           create_time)
            if _coerced_create_time:
                out['date_created'] = _coerced_create_time

            _coerced_modify_time = self.coerce_field_value('date_modified',
                                                           modify_time)
            if _coerced_modify_time:
                out['date_modified'] = _coerced_modify_time

        return out

    @classmethod
    def check_dependencies(cls):
        return True


def datetime_from_timestamp(ts):
    try:
        return datetime.fromtimestamp(ts).replace(microsecond=0)
    except (ValueError, TypeError):
        return None


def _get_access_time(file_path):
    t = os.path.getatime(file_path)
    return datetime_from_timestamp(t)


def _get_create_time(file_path):
    t = os.path.getctime(file_path)
    return datetime_from_timestamp(t)


def _get_modify_time(file_path):
    t = os.path.getmtime(file_path)
    return datetime_from_timestamp(t)
