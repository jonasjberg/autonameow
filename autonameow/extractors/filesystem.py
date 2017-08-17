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

import logging as log

from core import types
from core.exceptions import ExtractorError
from core.fileobject import FileObject
from extractors import BaseExtractor


class CommonFileSystemExtractor(BaseExtractor):
    handles_mime_types = ['*/*']
    data_query_string = 'filesystem'

    def __init__(self, source):
        super(CommonFileSystemExtractor, self).__init__(source)

        self.data = {}

    def query(self, field=None):
        if not self.data:
            try:
                self.data = self._get_data(self.source)
            except ExtractorError as e:
                log.error('{!s} query FAILED: {!s}'.format(self, e))
                raise

        if not field:
            log.debug('{!s} responding to query for all fields'.format(self))
            return self.data
        else:
            log.debug('{!s} responding to query for field: '
                      '"{!s}"'.format(self, field))
            return self.data.get(field, False)

    @staticmethod
    def _get_data(file_object):
        if not isinstance(file_object, FileObject):
            raise ExtractorError('Expected source to be "FileObject" instance')

        out = {
            'basename.full': types.AW_PATHCOMPONENT(file_object.filename),
            'basename.extension': types.AW_PATHCOMPONENT(file_object.suffix),
            'basename.suffix': types.AW_PATHCOMPONENT(file_object.suffix),
            'basename.prefix': types.AW_PATHCOMPONENT(file_object.fnbase),
            'pathname.full': types.AW_PATH(file_object.pathname),
            'pathname.parent': types.AW_PATH(file_object.pathparent),
            'contents.mime_type': file_object.mime_type
        }
        return out
