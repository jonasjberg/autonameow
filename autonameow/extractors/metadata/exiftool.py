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
from thirdparty import pyexiftool
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

    EXTRACTEDDATA_WRAPPER_LOOKUP = {
        'ASF:CreationDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.datetime, probability=1),
                fields.WeightedMapping(fields.date, probability=1)
            ],
            generic_field=fields.GenericDateCreated
        ),
        'ASF:ImageHeight': ExtractedData(types.AW_INTEGER),
        'ASF:ImageWidth': ExtractedData(types.AW_INTEGER),
        'ASF:VideoCodecName': ExtractedData(types.AW_STRING),
        'Composite:Aperture': ExtractedData(types.AW_FLOAT),
        'Composite:ImageSize': ExtractedData(types.AW_STRING),
        'Composite:Megapixels': ExtractedData(types.AW_FLOAT),
        'Composite:HyperfocalDistance': ExtractedData(types.AW_FLOAT),
        #'ExifTool:ExifToolVersion': ExtractedData(types.AW_FLOAT),
        'EXIF:CreateDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.datetime, probability=1),
                fields.WeightedMapping(fields.date, probability=1)
            ],
            generic_field=fields.GenericDateCreated
        ),
        'EXIF:DateTimeDigitized': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.datetime, probability=1),
                fields.WeightedMapping(fields.date, probability=1)
            ],
            generic_field=fields.GenericDateCreated
        ),
        'EXIF:DateTimeOriginal': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.datetime, probability=1),
                fields.WeightedMapping(fields.date, probability=1)
            ],
            generic_field=fields.GenericDateCreated
        ),
        'EXIF:ExifVersion': ExtractedData(types.AW_INTEGER),
        'EXIF:GainControl': ExtractedData(types.AW_INTEGER),
        # TODO: Handle GPS date/time-information.
        #       EXIF:GPSTimeStamp: '12:07:59'
        #       EXIF:GPSDateStamp: '2016:03:26'

        # 'EXIF:GPSTimeStamp': ExtractedData(
        #     coercer=types.AW_EXIFTOOLTIMEDATE,
        #     mapped_fields=[
        #         fields.WeightedMapping(fields.time, probability=1),
        #     ]
        # ),
        'EXIF:GPSDateStamp': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.date, probability=1),
            ],
            generic_field=fields.GenericDateCreated
        ),
        'EXIF:ImageDescription': ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                fields.WeightedMapping(fields.description, probability=1),
                fields.WeightedMapping(fields.tags, probability=0.5),
                fields.WeightedMapping(fields.title, probability=0.25)
            ],
            generic_field=fields.GenericDescription
        ),
        'EXIF:Make': ExtractedData(types.AW_STRING),
        'EXIF:Model': ExtractedData(types.AW_STRING),
        'EXIF:ModifyDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.datetime, probability=0.25),
                fields.WeightedMapping(fields.date, probability=0.25)
            ],
            generic_field=fields.GenericDateModified
        ),
        'EXIF:Software': ExtractedData(types.AW_STRING),
        'EXIF:UserComment': ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                fields.WeightedMapping(fields.description, probability=0.5),
                fields.WeightedMapping(fields.tags, probability=0.5)
            ],
            generic_field=fields.GenericDateModified
        ),
        'File:Directory': ExtractedData(types.AW_PATH),
        'File:FileAccessDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.datetime, probability=0.01),
                fields.WeightedMapping(fields.date, probability=0.01)
            ],
            generic_field=fields.GenericDateModified
        ),
        'File:FileInodeChangeDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.datetime, probability=0.01),
                fields.WeightedMapping(fields.date, probability=0.01)
            ],
            generic_field=fields.GenericDateModified
        ),
        'File:FileModifyDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.datetime, probability=0.25),
                fields.WeightedMapping(fields.date, probability=0.25)
            ],
            generic_field=fields.GenericDateModified
        ),
        'File:FileName': ExtractedData(types.AW_PATH),
        'File:FilePermissions': ExtractedData(types.AW_INTEGER),
        'File:FileSize': ExtractedData(types.AW_INTEGER),
        'File:FileType': ExtractedData(types.AW_STRING),
        'File:FileTypeExtension': ExtractedData(types.AW_PATHCOMPONENT),
        'File:ImageHeight': ExtractedData(types.AW_INTEGER),
        'File:ImageWidth': ExtractedData(types.AW_INTEGER),
        'File:MIMEType': ExtractedData(
            coercer=types.AW_MIMETYPE,
            mapped_fields=[
                fields.WeightedMapping(fields.extension, probability=1)
            ],
            generic_field=fields.GenericMimeType
        ),
        'PDF:CreateDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.datetime, probability=1),
                fields.WeightedMapping(fields.date, probability=1)
            ],
            generic_field=fields.GenericDateCreated
        ),
        'PDF:Creator': ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                fields.WeightedMapping(fields.author, probability=0.025),
                fields.WeightedMapping(fields.publisher, probability=0.02),
                fields.WeightedMapping(fields.title, probability=0.01)
            ],
            generic_field=fields.GenericCreator
        ),
        'PDF:Linearized': ExtractedData(types.AW_BOOLEAN),
        'PDF:ModifyDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.datetime, probability=0.25),
                fields.WeightedMapping(fields.date, probability=0.25)
            ],
            generic_field=fields.GenericDateModified
        ),
        'PDF:PDFVersion': ExtractedData(types.AW_FLOAT),
        'PDF:PageCount': ExtractedData(types.AW_INTEGER),
        'PDF:Producer': ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                fields.WeightedMapping(fields.publisher, probability=0.25),
                fields.WeightedMapping(fields.author, probability=0.02),
                fields.WeightedMapping(fields.title, probability=0.01)
            ],
            generic_field=fields.GenericProducer
        ),
        'SourceFile': ExtractedData(types.AW_PATH),
        'QuickTime:CreateDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.datetime, probability=1),
                fields.WeightedMapping(fields.date, probability=1)
            ],
            generic_field=fields.GenericDateCreated
        ),
        'QuickTime:CreationDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.datetime, probability=1),
                fields.WeightedMapping(fields.date, probability=1)
            ],
            generic_field=fields.GenericDateCreated
        ),
        'QuickTime:ModifyDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.datetime, probability=0.5),
                fields.WeightedMapping(fields.date, probability=0.5)
            ],
            generic_field=fields.GenericDateModified
        ),
        'QuickTime:CreationDate-und-SE': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.datetime, probability=1),
                fields.WeightedMapping(fields.date, probability=1)
            ],
            generic_field=fields.GenericDateCreated
        ),
        'QuickTime:TrackCreateDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.datetime, probability=1),
                fields.WeightedMapping(fields.date, probability=1)
            ],
            generic_field=fields.GenericDateCreated
        ),
        'QuickTime:TrackModifyDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.datetime, probability=0.5),
                fields.WeightedMapping(fields.date, probability=0.5)
            ],
            generic_field=fields.GenericDateModified
        ),
        'QuickTime:MediaCreateDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.datetime, probability=1),
                fields.WeightedMapping(fields.date, probability=1)
            ],
            generic_field=fields.GenericDateCreated
        ),
        'QuickTime:MediaModifyDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.datetime, probability=0.5),
                fields.WeightedMapping(fields.date, probability=0.5)
            ],
            generic_field=fields.GenericDateModified
        ),

        # TODO: [TD0084] Add handling collections to type wrapper classes.
        # 'XMP:Subject': ExtractedData(
        #     coercer=types.AW_STRINGLIST,
        #     mapped_fields=[
        #         fields.WeightedMapping(fields.tags, probability=1),
        #         fields.WeightedMapping(fields.title, probability=0.9)
        #         fields.WeightedMapping(fields.description, probability=0.8)
        #     ]
        # ),
        # TODO: [TD0084] Add handling collections to type wrapper classes.
        # 'XMP:TagsList': ExtractedData(
        #     coercer=types.AW_STRINGLIST,
        #     mapped_fields=[
        #         fields.WeightedMapping(fields.tags, probability=1),
        #         fields.WeightedMapping(fields.title, probability=0.9)
        #         fields.WeightedMapping(fields.description, probability=0.8)
        #     ]
        # )
    }

    def __init__(self):
        super(ExiftoolMetadataExtractor, self).__init__()

    def _get_metadata(self, source):
        _raw_metadata = self._get_exiftool_data(source)
        if _raw_metadata:
            # Internal data format boundary.  Wrap "raw" data with type classes.
            metadata = self._to_internal_format(_raw_metadata)
            return metadata

    def _to_internal_format(self, raw_metadata):
        out = {}

        for tag_name, value in raw_metadata.items():
            if tag_name in self.EXTRACTEDDATA_WRAPPER_LOOKUP:
                wrapper = self.EXTRACTEDDATA_WRAPPER_LOOKUP[tag_name]
            elif self._should_skip_binary_blob(value):
                    continue
            else:
                # Use a default 'ExtractedData' class.
                wrapper = ExtractedData(coercer=None, mapped_fields=None)

            wrapped = ExtractedData.from_raw(wrapper, value)
            if wrapped:
                out[tag_name] = wrapped
            else:
                self.log.debug('Wrapping exiftool data returned None '
                               'for "{!s}" ({})'.format(value, type(value)))

        return out

    def _get_exiftool_data(self, source):
        """
        Returns:
            Exiftool results as a dictionary of strings/ints/floats.
        """
        with pyexiftool.ExifTool() as et:
            try:
                return et.get_metadata(source)
            except (AttributeError, ValueError, TypeError) as e:
                # Raises ValueError if an ExifTool instance isn't running.
                raise ExtractorError(e)

    def _should_skip_binary_blob(self, value):
        return isinstance(value, str) and 'use -b option to extract' in value

    @classmethod
    def check_dependencies(cls):
        return util.is_executable('exiftool') and pyexiftool is not None
