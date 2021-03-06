# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2020 Jonas Sjöberg <autonameow@jonasjberg.com>
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

import re
import subprocess

from extractors.metadata.base import BaseMetadataExtractor
from extractors import ExtractorError
from util import coercers
from util import process


class JpeginfoMetadataExtractor(BaseMetadataExtractor):
    """
    Extracts jpeg/jfif image metadata using "jpeginfo".
    """
    HANDLES_MIME_TYPES = ['image/jpeg', 'image/jfif']
    IS_SLOW = False

    _HEALTH = {
        'OK': 1.0,
        'UNKNOWN': 0.66,
        'WARNING': 0.33,
        'ERROR': 0.0
    }

    def extract(self, fileobject, **kwargs):
        return self._get_metadata(fileobject.abspath)

    def _get_metadata(self, filepath):
        jpeginfo_output = _run_jpeginfo(filepath)
        if not jpeginfo_output:
            return dict()

        if 'not a jpeg file' in jpeginfo_output.lower():
            is_jpeg = False
            health = self._HEALTH.get('UNKNOWN')
        else:
            is_jpeg = True
            # Regex from 'photosort.py'. Copyright (c) 2013, Mike Greiling.
            match = re.search(r'\[([^\]]*)\][^\[]*$', jpeginfo_output)
            status = match.group(1) if match else 'UNKNOWN'
            health = self._HEALTH.get(status, self._HEALTH.get('UNKNOWN'))

        metadata = dict()
        coerced_health = self.coerce_field_value('health', health)
        if coerced_health is not None:
            metadata['health'] = coerced_health

        coerced_is_jpeg = self.coerce_field_value('is_jpeg', is_jpeg)
        if coerced_is_jpeg is not None:
            metadata['is_jpeg'] = coerced_is_jpeg

        return metadata

    @classmethod
    def dependencies_satisfied(cls):
        return process.is_executable('jpeginfo')


def _run_jpeginfo(filepath):
    try:
        process = subprocess.Popen(
            ['jpeginfo', '-c', filepath],
            shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        stdout, _ = process.communicate()
    except (OSError, ValueError, TypeError, subprocess.SubprocessError) as e:
        raise ExtractorError(e)

    str_stdout = coercers.force_string(stdout)
    if not str_stdout:
        return ''
    return str_stdout
