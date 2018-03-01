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

from extractors import BaseExtractor


class CrossPlatformFileSystemExtractor(BaseExtractor):
    HANDLES_MIME_TYPES = ['*/*']
    MEOWURI_LEAF = 'xplat'
    IS_SLOW = False

    FIELD_LOOKUP = {
        'abspath_full': {'coercer': 'aw_path', 'multivalued': 'false'},
        'basename_full': {
            'coercer': 'aw_pathcomponent',
            'multivalued': 'false'
        },
        'extension': {
            'coercer': 'aw_pathcomponent',
            'multivalued': 'false',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Extension', 'probability': '1'}},
            ],
        },
        'basename_suffix': {
            'coercer': 'aw_pathcomponent',
            'multivalued': 'false',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Extension', 'probability': '1'}},
            ]
        },
        'basename_prefix': {
            'coercer': 'aw_pathcomponent',
            'multivalued': 'false',
        },
        'pathname_full': {'coercer': 'aw_path', 'multivalued': 'false'},
        'pathname_parent': {'coercer': 'aw_path', 'multivalued': 'false'},
        'mime_type': {
            'coercer': 'aw_mimetype',
            'multivalued': 'false',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Extension', 'probability': '1'}},
            ],
            'generic_field': 'mime_type'
        },
        'date_accessed': {
            'coercer': 'aw_timedate',
            'multivalued': 'false',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Date', 'probability': '0.1'}},
                {'WeightedMapping': {'field': 'DateTime', 'probability': '0.1'}},
            ]
        },
        'date_created': {
            'coercer': 'aw_timedate',
            'multivalued': 'false',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Date', 'probability': '1'}},
                {'WeightedMapping': {'field': 'DateTime', 'probability': '1'}},
            ],
            'generic_field': 'date_created'
        },
        'date_modified': {
            'coercer': 'aw_timedate',
            'multivalued': 'false',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Date', 'probability': '0.25'}},
                {'WeightedMapping': {'field': 'DateTime', 'probability': '0.25'}},
            ],
            'generic_field': 'date_modified'
        }
    }

    def extract(self, fileobject, **kwargs):
        out = dict()
        out.update(self._collect_from_fileobject(fileobject))
        out.update(self._collect_filesystem_timestamps(fileobject))
        return out

    def _collect_from_fileobject(self, fileobject):
        _datasources = [
            ('abspath_full', fileobject.abspath),
            ('basename_full', fileobject.filename),
            ('extension', fileobject.basename_suffix),
            ('basename_suffix', fileobject.basename_suffix),
            ('basename_prefix', fileobject.basename_prefix),
            ('pathname_full', fileobject.pathname),
            ('pathname_parent', fileobject.pathparent),
            ('mime_type', fileobject.mime_type)
        ]

        result = dict()
        for _uri, _source in _datasources:
            _coerced_data = self.coerce_field_value(_uri, _source)
            if _coerced_data is not None:
                result[_uri] = _coerced_data
        return result

    def _collect_filesystem_timestamps(self, fileobject):
        result = dict()
        try:
            access_time = _get_access_time(fileobject.abspath)
            create_time = _get_create_time(fileobject.abspath)
            modify_time = _get_modify_time(fileobject.abspath)
        except OSError as e:
            self.log.error(
                'Unable to get filesystem timestamps: {!s}'.format(e)
            )
            return result

        coerced_t_access = self.coerce_field_value('date_accessed', access_time)
        if coerced_t_access:
            result['date_accessed'] = coerced_t_access

        coerced_t_create = self.coerce_field_value('date_created', create_time)
        if coerced_t_create:
            result['date_created'] = coerced_t_create

        coerced_t_modify = self.coerce_field_value('date_modified', modify_time)
        if coerced_t_modify:
            result['date_modified'] = coerced_t_modify

        return result

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
