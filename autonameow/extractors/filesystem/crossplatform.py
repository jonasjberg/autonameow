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

from extractors.metadata.base import BaseMetadataExtractor


class CrossPlatformFileSystemExtractor(BaseMetadataExtractor):
    HANDLES_MIME_TYPES = ['*/*']
    MEOWURI_LEAF = 'xplat'
    IS_SLOW = False
    FIELD_FILEOBJECT_ATTRIBUTE_MAP = [
        ('abspath_full', 'abspath'),
        ('basename_full', 'filename'),
        ('extension', 'basename_suffix'),
        ('basename_suffix', 'basename_suffix'),
        ('basename_prefix', 'basename_prefix'),
        ('pathname_full', 'pathname'),
        ('pathname_parent', 'pathparent'),
        ('mime_type', 'mime_type')
    ]

    def extract(self, fileobject, **kwargs):
        return self._get_metadata(fileobject)

    def _get_metadata(self, fileobject):
        metadata = dict()
        metadata.update(self._collect_from_fileobject(fileobject))
        metadata.update(self._collect_filesystem_timestamps(fileobject.abspath))
        return metadata

    def _collect_from_fileobject(self, fileobject):
        fileobject_metadata = dict()
        for field, attribute in self.FIELD_FILEOBJECT_ATTRIBUTE_MAP:
            fileobject_attr_value = getattr(fileobject, attribute)
            coerced_value = self.coerce_field_value(field, fileobject_attr_value)
            if coerced_value is not None:
                fileobject_metadata[field] = coerced_value
        return fileobject_metadata

    def _collect_filesystem_timestamps(self, filepath):
        timestamps = dict()
        try:
            access_time = _get_access_time(filepath)
            create_time = _get_create_time(filepath)
            modify_time = _get_modify_time(filepath)
        except OSError as e:
            self.log.error(
                'Unable to get filesystem timestamps: {!s}'.format(e)
            )
            return timestamps

        coerced_t_access = self.coerce_field_value('date_accessed', access_time)
        if coerced_t_access:
            timestamps['date_accessed'] = coerced_t_access

        coerced_t_create = self.coerce_field_value('date_created', create_time)
        if coerced_t_create:
            timestamps['date_created'] = coerced_t_create

        coerced_t_modify = self.coerce_field_value('date_modified', modify_time)
        if coerced_t_modify:
            timestamps['date_modified'] = coerced_t_modify

        return timestamps

    @classmethod
    def dependencies_satisfied(cls):
        return True


def datetime_from_timestamp(ts):
    try:
        return datetime.fromtimestamp(ts).replace(microsecond=0)
    except (ValueError, TypeError):
        return None


def _get_access_time(filepath):
    t = os.path.getatime(filepath)
    return datetime_from_timestamp(t)


def _get_create_time(filepath):
    t = os.path.getctime(filepath)
    return datetime_from_timestamp(t)


def _get_modify_time(filepath):
    t = os.path.getmtime(filepath)
    return datetime_from_timestamp(t)
