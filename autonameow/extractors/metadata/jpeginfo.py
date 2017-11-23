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

import re
import subprocess

from core import types
from core.model import genericfields as gf
from extractors import (
    BaseExtractor,
    ExtractorError
)
import util


class JpeginfoMetadataExtractor(BaseExtractor):
    """
    Extracts jpeg/jfif image metadata using "jpeginfo".
    """
    HANDLES_MIME_TYPES = ['image/jpeg', 'image/jfif']
    is_slow = False

    STATUS_LOOKUP = {
        'OK': 1.0,
        'UNKNOWN': 0.66,
        'WARNING': 0.33,
        'ERROR': 0.0
    }

    FIELD_LOOKUP = {
        'health': {
            'coercer': types.AW_FLOAT,
            'multivalued': False,
            'mapped_fields': None,
            'generic_field': gf.GenericHealth
        },
        'is_jpeg': {
            'coercer': types.AW_BOOLEAN,
            'multivalued': False,
            'mapped_fields': None,
            'generic_field': None
        }
    }

    def __init__(self):
        super(JpeginfoMetadataExtractor, self).__init__()

    def extract(self, fileobject, **kwargs):
        source = fileobject.abspath
        _metadata = self._get_metadata(source)
        return _metadata

    def _get_metadata(self, source):
        jpeginfo_output = _run_jpeginfo(source)
        if not jpeginfo_output:
            self.log.debug('Got empty output from jpeginfo')
            return

        if 'not a jpeg file' in jpeginfo_output.lower():
            is_jpeg = False
            health = self.STATUS_LOOKUP.get('UNKNOWN')
        else:
            is_jpeg = True
            # Regex from 'photosort.py'. Copyright (c) 2013, Mike Greiling.
            match = re.search("\[([^\]]*)\][^\[]*$", jpeginfo_output)
            status = match.group(1) if match else 'UNKNOWN'
            health = self.STATUS_LOOKUP.get(status,
                                            self.STATUS_LOOKUP.get('UNKNOWN'))

        out = {}

        _coerced_health = self.coerce_field_value('health', health)
        if _coerced_health is not None:
            out['health'] = _coerced_health

        _coerced_is_jpeg = self.coerce_field_value('is_jpeg', is_jpeg)
        if _coerced_is_jpeg is not None:
            out['is_jpeg'] = _coerced_is_jpeg

        return out

    @classmethod
    def check_dependencies(cls):
        return util.is_executable('jpeginfo')


def _run_jpeginfo(source):
    try:
        process = subprocess.Popen(
            ['jpeginfo', '-c', source],
            shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        stdout, stderr = process.communicate()
    except (OSError, ValueError, TypeError, subprocess.SubprocessError) as e:
        raise ExtractorError(e)

    result = types.force_string(stdout)
    if not result:
        return ''
    return result
