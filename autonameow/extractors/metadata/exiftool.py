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
    util
)
from core.model import (
    ExtractedData,
    WeightedMapping
)
from core.model import genericfields as gf
from core.namebuilder import fields
from extractors import (
    BaseExtractor,
    ExtractorError
)
from thirdparty import pyexiftool


IGNORED_EXIFTOOL_TAGNAMES = frozenset([
    'ExifTool:ExifToolVersion',
    'XMP:PageImage'
])


# Metadata to ignore per field. Note that the values are set literals.
BAD_EXIFTOOL_METADATA = {
    'PDF:Author': {'Author'},
    'PDF:Subject': {'Subject'},
    'PDF:Title': {'Title'},
    'XMP:Author': {'Author', 'Creator'},
    'XMP:Creator': {'Author', 'Creator'},
    'XMP:Description': {'Subject', 'Description'},
    'XMP:Subject': {'Subject', 'Description'},
    'XMP:Title': {'Title'}
}


class ExiftoolMetadataExtractor(BaseExtractor):
    """
    Extracts various types of metadata using "exiftool".
    """
    HANDLES_MIME_TYPES = ['video/*', 'application/pdf', 'image/*',
                          'application/epub+zip', 'text/*']
    is_slow = False

    COERCER_LOOKUP = {
        'ASF:CreationDate': types.AW_EXIFTOOLTIMEDATE,
        'ASF:ImageHeight': types.AW_INTEGER,
        'ASF:ImageWidth': types.AW_INTEGER,
        'ASF:VideoCodecName': types.AW_STRING,
        'Composite:Aperture': types.AW_FLOAT,
        'Composite:ImageSize': types.AW_STRING,
        'Composite:Megapixels': types.AW_FLOAT,
        'Composite:HyperfocalDistance': types.AW_FLOAT,
        'EXIF:CreateDate': types.AW_EXIFTOOLTIMEDATE,
        'EXIF:DateTimeDigitized': types.AW_EXIFTOOLTIMEDATE,
        'EXIF:DateTimeOriginal': types.AW_EXIFTOOLTIMEDATE,
        'EXIF:ExifVersion': types.AW_INTEGER,
        'EXIF:GainControl': types.AW_INTEGER,
        # TODO: Handle GPS date/time-information.
        #       EXIF:GPSTimeStamp: '12:07:59'
        #       EXIF:GPSDateStamp: '2016:03:26'

        # 'EXIF:GPSTimeStamp': coercer=types.AW_EXIFTOOLTIMEDATE,
        'EXIF:GPSDateStamp': types.AW_EXIFTOOLTIMEDATE,
        'EXIF:ImageDescription': types.AW_STRING,
        'EXIF:Make': types.AW_STRING,
        'EXIF:Model': types.AW_STRING,
        'EXIF:ModifyDate': types.AW_EXIFTOOLTIMEDATE,
        'EXIF:Software': types.AW_STRING,
        'EXIF:UserComment': types.AW_STRING,
        'File:Directory': types.AW_PATH,
        'File:FileAccessDate': types.AW_EXIFTOOLTIMEDATE,
        'File:FileInodeChangeDate': types.AW_EXIFTOOLTIMEDATE,
        'File:FileModifyDate': types.AW_EXIFTOOLTIMEDATE,
        'File:FileName': types.AW_PATH,
        'File:FilePermissions': types.AW_INTEGER,
        'File:FileSize': types.AW_INTEGER,
        'File:FileType': types.AW_STRING,
        'File:FileTypeExtension': types.AW_PATHCOMPONENT,
        'File:ImageHeight': types.AW_INTEGER,
        'File:ImageWidth': types.AW_INTEGER,
        'File:MIMEType': types.AW_MIMETYPE,
        'PDF:Author': types.AW_STRING,
        'PDF:CreateDate': types.AW_EXIFTOOLTIMEDATE,
        'PDF:Creator': types.AW_STRING,
        'PDF:Keywords': types.AW_STRING,
        'PDF:Linearized': types.AW_BOOLEAN,
        'PDF:ModifyDate': types.AW_EXIFTOOLTIMEDATE,
        'PDF:PDFVersion': types.AW_FLOAT,
        'PDF:PageCount': types.AW_INTEGER,
        'PDF:Producer': types.AW_STRING,
        'PDF:Subject': types.AW_STRING,
        'PDF:Title': types.AW_STRING,
        'PDF:Trapped': types.AW_BOOLEAN,
        'SourceFile': types.AW_PATH,
        'QuickTime:CompatibleBrands': types.AW_STRING,
        'QuickTime:CreateDate': types.AW_EXIFTOOLTIMEDATE,
        'QuickTime:CreationDate': types.AW_EXIFTOOLTIMEDATE,
        'QuickTime:ModifyDate': types.AW_EXIFTOOLTIMEDATE,
        'QuickTime:CreationDate-und-SE': types.AW_EXIFTOOLTIMEDATE,
        'QuickTime:TrackCreateDate': types.AW_EXIFTOOLTIMEDATE,
        'QuickTime:TrackModifyDate': types.AW_EXIFTOOLTIMEDATE,
        'QuickTime:MediaCreateDate': types.AW_EXIFTOOLTIMEDATE,
        'QuickTime:MediaModifyDate': types.AW_EXIFTOOLTIMEDATE,
        'XMP:About': types.AW_STRING,
        'XMP:CreateDate': types.AW_EXIFTOOLTIMEDATE,
        'XMP:Creator': types.AW_STRING,
        'XMP:CreatorTool': types.AW_STRING,
        'XMP:DocumentID': types.AW_STRING,
        'XMP:Format': types.AW_MIMETYPE,
        'XMP:HistoryAction': types.AW_STRING,
        'XMP:HistoryChanged': types.AW_STRING,
        'XMP:HistoryInstanceID': types.AW_STRING,
        'XMP:HistoryParameters': types.AW_STRING,
        'XMP:HistorySoftwareAgent': types.AW_STRING,
        'XMP:HistoryWhen': types.AW_TIMEDATE,
        'XMP:Keywords': types.AW_STRING,
        'XMP:ManifestLinkForm': types.AW_STRING,
        'XMP:ManifestReferenceInstanceID': types.AW_STRING,
        'XMP:ManifestReferenceDocumentID': types.AW_STRING,
        'XMP:MetadataDate': types.AW_EXIFTOOLTIMEDATE,
        'XMP:ModifyDate': types.AW_EXIFTOOLTIMEDATE,
        'XMP:Producer': types.AW_STRING,
        'XMP:Subject': types.AW_STRING,
        'XMP:TagsList': types.AW_STRING,
        'XMP:Title': types.AW_STRING,
        'XMP:XMPToolkit': types.AW_STRING,
    }

    METAINFO_LOOKUP = {
        'ASF:CreationDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            generic_field=gf.GenericDateCreated
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
            generic_field=gf.GenericDateCreated
        ),
        'EXIF:DateTimeDigitized': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            generic_field=gf.GenericDateCreated
        ),
        'EXIF:DateTimeOriginal': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            generic_field=gf.GenericDateCreated
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
            generic_field=gf.GenericDateCreated
        ),
        'EXIF:ImageDescription': ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                WeightedMapping(fields.Description, probability=1),
                WeightedMapping(fields.Tags, probability=0.5),
                WeightedMapping(fields.Title, probability=0.25)
            ],
            generic_field=gf.GenericDescription
        ),
        'EXIF:Make': ExtractedData(types.AW_STRING),
        'EXIF:Model': ExtractedData(types.AW_STRING),
        'EXIF:ModifyDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=0.25),
                WeightedMapping(fields.Date, probability=0.25)
            ],
            generic_field=gf.GenericDateModified
        ),
        'EXIF:Software': ExtractedData(types.AW_STRING),
        'EXIF:UserComment': ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                WeightedMapping(fields.Description, probability=0.5),
                WeightedMapping(fields.Tags, probability=0.5)
            ],
            generic_field=gf.GenericDateModified
        ),
        'File:Directory': ExtractedData(types.AW_PATH),
        'File:FileAccessDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=0.01),
                WeightedMapping(fields.Date, probability=0.01)
            ],
            generic_field=gf.GenericDateModified
        ),
        'File:FileInodeChangeDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=0.01),
                WeightedMapping(fields.Date, probability=0.01)
            ],
            generic_field=gf.GenericDateModified
        ),
        'File:FileModifyDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=0.25),
                WeightedMapping(fields.Date, probability=0.25)
            ],
            generic_field=gf.GenericDateModified
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
            generic_field=gf.GenericMimeType
        ),
        'PDF:Author': ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                WeightedMapping(fields.Author, probability=1),
            ],
            generic_field=gf.GenericAuthor
        ),
        'PDF:CreateDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            generic_field=gf.GenericDateCreated
        ),
        'PDF:Creator': ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                WeightedMapping(fields.Creator, probability=1),
                WeightedMapping(fields.Author, probability=0.025),
                WeightedMapping(fields.Publisher, probability=0.02),
                WeightedMapping(fields.Title, probability=0.01)
            ],
            generic_field=gf.GenericCreator
        ),
        'PDF:Keywords': ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                WeightedMapping(fields.Tags, probability=1),
            ],
            generic_field=gf.GenericTags,
            multivalued=True
        ),
        'PDF:Linearized': ExtractedData(types.AW_BOOLEAN),
        'PDF:ModifyDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=0.25),
                WeightedMapping(fields.Date, probability=0.25)
            ],
            generic_field=gf.GenericDateModified
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
            generic_field=gf.GenericProducer
        ),
        'PDF:Subject': ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                WeightedMapping(fields.Description, probability=1),
                WeightedMapping(fields.Tags, probability=0.8),
                WeightedMapping(fields.Title, probability=0.5)
            ],
            generic_field=gf.GenericSubject,
            # multivalued=True
        ),
        'PDF:Title': ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                WeightedMapping(fields.Title, probability=1)
            ],
            generic_field=gf.GenericTitle
        ),
        'PDF:Trapped': ExtractedData(
            coercer=types.AW_BOOLEAN
        ),
        'SourceFile': ExtractedData(types.AW_PATH),
        'QuickTime:CompatibleBrands': ExtractedData(
            coercer=types.AW_STRING,
            multivalued=True
        ),
        'QuickTime:CreateDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            generic_field=gf.GenericDateCreated
        ),
        'QuickTime:CreationDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            generic_field=gf.GenericDateCreated
        ),
        'QuickTime:ModifyDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=0.5),
                WeightedMapping(fields.Date, probability=0.5)
            ],
            generic_field=gf.GenericDateModified
        ),
        'QuickTime:CreationDate-und-SE': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            generic_field=gf.GenericDateCreated
        ),
        'QuickTime:TrackCreateDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            generic_field=gf.GenericDateCreated
        ),
        'QuickTime:TrackModifyDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=0.5),
                WeightedMapping(fields.Date, probability=0.5)
            ],
            generic_field=gf.GenericDateModified
        ),
        'QuickTime:MediaCreateDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            generic_field=gf.GenericDateCreated
        ),
        'QuickTime:MediaModifyDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=0.5),
                WeightedMapping(fields.Date, probability=0.5)
            ],
            generic_field=gf.GenericDateModified
        ),
        'XMP:About': ExtractedData(types.AW_STRING),
        'XMP:CreateDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            generic_field=gf.GenericDateCreated
        ),
        'XMP:Creator': ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                WeightedMapping(fields.Author, probability=1),
                WeightedMapping(fields.Creator, probability=0.5),
                WeightedMapping(fields.Publisher, probability=0.02),
                WeightedMapping(fields.Title, probability=0.01)
            ],
            generic_field=gf.GenericAuthor
        ),
        'XMP:CreatorTool': ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                WeightedMapping(fields.Creator, probability=1),
                WeightedMapping(fields.Author, probability=0.025),
                WeightedMapping(fields.Publisher, probability=0.02),
                WeightedMapping(fields.Title, probability=0.01)
            ],
            generic_field=gf.GenericCreator
        ),
        'XMP:DocumentID': ExtractedData(types.AW_STRING),
        'XMP:Format': ExtractedData(
            coercer=types.AW_MIMETYPE,
            mapped_fields=[
                WeightedMapping(fields.Extension, probability=0.75)
            ],
            generic_field=gf.GenericMimeType
        ),
        'XMP:HistoryAction': ExtractedData(
            coercer=types.AW_STRING,
            multivalued=True
        ),
        'XMP:HistoryChanged': ExtractedData(
            coercer=types.AW_STRING,
            multivalued=True
        ),
        'XMP:HistoryInstanceID': ExtractedData(
            coercer=types.AW_STRING,
            multivalued=True
        ),
        'XMP:HistoryParameters': ExtractedData(
            coercer=types.AW_STRING,
            multivalued=True
        ),
        'XMP:HistorySoftwareAgent': ExtractedData(
            coercer=types.AW_STRING,
            multivalued=True
        ),
        'XMP:HistoryWhen': ExtractedData(
            coercer=types.AW_TIMEDATE,
            multivalued=True
        ),
        'XMP:Keywords': ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                WeightedMapping(fields.Tags, probability=1),
                WeightedMapping(fields.Title, probability=0.5),
                WeightedMapping(fields.Description, probability=0.8)
            ],
            generic_field=gf.GenericTags
        ),
        'XMP:ManifestLinkForm': ExtractedData(
            coercer=types.AW_STRING,
            multivalued=True
        ),
        'XMP:ManifestReferenceInstanceID': ExtractedData(
            coercer=types.AW_STRING,
            multivalued=True
        ),
        'XMP:ManifestReferenceDocumentID': ExtractedData(
            coercer=types.AW_STRING,
            multivalued=True
        ),
        'XMP:MetadataDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=0.25),
                WeightedMapping(fields.Date, probability=0.25)
            ],
            generic_field=gf.GenericDateModified
        ),
        'XMP:ModifyDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=0.25),
                WeightedMapping(fields.Date, probability=0.25)
            ],
            generic_field=gf.GenericDateModified
        ),
        'XMP:Producer': ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                WeightedMapping(fields.Publisher, probability=0.25),
                WeightedMapping(fields.Author, probability=0.02),
                WeightedMapping(fields.Title, probability=0.01)
            ],
            generic_field=gf.GenericProducer
        ),
        'XMP:Subject': ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                WeightedMapping(fields.Description, probability=1),
                WeightedMapping(fields.Tags, probability=0.8),
                WeightedMapping(fields.Title, probability=0.5)
            ],
            generic_field=gf.GenericSubject,
            multivalued=True
        ),
        'XMP:TagsList': ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                WeightedMapping(fields.Tags, probability=1),
                WeightedMapping(fields.Title, probability=0.5),
                WeightedMapping(fields.Description, probability=0.8)
            ],
            generic_field=gf.GenericTags
        ),
        'XMP:Title': ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                WeightedMapping(fields.Title, probability=1)
            ],
            generic_field=gf.GenericTitle
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

    def metainfo(self, fileobject, **kwargs):
        pass

    def extract(self, fileobject, **kwargs):
        pass

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

            if not is_bad_metadata(tag_name, value):
                _wrapped = self._wrap_tag_value(tag_name, value)
                if _wrapped:
                    _wrapped.source = self
                    out[tag_name] = _wrapped

        return out

    def _wrap_tag_value(self, tagname, value):
        # TODO: [TD0119] Separate adding contextual information from coercion.
        wrapper = self.COERCER_LOOKUP.get(tagname)
        if not wrapper:
            self.log.debug(
                'Coercer unspecified for tag: "{!s}" with'
                ' value: "{!s}"'.format(tagname, value)
            )
            wrapper = ExtractedData(coercer=None, mapped_fields=None)

        # TODO: [TD0084] Add handling collections to type wrapper classes.
        if isinstance(value, list):
            if not wrapper.multivalued:
                self.log.warning(
                    'Got list but "ExtractedData" wrapper is not multivalued.'
                    ' Tag: "{!s}" Value: "{!s}"'.format(tagname, value)
                )
                return

        wrapped = ExtractedData.from_raw(wrapper, value)
        if wrapped:
            return wrapped
        else:
            self.log.debug('Wrapping exiftool data returned None '
                           'for "{!s}" ({})'.format(value, type(value)))

    @classmethod
    def check_dependencies(cls):
        return util.is_executable('exiftool') and pyexiftool is not None


def is_bad_metadata(tag_name, value):
    if tag_name in BAD_EXIFTOOL_METADATA:
        if isinstance(value, list):
            for v in value:
                if v in BAD_EXIFTOOL_METADATA[tag_name]:
                    return True
            return False
        else:
            if value in BAD_EXIFTOOL_METADATA[tag_name]:
                return True
    return False


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
