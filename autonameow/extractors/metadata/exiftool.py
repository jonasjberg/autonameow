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
    util,
    fields
)
from core.util import wrap_exiftool
from extractors import metadata
from extractors.metadata import AbstractMetadataExtractor


class ExiftoolMetadataExtractor(AbstractMetadataExtractor):
    """
    Extracts various types of metadata using "exiftool".
    """
    handles_mime_types = ['video/*', 'application/pdf', 'image/*',
                          'application/epub+zip', 'text/*']
    meowuri_root = 'metadata.exiftool'

    tagname_type_lookup = {
        'Composite:Aperture': metadata.Item(wrapper=types.AW_FLOAT, fields=None),
        'Composite:ImageSize': metadata.Item(wrapper=types.AW_STRING, fields=None),
        'Composite:HyperfocalDistance': metadata.Item(types.AW_FLOAT, fields=None),
        'EXIF:CreateDate': metadata.Item(
            wrapper=types.AW_EXIFTOOLTIMEDATE,
            fields=[
                fields.Weighted(fields.datetime, probability=1),
                fields.Weighted(fields.date, probability=1)
            ]
        ),
        'EXIF:DateTimeDigitized': metadata.Item(
            wrapper=types.AW_EXIFTOOLTIMEDATE,
            fields=[
                fields.Weighted(fields.datetime, probability=1),
                fields.Weighted(fields.date, probability=1)
            ]
        ),
        'EXIF:DateTimeOriginal': metadata.Item(
            wrapper=types.AW_EXIFTOOLTIMEDATE,
            fields=[
                fields.Weighted(fields.datetime, probability=1),
                fields.Weighted(fields.date, probability=1)
            ]
        ),
        'EXIF:ExifVersion': (types.AW_INTEGER, None),
        'EXIF:GainControl': (types.AW_INTEGER, None),
        'EXIF:ImageDescription': (types.AW_STRING, None),
        'EXIF:Make': (types.AW_STRING, None),
        'EXIF:ModifyDate': (types.AW_EXIFTOOLTIMEDATE, None),
        'EXIF:Software': (types.AW_STRING, None),
        'EXIF:UserComment': (types.AW_STRING, None),
        'ExifTool:Error': (types.AW_STRING, None),
        'ExifTool:ExifToolVersion': (types.AW_FLOAT, None),
        'File:Directory': (types.AW_PATH, None),
        'File:FileAccessDate': (types.AW_EXIFTOOLTIMEDATE, None),
        'File:FileInodeChangeDate': (types.AW_EXIFTOOLTIMEDATE, None),
        'File:FileModifyDate': (types.AW_EXIFTOOLTIMEDATE, None),
        'File:FileName': (types.AW_PATH, None),
        'File:FilePermissions': (types.AW_INTEGER, None),
        'File:FileSize': (types.AW_INTEGER, None),
        'File:FileType': (types.AW_STRING, None),
        'File:FileTypeExtension': (types.AW_PATH, None),
        'File:ImageHeight': (types.AW_INTEGER, None),
        'File:ImageWidth': (types.AW_INTEGER, None),
        'File:MIMEType': (types.AW_STRING, None),
        'PDF:CreateDate': (types.AW_EXIFTOOLTIMEDATE, None),
        'PDF:Creator': (types.AW_STRING, None),
        'PDF:Linearized': (types.AW_BOOLEAN, None),
        'PDF:ModifyDate': (types.AW_EXIFTOOLTIMEDATE, None),
        'PDF:PDFVersion': metadata.Item(wrapper=types.AW_FLOAT, fields=None),
        'PDF:PageCount': metadata.Item(wrapper=types.AW_INTEGER, fields=None),
        'PDF:Producer': metadata.Item(
            wrapper=types.AW_STRING,
            fields=[
                fields.Weighted(fields.publisher, probability=0.25),
                fields.Weighted(fields.author, probability=0.01)
            ]
        ),
        'SourceFile': (types.AW_PATH, None),
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
