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

import logging
import os

from datetime import datetime

from extractors import (
    BaseExtractor,
    ExtractorError,
    ExtractedData
)
from core import types, fields
from core.fileobject import FileObject


log = logging.getLogger(__name__)


class CommonFileSystemExtractor(BaseExtractor):
    handles_mime_types = ['*/*']
    meowuri_root = 'filesystem'

    wrapper_lookup = {
        'abspath.full': ExtractedData(types.AW_PATH),
        'basename.full': ExtractedData(types.AW_PATHCOMPONENT),
        'basename.extension': ExtractedData(
            wrapper=types.AW_PATHCOMPONENT,
            mapped_fields=[
                fields.WeightedMapping(fields.extension, probability=1),
            ]
        ),
        'basename.suffix': ExtractedData(
            wrapper=types.AW_PATHCOMPONENT,
            mapped_fields=[
                fields.WeightedMapping(fields.extension, probability=1),
            ]
        ),
        'basename.prefix': ExtractedData(types.AW_PATHCOMPONENT),
        'pathname.full': ExtractedData(types.AW_PATH),
        'pathname.parent': ExtractedData(types.AW_PATH),
        'contents.mime_type': ExtractedData(
            wrapper=types.AW_STRING,
            mapped_fields=[
                fields.WeightedMapping(fields.extension, probability=1),
            ]
        ),
        'date_accessed': ExtractedData(
            wrapper=types.AW_TIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.date, probability=0.1),
                fields.WeightedMapping(fields.datetime, probability=0.1),
            ]
        ),
        'date_created': ExtractedData(
            wrapper=types.AW_TIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.date, probability=1),
                fields.WeightedMapping(fields.datetime, probability=1),
            ]
        ),
        'date_modified': ExtractedData(
            wrapper=types.AW_TIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.date, probability=0.25),
                fields.WeightedMapping(fields.datetime, probability=0.25),
            ]
        )
    }

    def __init__(self, source):
        super(CommonFileSystemExtractor, self).__init__(source)

        self.data = {}

    def execute(self, **kwargs):
        if not self.data:
            try:
                self.data = self._get_data(self.source)
            except ExtractorError as e:
                self.log.error('{!s} extraction FAILED: {!s}'.format(self, e))
                raise

        if 'field' not in kwargs:
            self.log.debug('{!s} returning all extracted data'.format(self))
            return self.data
        else:
            field = kwargs.get('field')
            self.log.debug('{!s} returning data matching field: '
                           '"{!s}"'.format(self, field))
            return self.data.get(field)

    def _get_data(self, file_object):
        if not isinstance(file_object, FileObject):
            raise ExtractorError(
                'Expected source to be "FileObject" instance'
            )

        # out = {
        #     'basename.full': types.AW_PATHCOMPONENT(file_object.filename),
        #     'basename.extension': types.AW_PATHCOMPONENT(file_object.basename_suffix),
        #     'basename.suffix': types.AW_PATHCOMPONENT(file_object.basename_suffix),
        #     'basename.prefix': types.AW_PATHCOMPONENT(file_object.basename_prefix),
        #     'pathname.full': types.AW_PATH(file_object.pathname),
        #     'pathname.parent': types.AW_PATH(file_object.pathparent),
        #     'contents.mime_type': file_object.mime_type
        # }

        meowuris_datasources = [
            ('abspath.full', file_object.abspath),
            ('basename.full', file_object.filename),
            ('basename.extension', file_object.basename_suffix),
            ('basename.suffix', file_object.basename_suffix),
            ('basename.prefix', file_object.basename_prefix),
            ('pathname.full', file_object.pathname),
            ('pathname.parent', file_object.pathparent),
            ('contents.mime_type', file_object.mime_type)
        ]
        out = {}
        for meowuri, datasource in meowuris_datasources:
            out[meowuri] = self._to_internal_format(meowuri, datasource)

        try:
            access_time = _get_access_time(file_object.abspath)
            create_time = _get_create_time(file_object.abspath)
            modify_time = _get_modify_time(file_object.abspath)
        except OSError as e:
            self.log.error('Unable to get timestamps from filesystem:'
                           ' {!s}'.format(e))
        else:
            out['date_accessed'] = self._to_internal_format('date_accessed',
                                                            access_time)
            out['date_created'] = self._to_internal_format('date_created',
                                                           create_time)
            out['date_modified'] = self._to_internal_format('date_modified',
                                                            modify_time)

        return out

    def _to_internal_format(self, meowuri, data):
        wrapper = self.wrapper_lookup[meowuri]
        return wrapper(data)

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
