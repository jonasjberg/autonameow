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
    ExtractedData
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
        'Composite:Aperture': ExtractedData(types.AW_FLOAT),
        'Composite:ImageSize': ExtractedData(types.AW_STRING),
        'Composite:HyperfocalDistance': ExtractedData(types.AW_FLOAT),
        #'ExifTool:ExifToolVersion': ExtractedData(types.AW_FLOAT),
        'EXIF:CreateDate': ExtractedData(
            wrapper=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.datetime, probability=1),
                fields.WeightedMapping(fields.date, probability=1)
            ]
        ),
        'EXIF:DateTimeDigitized': ExtractedData(
            wrapper=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.datetime, probability=1),
                fields.WeightedMapping(fields.date, probability=1)
            ]
        ),
        'EXIF:DateTimeOriginal': ExtractedData(
            wrapper=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.datetime, probability=1),
                fields.WeightedMapping(fields.date, probability=1)
            ]
        ),
        'EXIF:ExifVersion': ExtractedData(types.AW_INTEGER),
        'EXIF:GainControl': ExtractedData(types.AW_INTEGER),
        'EXIF:ImageDescription': ExtractedData(types.AW_STRING),
        'EXIF:Make': ExtractedData(types.AW_STRING),
        'EXIF:ModifyDate': ExtractedData(types.AW_EXIFTOOLTIMEDATE),
        'EXIF:Software': ExtractedData(types.AW_STRING),
        'EXIF:UserComment': ExtractedData(types.AW_STRING),
        'File:Directory': ExtractedData(types.AW_PATH),
        'File:FileAccessDate': ExtractedData(types.AW_EXIFTOOLTIMEDATE),
        'File:FileInodeChangeDate': ExtractedData(types.AW_EXIFTOOLTIMEDATE),
        'File:FileModifyDate': ExtractedData(types.AW_EXIFTOOLTIMEDATE),
        'File:FileName': ExtractedData(types.AW_PATH),
        'File:FilePermissions': ExtractedData(types.AW_INTEGER),
        'File:FileSize': ExtractedData(types.AW_INTEGER),
        'File:FileType': ExtractedData(types.AW_STRING),
        'File:FileTypeExtension': ExtractedData(types.AW_PATH),
        'File:ImageHeight': ExtractedData(types.AW_INTEGER),
        'File:ImageWidth': ExtractedData(types.AW_INTEGER),
        'File:MIMEType': ExtractedData(types.AW_STRING),
        'PDF:CreateDate': ExtractedData(types.AW_EXIFTOOLTIMEDATE),
        'PDF:Creator': ExtractedData(types.AW_STRING),
        'PDF:Linearized': ExtractedData(types.AW_BOOLEAN),
        'PDF:ModifyDate': ExtractedData(types.AW_EXIFTOOLTIMEDATE),
        'PDF:PDFVersion': ExtractedData(types.AW_FLOAT),
        'PDF:PageCount': ExtractedData(types.AW_INTEGER),
        'PDF:Producer': ExtractedData(
            wrapper=types.AW_STRING,
            mapped_fields=[
                fields.WeightedMapping(fields.publisher, probability=0.25),
                fields.WeightedMapping(fields.author, probability=0.01)
            ]
        ),
        'SourceFile': ExtractedData(types.AW_PATH),
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
