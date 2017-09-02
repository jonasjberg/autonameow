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
    types,
    util,
    fields
)
from core.util import wrap_exiftool
from extractors import (
    ExtractorError,
    metadata
)
from extractors.metadata.common import AbstractMetadataExtractor


class ExiftoolMetadataExtractor(AbstractMetadataExtractor):
    """
    Extracts various types of metadata using "exiftool".
    """
    handles_mime_types = ['video/*', 'application/pdf', 'image/*',
                          'application/epub+zip', 'text/*']
    meowuri_root = 'metadata.exiftool'

    tagname_type_lookup = {
        'Composite:Aperture': metadata.Item(types.AW_FLOAT),
        'Composite:ImageSize': metadata.Item(types.AW_STRING),
        'Composite:HyperfocalDistance': metadata.Item(types.AW_FLOAT),
        'EXIF:CreateDate': metadata.Item(
            wrapper=types.AW_EXIFTOOLTIMEDATE,
            fields=[
                fields.WeightedMapping(fields.datetime, probability=1),
                fields.WeightedMapping(fields.date, probability=1)
            ]
        ),
        'EXIF:DateTimeDigitized': metadata.Item(
            wrapper=types.AW_EXIFTOOLTIMEDATE,
            fields=[
                fields.WeightedMapping(fields.datetime, probability=1),
                fields.WeightedMapping(fields.date, probability=1)
            ]
        ),
        'EXIF:DateTimeOriginal': metadata.Item(
            wrapper=types.AW_EXIFTOOLTIMEDATE,
            fields=[
                fields.WeightedMapping(fields.datetime, probability=1),
                fields.WeightedMapping(fields.date, probability=1)
            ]
        ),
        'EXIF:ExifVersion': metadata.Item(types.AW_INTEGER),
        'EXIF:GainControl': metadata.Item(types.AW_INTEGER),
        'EXIF:ImageDescription': metadata.Item(types.AW_STRING),
        'EXIF:Make': metadata.Item(types.AW_STRING),
        'EXIF:ModifyDate': metadata.Item(types.AW_EXIFTOOLTIMEDATE),
        'EXIF:Software': metadata.Item(types.AW_STRING),
        'EXIF:UserComment': metadata.Item(types.AW_STRING),
        'File:Directory': metadata.Item(types.AW_PATH),
        'File:FileAccessDate': metadata.Item(types.AW_EXIFTOOLTIMEDATE),
        'File:FileInodeChangeDate': metadata.Item(types.AW_EXIFTOOLTIMEDATE),
        'File:FileModifyDate': metadata.Item(types.AW_EXIFTOOLTIMEDATE),
        'File:FileName': metadata.Item(types.AW_PATH),
        'File:FilePermissions': metadata.Item(types.AW_INTEGER),
        'File:FileSize': metadata.Item(types.AW_INTEGER),
        'File:FileType': metadata.Item(types.AW_STRING),
        'File:FileTypeExtension': metadata.Item(types.AW_PATH),
        'File:ImageHeight': metadata.Item(types.AW_INTEGER),
        'File:ImageWidth': metadata.Item(types.AW_INTEGER),
        'File:MIMEType': metadata.Item(types.AW_STRING),
        'PDF:CreateDate': metadata.Item(types.AW_EXIFTOOLTIMEDATE),
        'PDF:Creator': metadata.Item(types.AW_STRING),
        'PDF:Linearized': metadata.Item(types.AW_BOOLEAN),
        'PDF:ModifyDate': metadata.Item(types.AW_EXIFTOOLTIMEDATE),
        'PDF:PDFVersion': metadata.Item(types.AW_FLOAT),
        'PDF:PageCount': metadata.Item(types.AW_INTEGER),
        'PDF:Producer': metadata.Item(
            wrapper=types.AW_STRING,
            fields=[
                fields.WeightedMapping(fields.publisher, probability=0.25),
                fields.WeightedMapping(fields.author, probability=0.01)
            ]
        ),
        'SourceFile': metadata.Item(types.AW_PATH),
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
                raise ExtractorError(e)

    @classmethod
    def check_dependencies(cls):
        return util.is_executable('exiftool')
