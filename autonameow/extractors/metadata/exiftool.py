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
            ],
            generic_field=fields.GenericDateCreated
        ),
        'EXIF:DateTimeDigitized': ExtractedData(
            wrapper=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.datetime, probability=1),
                fields.WeightedMapping(fields.date, probability=1)
            ],
            generic_field=fields.GenericDateCreated
        ),
        'EXIF:DateTimeOriginal': ExtractedData(
            wrapper=types.AW_EXIFTOOLTIMEDATE,
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
        #     wrapper=types.AW_EXIFTOOLTIMEDATE,
        #     mapped_fields=[
        #         fields.WeightedMapping(fields.time, probability=1),
        #     ]
        # ),
        'EXIF:GPSDateStamp': ExtractedData(
            wrapper=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.date, probability=1),
            ],
            generic_field=fields.GenericDateCreated
        ),
        'EXIF:ImageDescription': ExtractedData(
            wrapper=types.AW_STRING,
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
            wrapper=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.datetime, probability=0.25),
                fields.WeightedMapping(fields.date, probability=0.25)
            ],
            generic_field=fields.GenericDateModified
        ),
        'EXIF:Software': ExtractedData(types.AW_STRING),
        'EXIF:UserComment': ExtractedData(
            wrapper=types.AW_STRING,
            mapped_fields=[
                fields.WeightedMapping(fields.description, probability=0.5),
                fields.WeightedMapping(fields.tags, probability=0.5)
            ],
            generic_field=fields.GenericDateModified
        ),
        'File:Directory': ExtractedData(types.AW_PATH),
        'File:FileAccessDate': ExtractedData(
            wrapper=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.datetime, probability=0.01),
                fields.WeightedMapping(fields.date, probability=0.01)
            ],
            generic_field=fields.GenericDateModified
        ),
        'File:FileInodeChangeDate': ExtractedData(
            wrapper=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.datetime, probability=0.01),
                fields.WeightedMapping(fields.date, probability=0.01)
            ],
            generic_field=fields.GenericDateModified
        ),
        'File:FileModifyDate': ExtractedData(
            wrapper=types.AW_EXIFTOOLTIMEDATE,
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
            wrapper=types.AW_MIMETYPE,
            mapped_fields=[
                fields.WeightedMapping(fields.extension, probability=1)
            ],
            generic_field=fields.GenericMimeType
        ),
        'PDF:CreateDate': ExtractedData(
            wrapper=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.datetime, probability=1),
                fields.WeightedMapping(fields.date, probability=1)
            ],
            generic_field=fields.GenericDateCreated
        ),
        'PDF:Creator': ExtractedData(
            wrapper=types.AW_STRING,
            mapped_fields=[
                fields.WeightedMapping(fields.author, probability=0.025),
                fields.WeightedMapping(fields.publisher, probability=0.02),
                fields.WeightedMapping(fields.title, probability=0.01)
            ],
            generic_field=fields.GenericCreator
        ),
        'PDF:Linearized': ExtractedData(types.AW_BOOLEAN),
        'PDF:ModifyDate': ExtractedData(
            wrapper=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.datetime, probability=0.25),
                fields.WeightedMapping(fields.date, probability=0.25)
            ],
            generic_field=fields.GenericDateModified
        ),
        'PDF:PDFVersion': ExtractedData(types.AW_FLOAT),
        'PDF:PageCount': ExtractedData(types.AW_INTEGER),
        'PDF:Producer': ExtractedData(
            wrapper=types.AW_STRING,
            mapped_fields=[
                fields.WeightedMapping(fields.publisher, probability=0.25),
                fields.WeightedMapping(fields.author, probability=0.02),
                fields.WeightedMapping(fields.title, probability=0.01)
            ],
            generic_field=fields.GenericProducer
        ),
        'SourceFile': ExtractedData(types.AW_PATH),
        'QuickTime:CreateDate': ExtractedData(
            wrapper=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.datetime, probability=1),
                fields.WeightedMapping(fields.date, probability=1)
            ],
            generic_field=fields.GenericDateCreated
        ),
        'QuickTime:CreationDate': ExtractedData(
            wrapper=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.datetime, probability=1),
                fields.WeightedMapping(fields.date, probability=1)
            ],
            generic_field=fields.GenericDateCreated
        ),
        'QuickTime:ModifyDate': ExtractedData(
            wrapper=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.datetime, probability=0.5),
                fields.WeightedMapping(fields.date, probability=0.5)
            ],
            generic_field=fields.GenericDateModified
        ),
        'QuickTime:CreationDate-und-SE': ExtractedData(
            wrapper=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.datetime, probability=1),
                fields.WeightedMapping(fields.date, probability=1)
            ],
            generic_field=fields.GenericDateCreated
        ),
        'QuickTime:TrackCreateDate': ExtractedData(
            wrapper=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.datetime, probability=1),
                fields.WeightedMapping(fields.date, probability=1)
            ],
            generic_field=fields.GenericDateCreated
        ),
        'QuickTime:TrackModifyDate': ExtractedData(
            wrapper=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.datetime, probability=0.5),
                fields.WeightedMapping(fields.date, probability=0.5)
            ],
            generic_field=fields.GenericDateModified
        ),
        'QuickTime:MediaCreateDate': ExtractedData(
            wrapper=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.datetime, probability=1),
                fields.WeightedMapping(fields.date, probability=1)
            ],
            generic_field=fields.GenericDateCreated
        ),
        'QuickTime:MediaModifyDate': ExtractedData(
            wrapper=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                fields.WeightedMapping(fields.datetime, probability=0.5),
                fields.WeightedMapping(fields.date, probability=0.5)
            ],
            generic_field=fields.GenericDateModified
        ),

        # TODO: [TD0084] Add handling collections to type wrapper classes.
        # 'XMP:Subject': ExtractedData(
        #     wrapper=types.AW_STRINGLIST,
        #     mapped_fields=[
        #         fields.WeightedMapping(fields.tags, probability=1),
        #         fields.WeightedMapping(fields.title, probability=0.9)
        #         fields.WeightedMapping(fields.description, probability=0.8)
        #     ]
        # ),
        # TODO: [TD0084] Add handling collections to type wrapper classes.
        # 'XMP:TagsList': ExtractedData(
        #     wrapper=types.AW_STRINGLIST,
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
            if tag_name in self.tagname_type_lookup:
                wrapper = self.tagname_type_lookup[tag_name]
            else:
                # Use a default 'ExtractedData' class.
                wrapper = ExtractedData(wrapper=None, mapped_fields=None)

            try:
                item = wrapper(value)
            except types.AWTypeError:
                self.log.warning('Wrapping exiftool data raised AWTypeError '
                                 'for "{!s}" ({})'.format(value, type(value)))
                pass
            else:
                out[tag_name] = item

        return out

    def _get_exiftool_data(self, source):
        """
        Returns:
            Exiftool results as a dictionary of strings/ints/floats.
        """
        with wrap_exiftool.ExifTool() as et:
            try:
                return et.get_metadata(source)
            except (AttributeError, ValueError, TypeError) as e:
                # Raises ValueError if an ExifTool instance isn't running.
                raise ExtractorError(e)

    @classmethod
    def check_dependencies(cls):
        return util.is_executable('exiftool')
