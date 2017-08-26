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

from core import (
    exceptions,
    types,
    util
)
from core.util import wrap_exiftool
from extractors.metadata import AbstractMetadataExtractor


class ExiftoolMetadataExtractor(AbstractMetadataExtractor):
    """
    Extracts various types of metadata using "exiftool".
    """
    handles_mime_types = ['video/*', 'application/pdf', 'image/*',
                          'application/epub+zip', 'text/*']
    meowuri_root = 'metadata.exiftool'

    tagname_type_lookup = {
        'Composite:Aperture': types.AW_FLOAT,
        'Composite:ImageSize': types.AW_STRING,
        'Composite:HyperfocalDistance': types.AW_FLOAT,
        'EXIF:CreateDate': types.AW_EXIFTOOLTIMEDATE,
        'EXIF:DateTimeDigitized': types.AW_EXIFTOOLTIMEDATE,
        'EXIF:DateTimeOriginal': types.AW_EXIFTOOLTIMEDATE,
        'EXIF:ExifVersion': types.AW_INTEGER,
        'EXIF:GainControl': types.AW_INTEGER,
        'EXIF:ImageDescription': types.AW_STRING,
        'EXIF:Make': types.AW_STRING,
        'EXIF:ModifyDate': types.AW_EXIFTOOLTIMEDATE,
        'EXIF:Software': types.AW_STRING,
        'EXIF:UserComment': types.AW_STRING,
        'ExifTool:Error': types.AW_STRING,
        'ExifTool:ExifToolVersion': types.AW_FLOAT,
        'File:Directory': types.AW_PATH,
        'File:FileAccessDate': types.AW_EXIFTOOLTIMEDATE,
        'File:FileInodeChangeDate': types.AW_EXIFTOOLTIMEDATE,
        'File:FileModifyDate': types.AW_EXIFTOOLTIMEDATE,
        'File:FileName': types.AW_PATH,
        'File:FilePermissions': types.AW_INTEGER,
        'File:FileSize': types.AW_INTEGER,
        'File:FileType': types.AW_STRING,
        'File:FileTypeExtension': types.AW_PATH,
        'File:ImageHeight': types.AW_INTEGER,
        'File:ImageWidth': types.AW_INTEGER,
        'File:MIMEType': types.AW_STRING,
        'PDF:CreateDate': types.AW_EXIFTOOLTIMEDATE,
        'PDF:Creator': types.AW_STRING,
        'PDF:Linearized': types.AW_BOOLEAN,
        'PDF:ModifyDate': types.AW_EXIFTOOLTIMEDATE,
        'PDF:PDFVersion': types.AW_FLOAT,
        'PDF:PageCount': types.AW_INTEGER,
        'PDF:Producer': types.AW_STRING,
        'SourceFile': types.AW_PATH,
    }

    def __init__(self, source):
        super(ExiftoolMetadataExtractor, self).__init__(source)
        self._raw_metadata = None

    def _get_raw_metadata(self):
        result = self._get_exiftool_data()
        if result:
            return result
        else:
            return {}

    def _get_exiftool_data(self):
        """
        Returns:
            Exiftool results as a dictionary of strings/ints/floats.
        """
        with wrap_exiftool.ExifTool() as et:
            try:
                return et.get_metadata(self.source)
            except (AttributeError, ValueError, TypeError) as e:
                # Raises ValueError if an ExifTool instance isn't running.
                raise exceptions.ExtractorError(e)

    @classmethod
    def check_dependencies(cls):
        return util.is_executable('exiftool')
