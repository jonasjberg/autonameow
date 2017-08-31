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

import os

from datetime import datetime

from core import (
    exceptions,
    types
)
from core.fileobject import FileObject
from extractors import BaseExtractor


class CommonFileSystemExtractor(BaseExtractor):
    handles_mime_types = ['*/*']
    meowuri_root = 'filesystem'

    def __init__(self, source):
        super(CommonFileSystemExtractor, self).__init__(source)

        self.data = {}

    def execute(self, **kwargs):
        if not self.data:
            try:
                self.data = self._get_data(self.source)
            except exceptions.ExtractorError as e:
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
            raise exceptions.ExtractorError(
                'Expected source to be "FileObject" instance'
            )

        out = {
            'basename.full': types.AW_PATHCOMPONENT(file_object.filename),
            'basename.extension': types.AW_PATHCOMPONENT(file_object.basename_suffix),
            'basename.suffix': types.AW_PATHCOMPONENT(file_object.basename_suffix),
            'basename.prefix': types.AW_PATHCOMPONENT(file_object.basename_prefix),
            'pathname.full': types.AW_PATH(file_object.pathname),
            'pathname.parent': types.AW_PATH(file_object.pathparent),
            'contents.mime_type': file_object.mime_type
        }

        try:
            modify_time = os.path.getmtime(file_object.abspath)
            create_time = os.path.getctime(file_object.abspath)
            access_time = os.path.getatime(file_object.abspath)
        except OSError as e:
            self.log.error('Unable to get timestamps from filesystem:'
                           ' {!s}'.format(e))
        else:
            add_datetime_from_timestamp(out, 'date_accessed', access_time)
            add_datetime_from_timestamp(out, 'date_created', create_time)
            add_datetime_from_timestamp(out, 'date_modified', modify_time)

        return out

    @classmethod
    def check_dependencies(cls):
        return True


def add_datetime_from_timestamp(dictionary, key, ts):
    try:
        dt = datetime.fromtimestamp(ts).replace(microsecond=0)
        dictionary[key] = dt
    except (ValueError, TypeError):
        pass
