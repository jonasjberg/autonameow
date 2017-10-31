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
    WeightedMapping,
    MetaInfo
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

    EXTRACTEDDATA_LOOKUP = {
        'ASF:CreationDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
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
        ),
        'EXIF:DateTimeDigitized': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
        ),
        'EXIF:DateTimeOriginal': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
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
        ),
        'EXIF:ImageDescription': ExtractedData(
            coercer=types.AW_STRING,
        ),
        'EXIF:Make': ExtractedData(types.AW_STRING),
        'EXIF:Model': ExtractedData(types.AW_STRING),
        'EXIF:ModifyDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
        ),
        'EXIF:Software': ExtractedData(types.AW_STRING),
        'EXIF:UserComment': ExtractedData(
            coercer=types.AW_STRING,
        ),
        'File:Directory': ExtractedData(types.AW_PATH),
        'File:FileAccessDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
        ),
        'File:FileInodeChangeDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
        ),
        'File:FileModifyDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
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
        ),
        'PDF:Author': ExtractedData(
            coercer=types.AW_STRING,
        ),
        'PDF:CreateDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
        ),
        'PDF:Creator': ExtractedData(
            coercer=types.AW_STRING,
        ),
        'PDF:Keywords': ExtractedData(
            coercer=types.AW_STRING,
            multivalued=True
        ),
        'PDF:Linearized': ExtractedData(types.AW_BOOLEAN),
        'PDF:ModifyDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
        ),
        'PDF:PDFVersion': ExtractedData(types.AW_FLOAT),
        'PDF:PageCount': ExtractedData(types.AW_INTEGER),
        'PDF:Producer': ExtractedData(
            coercer=types.AW_STRING,
        ),
        'PDF:Subject': ExtractedData(
            coercer=types.AW_STRING,
            # multivalued=True
        ),
        'PDF:Title': ExtractedData(
            coercer=types.AW_STRING,
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
        ),
        'QuickTime:CreationDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
        ),
        'QuickTime:ModifyDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
        ),
        'QuickTime:CreationDate-und-SE': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
        ),
        'QuickTime:TrackCreateDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
        ),
        'QuickTime:TrackModifyDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
        ),
        'QuickTime:MediaCreateDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
        ),
        'QuickTime:MediaModifyDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
        ),
        'XMP:About': ExtractedData(types.AW_STRING),
        'XMP:CreateDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
        ),
        'XMP:Creator': ExtractedData(
            coercer=types.AW_STRING,
        ),
        'XMP:CreatorTool': ExtractedData(
            coercer=types.AW_STRING,
        ),
        'XMP:DocumentID': ExtractedData(types.AW_STRING),
        'XMP:Format': ExtractedData(
            coercer=types.AW_MIMETYPE,
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
        ),
        'XMP:ModifyDate': ExtractedData(
            coercer=types.AW_EXIFTOOLTIMEDATE,
        ),
        'XMP:Producer': ExtractedData(
            coercer=types.AW_STRING,
        ),
        'XMP:Subject': ExtractedData(
            coercer=types.AW_STRING,
            multivalued=True
        ),
        'XMP:TagsList': ExtractedData(
            coercer=types.AW_STRING,
        ),
        'XMP:Title': ExtractedData(
            coercer=types.AW_STRING,
        ),
        'XMP:XMPToolkit': ExtractedData(types.AW_STRING),
    }

    METAINFO_LOOKUP = {
        'ASF:CreationDate': MetaInfo(
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            generic_field=gf.GenericDateCreated
        ),
        'ASF:ImageHeight': None,
        'ASF:ImageWidth': None,
        'ASF:VideoCodecName': None,
        'Composite:Aperture': None,
        'Composite:ImageSize': None,
        'Composite:Megapixels': None,
        'Composite:HyperfocalDistance': None,
        # 'ExifTool:ExifToolVersion': MetaInfo(types.AW_FLOAT),
        'EXIF:CreateDate': MetaInfo(
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            generic_field=gf.GenericDateCreated
        ),
        'EXIF:DateTimeDigitized': MetaInfo(
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            generic_field=gf.GenericDateCreated
        ),
        'EXIF:DateTimeOriginal': MetaInfo(
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            generic_field=gf.GenericDateCreated
        ),
        'EXIF:ExifVersion': MetaInfo(types.AW_INTEGER),
        'EXIF:GainControl': MetaInfo(types.AW_INTEGER),
        # TODO: Handle GPS date/time-information.
        #       EXIF:GPSTimeStamp: '12:07:59'
        #       EXIF:GPSDateStamp: '2016:03:26'

        # 'EXIF:GPSTimeStamp': MetaInfo(
        #     mapped_fields=[
        #         fields.WeightedMapping(fields.Time, probability=1),
        #     ]
        # ),
        'EXIF:GPSDateStamp': MetaInfo(
            mapped_fields=[
                WeightedMapping(fields.Date, probability=1),
            ],
            generic_field=gf.GenericDateCreated
        ),
        'EXIF:ImageDescription': MetaInfo(
            mapped_fields=[
                WeightedMapping(fields.Description, probability=1),
                WeightedMapping(fields.Tags, probability=0.5),
                WeightedMapping(fields.Title, probability=0.25)
            ],
            generic_field=gf.GenericDescription
        ),
        'EXIF:Make': MetaInfo(types.AW_STRING),
        'EXIF:Model': MetaInfo(types.AW_STRING),
        'EXIF:ModifyDate': MetaInfo(
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=0.25),
                WeightedMapping(fields.Date, probability=0.25)
            ],
            generic_field=gf.GenericDateModified
        ),
        'EXIF:Software': MetaInfo(types.AW_STRING),
        'EXIF:UserComment': MetaInfo(
            mapped_fields=[
                WeightedMapping(fields.Description, probability=0.5),
                WeightedMapping(fields.Tags, probability=0.5)
            ],
            generic_field=gf.GenericDateModified
        ),
        'File:Directory': MetaInfo(types.AW_PATH),
        'File:FileAccessDate': MetaInfo(
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=0.01),
                WeightedMapping(fields.Date, probability=0.01)
            ],
            generic_field=gf.GenericDateModified
        ),
        'File:FileInodeChangeDate': MetaInfo(
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=0.01),
                WeightedMapping(fields.Date, probability=0.01)
            ],
            generic_field=gf.GenericDateModified
        ),
        'File:FileModifyDate': MetaInfo(
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=0.25),
                WeightedMapping(fields.Date, probability=0.25)
            ],
            generic_field=gf.GenericDateModified
        ),
        'File:FileName': MetaInfo(types.AW_PATH),
        'File:FilePermissions': MetaInfo(types.AW_INTEGER),
        'File:FileSize': MetaInfo(types.AW_INTEGER),
        'File:FileType': MetaInfo(types.AW_STRING),
        'File:FileTypeExtension': MetaInfo(types.AW_PATHCOMPONENT),
        'File:ImageHeight': MetaInfo(types.AW_INTEGER),
        'File:ImageWidth': MetaInfo(types.AW_INTEGER),
        'File:MIMEType': MetaInfo(
            mapped_fields=[
                WeightedMapping(fields.Extension, probability=1)
            ],
            generic_field=gf.GenericMimeType
        ),
        'PDF:Author': MetaInfo(
            mapped_fields=[
                WeightedMapping(fields.Author, probability=1),
            ],
            generic_field=gf.GenericAuthor
        ),
        'PDF:CreateDate': MetaInfo(
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            generic_field=gf.GenericDateCreated
        ),
        'PDF:Creator': MetaInfo(
            mapped_fields=[
                WeightedMapping(fields.Creator, probability=1),
                WeightedMapping(fields.Author, probability=0.025),
                WeightedMapping(fields.Publisher, probability=0.02),
                WeightedMapping(fields.Title, probability=0.01)
            ],
            generic_field=gf.GenericCreator
        ),
        'PDF:Keywords': MetaInfo(
            mapped_fields=[
                WeightedMapping(fields.Tags, probability=1),
            ],
            generic_field=gf.GenericTags,
            multivalued=True
        ),
        'PDF:Linearized': MetaInfo(types.AW_BOOLEAN),
        'PDF:ModifyDate': MetaInfo(
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=0.25),
                WeightedMapping(fields.Date, probability=0.25)
            ],
            generic_field=gf.GenericDateModified
        ),
        'PDF:PDFVersion': MetaInfo(types.AW_FLOAT),
        'PDF:PageCount': MetaInfo(types.AW_INTEGER),
        'PDF:Producer': MetaInfo(
            mapped_fields=[
                WeightedMapping(fields.Publisher, probability=0.25),
                WeightedMapping(fields.Author, probability=0.02),
                WeightedMapping(fields.Title, probability=0.01)
            ],
            generic_field=gf.GenericProducer
        ),
        'PDF:Subject': MetaInfo(
            mapped_fields=[
                WeightedMapping(fields.Description, probability=1),
                WeightedMapping(fields.Tags, probability=0.8),
                WeightedMapping(fields.Title, probability=0.5)
            ],
            generic_field=gf.GenericSubject,
            # multivalued=True
        ),
        'PDF:Title': MetaInfo(
            mapped_fields=[
                WeightedMapping(fields.Title, probability=1)
            ],
            generic_field=gf.GenericTitle
        ),
        'PDF:Trapped': MetaInfo(
        ),
        'SourceFile': MetaInfo(types.AW_PATH),
        'QuickTime:CompatibleBrands': MetaInfo(
            multivalued=True
        ),
        'QuickTime:CreateDate': MetaInfo(
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            generic_field=gf.GenericDateCreated
        ),
        'QuickTime:CreationDate': MetaInfo(
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            generic_field=gf.GenericDateCreated
        ),
        'QuickTime:ModifyDate': MetaInfo(
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=0.5),
                WeightedMapping(fields.Date, probability=0.5)
            ],
            generic_field=gf.GenericDateModified
        ),
        'QuickTime:CreationDate-und-SE': MetaInfo(
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            generic_field=gf.GenericDateCreated
        ),
        'QuickTime:TrackModifyDate': MetaInfo(
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=0.5),
                WeightedMapping(fields.Date, probability=0.5)
            ],
            generic_field=gf.GenericDateModified
        ),
        'QuickTime:MediaCreateDate': MetaInfo(
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            generic_field=gf.GenericDateCreated
        ),
        'QuickTime:MediaModifyDate': MetaInfo(
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=0.5),
                WeightedMapping(fields.Date, probability=0.5)
            ],
            generic_field=gf.GenericDateModified
        ),
        'XMP:About': MetaInfo(types.AW_STRING),
        'XMP:CreateDate': MetaInfo(
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            generic_field=gf.GenericDateCreated
        ),
        'XMP:Creator': MetaInfo(
            mapped_fields=[
                WeightedMapping(fields.Author, probability=1),
                WeightedMapping(fields.Creator, probability=0.5),
                WeightedMapping(fields.Publisher, probability=0.02),
                WeightedMapping(fields.Title, probability=0.01)
            ],
            generic_field=gf.GenericAuthor
        ),
        'XMP:CreatorTool': MetaInfo(
            mapped_fields=[
                WeightedMapping(fields.Creator, probability=1),
                WeightedMapping(fields.Author, probability=0.025),
                WeightedMapping(fields.Publisher, probability=0.02),
                WeightedMapping(fields.Title, probability=0.01)
            ],
            generic_field=gf.GenericCreator
        ),
        'XMP:DocumentID': MetaInfo(types.AW_STRING),
        'XMP:Format': MetaInfo(
            mapped_fields=[
                WeightedMapping(fields.Extension, probability=0.75)
            ],
            generic_field=gf.GenericMimeType
        ),
        'XMP:HistoryAction': MetaInfo(
            multivalued=True
        ),
        'XMP:HistoryChanged': MetaInfo(
            multivalued=True
        ),
        'XMP:HistoryInstanceID': MetaInfo(
            multivalued=True
        ),
        'XMP:HistoryParameters': MetaInfo(
            multivalued=True
        ),
        'XMP:HistorySoftwareAgent': MetaInfo(
            multivalued=True
        ),
        'XMP:HistoryWhen': MetaInfo(
            multivalued=True
        ),
        'XMP:Keywords': MetaInfo(
            mapped_fields=[
                WeightedMapping(fields.Tags, probability=1),
                WeightedMapping(fields.Title, probability=0.5),
                WeightedMapping(fields.Description, probability=0.8)
            ],
            generic_field=gf.GenericTags
        ),
        'XMP:ManifestLinkForm': MetaInfo(
            multivalued=True
        ),
        'XMP:ManifestReferenceInstanceID': MetaInfo(
            multivalued=True
        ),
        'XMP:ManifestReferenceDocumentID': MetaInfo(
            multivalued=True
        ),
        'XMP:MetadataDate': MetaInfo(
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=0.25),
                WeightedMapping(fields.Date, probability=0.25)
            ],
            generic_field=gf.GenericDateModified
        ),
        'XMP:ModifyDate': MetaInfo(
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=0.25),
                WeightedMapping(fields.Date, probability=0.25)
            ],
            generic_field=gf.GenericDateModified
        ),
        'XMP:Producer': MetaInfo(
            mapped_fields=[
                WeightedMapping(fields.Publisher, probability=0.25),
                WeightedMapping(fields.Author, probability=0.02),
                WeightedMapping(fields.Title, probability=0.01)
            ],
            generic_field=gf.GenericProducer
        ),
        'XMP:Subject': MetaInfo(
            mapped_fields=[
                WeightedMapping(fields.Description, probability=1),
                WeightedMapping(fields.Tags, probability=0.8),
                WeightedMapping(fields.Title, probability=0.5)
            ],
            generic_field=gf.GenericSubject,
            multivalued=True
        ),
        'XMP:TagsList': MetaInfo(
            mapped_fields=[
                WeightedMapping(fields.Tags, probability=1),
                WeightedMapping(fields.Title, probability=0.5),
                WeightedMapping(fields.Description, probability=0.8)
            ],
            generic_field=gf.GenericTags
        ),
        'XMP:Title': MetaInfo(
            mapped_fields=[
                WeightedMapping(fields.Title, probability=1)
            ],
            generic_field=gf.GenericTitle
        ),
        'XMP:XMPToolkit': MetaInfo(types.AW_STRING),
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
