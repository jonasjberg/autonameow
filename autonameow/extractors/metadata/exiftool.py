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
    model,
    types,
    util
)
from core.model import (
    ExtractedData,
    WeightedMapping
)
from core.namebuilder import fields
from extractors import (
    BaseExtractor,
    ExtractorError
)
from thirdparty import pyexiftool


IGNORED_EXIFTOOL_TAGNAMES = frozenset([
    'ExifTool:ExifToolVersion'
])


class ExiftoolMetadataExtractor(BaseExtractor):
    """
    Extracts various types of metadata using "exiftool".
    """
    HANDLES_MIME_TYPES = ['video/*', 'application/pdf', 'image/*',
                          'application/epub+zip', 'text/*']

    EXTRACTEDDATA_WRAPPER_LOOKUP = {
        'ASF:CreationDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            generic_field=model.GenericDateCreated
        ),
        'ASF:ImageHeight': ExtractedData(types.AW_INTEGER),
        'ASF:ImageWidth': ExtractedData(types.AW_INTEGER),
        'ASF:VideoCodecName': ExtractedData(types.AW_STRING),
        'Composite:Aperture': ExtractedData(types.AW_FLOAT),
        'Composite:ImageSize': ExtractedData(types.AW_STRING),
        'Composite:Megapixels': ExtractedData(types.AW_FLOAT),
        'Composite:HyperfocalDistance': ExtractedData(types.AW_FLOAT),
        # 'ExifTool:ExifToolVersion': ExtractedData(types.AW_FLOAT),
        'EXIF:CreateDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            generic_field=model.GenericDateCreated
        ),
        'EXIF:DateTimeDigitized': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            generic_field=model.GenericDateCreated
        ),
        'EXIF:DateTimeOriginal': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            generic_field=model.GenericDateCreated
        ),
        'EXIF:ExifVersion': ExtractedData(types.AW_INTEGER),
        'EXIF:GainControl': ExtractedData(types.AW_INTEGER),
        # TODO: Handle GPS date/time-information.
        #       EXIF:GPSTimeStamp: '12:07:59'
        #       EXIF:GPSDateStamp: '2016:03:26'

        # 'EXIF:GPSTimeStamp': ExtractedData(
        #     coercer=types.AW_EXIFTOOLTIMEDATE,
        #     mapped_fields=[
        #         fields.WeightedMapping(fields.Time, probability=1),
        #     ]
        # ),
        'EXIF:GPSDateStamp': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.Date, probability=1),
            ],
            generic_field=model.GenericDateCreated
        ),
        'EXIF:ImageDescription': ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                WeightedMapping(fields.Description, probability=1),
                WeightedMapping(fields.Tags, probability=0.5),
                WeightedMapping(fields.Title, probability=0.25)
            ],
            generic_field=model.GenericDescription
        ),
        'EXIF:Make': ExtractedData(types.AW_STRING),
        'EXIF:Model': ExtractedData(types.AW_STRING),
        'EXIF:ModifyDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=0.25),
                WeightedMapping(fields.Date, probability=0.25)
            ],
            generic_field=model.GenericDateModified
        ),
        'EXIF:Software': ExtractedData(types.AW_STRING),
        'EXIF:UserComment': ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                WeightedMapping(fields.Description, probability=0.5),
                WeightedMapping(fields.Tags, probability=0.5)
            ],
            generic_field=model.GenericDateModified
        ),
        'File:Directory': ExtractedData(types.AW_PATH),
        'File:FileAccessDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=0.01),
                WeightedMapping(fields.Date, probability=0.01)
            ],
            generic_field=model.GenericDateModified
        ),
        'File:FileInodeChangeDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=0.01),
                WeightedMapping(fields.Date, probability=0.01)
            ],
            generic_field=model.GenericDateModified
        ),
        'File:FileModifyDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=0.25),
                WeightedMapping(fields.Date, probability=0.25)
            ],
            generic_field=model.GenericDateModified
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
                WeightedMapping(fields.Extension, probability=1)
            ],
            generic_field=model.GenericMimeType
        ),
        'PDF:Author': ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                WeightedMapping(fields.Author, probability=1),
            ],
            generic_field=model.GenericAuthor
        ),
        'PDF:CreateDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            generic_field=model.GenericDateCreated
        ),
        'PDF:Creator': ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                WeightedMapping(fields.Creator, probability=1),
                WeightedMapping(fields.Author, probability=0.025),
                WeightedMapping(fields.Publisher, probability=0.02),
                WeightedMapping(fields.Title, probability=0.01)
            ],
            generic_field=model.GenericCreator
        ),
        'PDF:Keywords': ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                WeightedMapping(fields.Tags, probability=1),
            ],
            generic_field=model.GenericTags
        ),
        'PDF:Linearized': ExtractedData(types.AW_BOOLEAN),
        'PDF:ModifyDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=0.25),
                WeightedMapping(fields.Date, probability=0.25)
            ],
            generic_field=model.GenericDateModified
        ),
        'PDF:PDFVersion': ExtractedData(types.AW_FLOAT),
        'PDF:PageCount': ExtractedData(types.AW_INTEGER),
        'PDF:Producer': ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                WeightedMapping(fields.Publisher, probability=0.25),
                WeightedMapping(fields.Author, probability=0.02),
                WeightedMapping(fields.Title, probability=0.01)
            ],
            generic_field=model.GenericProducer
        ),
        'PDF:Title': ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                WeightedMapping(fields.Title, probability=1)
            ],
            generic_field=model.GenericTitle
        ),
        'SourceFile': ExtractedData(types.AW_PATH),
        'QuickTime:CreateDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            generic_field=model.GenericDateCreated
        ),
        'QuickTime:CreationDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            generic_field=model.GenericDateCreated
        ),
        'QuickTime:ModifyDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=0.5),
                WeightedMapping(fields.Date, probability=0.5)
            ],
            generic_field=model.GenericDateModified
        ),
        'QuickTime:CreationDate-und-SE': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            generic_field=model.GenericDateCreated
        ),
        'QuickTime:TrackCreateDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            generic_field=model.GenericDateCreated
        ),
        'QuickTime:TrackModifyDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=0.5),
                WeightedMapping(fields.Date, probability=0.5)
            ],
            generic_field=model.GenericDateModified
        ),
        'QuickTime:MediaCreateDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            generic_field=model.GenericDateCreated
        ),
        'QuickTime:MediaModifyDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=0.5),
                WeightedMapping(fields.Date, probability=0.5)
            ],
            generic_field=model.GenericDateModified
        ),
        'XMP:About': ExtractedData(types.AW_STRING),
        'XMP:CreateDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            generic_field=model.GenericDateCreated
        ),
        'XMP:Creator': ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                WeightedMapping(fields.Author, probability=1),
                WeightedMapping(fields.Creator, probability=0.5),
                WeightedMapping(fields.Publisher, probability=0.02),
                WeightedMapping(fields.Title, probability=0.01)
            ],
            generic_field=model.GenericAuthor
        ),
        'XMP:CreatorTool': ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                WeightedMapping(fields.Creator, probability=1),
                WeightedMapping(fields.Author, probability=0.025),
                WeightedMapping(fields.Publisher, probability=0.02),
                WeightedMapping(fields.Title, probability=0.01)
            ],
            generic_field=model.GenericCreator
        ),
        'XMP:DocumentID': ExtractedData(types.AW_STRING),
        'XMP:Format': ExtractedData(
            coercer=types.AW_MIMETYPE,
            mapped_fields=[
                WeightedMapping(fields.Extension, probability=0.75)
            ],
            generic_field=model.GenericMimeType
        ),
        'XMP:Keywords': ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                WeightedMapping(fields.Tags, probability=1),
                WeightedMapping(fields.Title, probability=0.5),
                WeightedMapping(fields.Description, probability=0.8)
            ],
            generic_field=model.GenericTags
        ),
        'XMP:MetadataDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=0.25),
                WeightedMapping(fields.Date, probability=0.25)
            ],
            generic_field=model.GenericDateModified
        ),
        'XMP:ModifyDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=0.25),
                WeightedMapping(fields.Date, probability=0.25)
            ],
            generic_field=model.GenericDateModified
        ),
        'XMP:Producer': ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                WeightedMapping(fields.Publisher, probability=0.25),
                WeightedMapping(fields.Author, probability=0.02),
                WeightedMapping(fields.Title, probability=0.01)
            ],
            generic_field=model.GenericProducer
        ),
        'XMP:Subject': ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                WeightedMapping(fields.Description, probability=1),
                WeightedMapping(fields.Tags, probability=0.8),
                WeightedMapping(fields.Title, probability=0.5)
            ],
            generic_field=model.GenericSubject
        ),
        'XMP:TagsList': ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                WeightedMapping(fields.Tags, probability=1),
                WeightedMapping(fields.Title, probability=0.5),
                WeightedMapping(fields.Description, probability=0.8)
            ],
            generic_field=model.GenericTags
        ),
        'XMP:Title': ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                WeightedMapping(fields.Title, probability=1)
            ],
            generic_field=model.GenericTitle
        ),
        'XMP:XMPToolkit': ExtractedData(types.AW_STRING),
    }

    def __init__(self):
        super(ExiftoolMetadataExtractor, self).__init__()

    def execute(self, fileobject, **kwargs):
        self.log.debug('{!s}: Starting extraction'.format(self))
        source = fileobject.abspath

        try:
            _metadata = self._get_metadata(source)
        except NotImplementedError as e:
            raise ExtractorError('Called unimplemented code in {!s}: '
                                 '{!s}'.format(self, e))

        self.log.debug('{!s}: Completed extraction'.format(self))
        return _metadata

    def _get_metadata(self, source):
        _raw_metadata = _get_exiftool_data(source)
        if _raw_metadata:
            # Internal data format boundary.  Wrap "raw" data with type classes.
            metadata = self._to_internal_format(_raw_metadata)
            return metadata

    def _to_internal_format(self, raw_metadata):
        out = {}

        for tag_name, value in raw_metadata.items():
            if value is None:
                continue
            if is_ignored_tagname(tag_name):
                continue
            if is_binary_blob(value):
                continue

            # TODO: [TD0084] Add handling collections to type wrapper classes.
            if isinstance(value, list):
                for v in value:
                    _wrapped = self._wrap_tag_value(tag_name, v)
                    if not _wrapped:
                        continue

                    _any_existing = out.get(tag_name)
                    if _any_existing:
                        if not isinstance(_any_existing, list):
                            _any_existing = [_any_existing]
                        out[tag_name] = _any_existing + [_wrapped]
                    else:
                        out[tag_name] = [_wrapped]
            else:
                _wrapped = self._wrap_tag_value(tag_name, value)
                if _wrapped:
                    out[tag_name] = _wrapped

        return out

    def _wrap_tag_value(self, tagname, value):
        wrapper = self.EXTRACTEDDATA_WRAPPER_LOOKUP.get(tagname)
        if not wrapper:
            wrapper = ExtractedData(coercer=None, mapped_fields=None)

        wrapped = ExtractedData.from_raw(wrapper, value)
        if wrapped:
            return wrapped
        else:
            self.log.debug('Wrapping exiftool data returned None '
                           'for "{!s}" ({})'.format(value, type(value)))

    @classmethod
    def check_dependencies(cls):
        return util.is_executable('exiftool') and pyexiftool is not None


def is_binary_blob(value):
    return isinstance(value, str) and 'use -b option to extract' in value


def is_ignored_tagname(tagname):
    return bool(tagname in IGNORED_EXIFTOOL_TAGNAMES)


def _get_exiftool_data(source):
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