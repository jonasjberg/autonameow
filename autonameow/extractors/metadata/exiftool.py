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

from core import types
from core.model import WeightedMapping
from core.model import genericfields as gf
from core.namebuilder import fields
from extractors import (
    BaseExtractor,
    ExtractorError
)
from thirdparty import pyexiftool
import util


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

    FIELD_LOOKUP = {
        'ASF:CreationDate': {
            'coercer': types.AW_EXIFTOOLTIMEDATE,
            'multivalued': False,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            'generic_field': gf.GenericDateCreated
        },
        'ASF:ImageHeight': {'coercer': types.AW_INTEGER},
        'ASF:ImageWidth': {'coercer': types.AW_INTEGER},
        'ASF:VideoCodecName': {'coercer': types.AW_STRING},
        'Composite:Aperture': {'coercer': types.AW_FLOAT},
        'Composite:ImageSize': {'coercer': types.AW_STRING},
        'Composite:Megapixels': {'coercer': types.AW_FLOAT},
        'Composite:HyperfocalDistance': {'coercer': types.AW_FLOAT},
        'EXIF:CreateDate': {
            'coercer': types.AW_EXIFTOOLTIMEDATE,
            'multivalued': False,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            'generic_field': gf.GenericDateCreated
        },
        'EXIF:DateTimeDigitized': {
            'coercer': types.AW_EXIFTOOLTIMEDATE,
            'multivalued': False,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            'generic_field': gf.GenericDateCreated
        },
        'EXIF:DateTimeOriginal': {
            'coercer': types.AW_EXIFTOOLTIMEDATE,
            'multivalued': False,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            'generic_field': gf.GenericDateCreated
        },
        'EXIF:ExifVersion': {'coercer': types.AW_INTEGER},
        'EXIF:GainControl': {'coercer': types.AW_INTEGER},
        # TODO: Handle GPS date/time-information.
        #       EXIF:GPSTimeStamp: '12:07:59'
        #       EXIF:GPSDateStamp: '2016:03:26'

        # 'EXIF:GPSTimeStamp': {
        #     'coercer': types.AW_EXIFTOOLTIMEDATE,
        #     'mapped_fields': [
        #         fields.WeightedMapping(fields.Time, probability=1),
        #     ]
        # },
        'EXIF:GPSDateStamp': {
            'coercer': types.AW_EXIFTOOLTIMEDATE,
            'mapped_fields': [
                WeightedMapping(fields.Date, probability=1),
            ],
            'generic_field': gf.GenericDateCreated
        },
        'EXIF:ImageDescription': {
            'coercer': types.AW_STRING,
            'mapped_fields': [
                WeightedMapping(fields.Description, probability=1),
                WeightedMapping(fields.Tags, probability=0.5),
                WeightedMapping(fields.Title, probability=0.25)
            ],
            'generic_field': gf.GenericDescription
        },
        'EXIF:ExifImageHeight': {'coercer': types.AW_INTEGER},
        'EXIF:ExifImageWidth': {'coercer': types.AW_INTEGER},
        'EXIF:Make': {'coercer': types.AW_STRING},
        'EXIF:Model': {'coercer': types.AW_STRING},
        'EXIF:ModifyDate': {
            'coercer': types.AW_EXIFTOOLTIMEDATE,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=0.25),
                WeightedMapping(fields.Date, probability=0.25)
            ],
            'generic_field': gf.GenericDateModified
        },
        'EXIF:Software': {'coercer': types.AW_STRING},
        'EXIF:UserComment': {
            'coercer': types.AW_STRING,
            'mapped_fields': [
                WeightedMapping(fields.Description, probability=0.5),
                WeightedMapping(fields.Tags, probability=0.5)
            ],
            'generic_field': gf.GenericDescription
        },
        'File:Comment': {
            'coercer': types.AW_STRING,
            'mapped_fields': [
                WeightedMapping(fields.Description, probability=0.5),
                WeightedMapping(fields.Tags, probability=0.5)
            ],
            'generic_field': gf.GenericDescription
        },
        'File:Directory': {'coercer': types.AW_PATH},
        'File:FileAccessDate': {
            'coercer': types.AW_EXIFTOOLTIMEDATE,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=0.01),
                WeightedMapping(fields.Date, probability=0.01)
            ],
            'generic_field': gf.GenericDateModified
        },
        'File:FileInodeChangeDate': {
            'coercer': types.AW_EXIFTOOLTIMEDATE,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=0.01),
                WeightedMapping(fields.Date, probability=0.01)
            ],
            'generic_field': gf.GenericDateModified
        },
        'File:FileModifyDate': {
            'coercer': types.AW_EXIFTOOLTIMEDATE,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=0.25),
                WeightedMapping(fields.Date, probability=0.25)
            ],
            'generic_field': gf.GenericDateModified
        },
        'File:FileName': {'coercer': types.AW_PATH},
        'File:FilePermissions': {'coercer': types.AW_INTEGER},
        'File:FileSize': {'coercer': types.AW_INTEGER},
        'File:FileType': {'coercer': types.AW_STRING},
        'File:FileTypeExtension': {'coercer': types.AW_PATHCOMPONENT},
        'File:ImageHeight': {'coercer': types.AW_INTEGER},
        'File:ImageWidth': {'coercer': types.AW_INTEGER},
        'File:MIMEType': {
            'coercer': types.AW_MIMETYPE,
            'mapped_fields': [
                WeightedMapping(fields.Extension, probability=1)
            ],
            'generic_field': gf.GenericMimeType
        },
        'PDF:Author': {
            'coercer': types.AW_STRING,
            'mapped_fields': [
                WeightedMapping(fields.Author, probability=1),
            ],
            'generic_field': gf.GenericAuthor
        },
        'PDF:CreateDate': {
            'coercer': types.AW_EXIFTOOLTIMEDATE,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            'generic_field': gf.GenericDateCreated
        },
        'PDF:Creator': {
            'coercer': types.AW_STRING,
            'mapped_fields': [
                WeightedMapping(fields.Creator, probability=1),
                WeightedMapping(fields.Author, probability=0.025),
                WeightedMapping(fields.Publisher, probability=0.02),
                WeightedMapping(fields.Title, probability=0.01)
            ],
            'generic_field': gf.GenericCreator
        },
        'PDF:Keywords': {
            'coercer': types.AW_STRING,
            'multivalued': True,
            'mapped_fields': [
                WeightedMapping(fields.Tags, probability=1),
            ],
            'generic_field': gf.GenericTags
        },
        'PDF:Linearized': {'coercer': types.AW_BOOLEAN},
        'PDF:ModifyDate': {
            'coercer': types.AW_EXIFTOOLTIMEDATE,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=0.25),
                WeightedMapping(fields.Date, probability=0.25)
            ],
            'generic_field': gf.GenericDateModified
        },
        'PDF:PDFVersion': {'coercer': types.AW_FLOAT},
        'PDF:PageCount': {'coercer': types.AW_INTEGER},
        'PDF:Producer': {
            'coercer': types.AW_STRING,
            'mapped_fields': [
                WeightedMapping(fields.Publisher, probability=0.25),
                WeightedMapping(fields.Author, probability=0.02),
                WeightedMapping(fields.Title, probability=0.01)
            ],
            'generic_field': gf.GenericProducer
        },
        'PDF:Subject': {
            'coercer': types.AW_STRING,
            'multivalued': True,
            'mapped_fields': [
                WeightedMapping(fields.Description, probability=1),
                WeightedMapping(fields.Tags, probability=0.8),
                WeightedMapping(fields.Title, probability=0.5)
            ],
            'generic_field': gf.GenericSubject,
        },
        'PDF:Title': {
            'coercer': types.AW_STRING,
            'mapped_fields': [
                WeightedMapping(fields.Title, probability=1)
            ],
            'generic_field': gf.GenericTitle
        },
        'PDF:Trapped': {'coercer': types.AW_BOOLEAN},
        'SourceFile': {'coercer': types.AW_PATH},
        'QuickTime:CompatibleBrands': {
            'coercer': types.AW_STRING,
            'multivalued': True
        },
        'QuickTime:CreateDate': {
            'coercer': types.AW_EXIFTOOLTIMEDATE,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            'generic_field': gf.GenericDateCreated
        },
        'QuickTime:CreationDate': {
            'coercer': types.AW_EXIFTOOLTIMEDATE,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            'generic_field': gf.GenericDateCreated
        },
        'QuickTime:ModifyDate': {
            'coercer': types.AW_EXIFTOOLTIMEDATE,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=0.5),
                WeightedMapping(fields.Date, probability=0.5)
            ],
            'generic_field': gf.GenericDateModified
        },
        'QuickTime:CreationDate-und-SE': {
            'coercer': types.AW_EXIFTOOLTIMEDATE,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            'generic_field': gf.GenericDateCreated
        },
        'QuickTime:TrackCreateDate': {
            'coercer': types.AW_EXIFTOOLTIMEDATE,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            'generic_field': gf.GenericDateCreated
        },
        'QuickTime:TrackModifyDate': {
            'coercer': types.AW_EXIFTOOLTIMEDATE,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=0.5),
                WeightedMapping(fields.Date, probability=0.5)
            ],
            'generic_field': gf.GenericDateModified
        },
        'QuickTime:MediaCreateDate': {
            'coercer': types.AW_EXIFTOOLTIMEDATE,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            'generic_field': gf.GenericDateCreated
        },
        'QuickTime:MediaModifyDate': {
            'coercer': types.AW_EXIFTOOLTIMEDATE,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=0.5),
                WeightedMapping(fields.Date, probability=0.5)
            ],
            'generic_field': gf.GenericDateModified
        },
        'XMP:About': {'coercer': types.AW_STRING},
        'XMP:CreateDate': {
            'coercer': types.AW_EXIFTOOLTIMEDATE,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            'generic_field': gf.GenericDateCreated
        },
        'XMP:Creator': {
            'coercer': types.AW_STRING,
            'mapped_fields': [
                WeightedMapping(fields.Author, probability=1),
                WeightedMapping(fields.Creator, probability=0.5),
                WeightedMapping(fields.Publisher, probability=0.02),
                WeightedMapping(fields.Title, probability=0.01)
            ],
            'generic_field': gf.GenericAuthor
        },
        'XMP:CreatorTool': {
            'coercer': types.AW_STRING,
            'mapped_fields': [
                WeightedMapping(fields.Creator, probability=1),
                WeightedMapping(fields.Author, probability=0.025),
                WeightedMapping(fields.Publisher, probability=0.02),
                WeightedMapping(fields.Title, probability=0.01)
            ],
            'generic_field': gf.GenericCreator
        },
        'XMP:DocumentID': {'coercer': types.AW_STRING},
        'XMP:Format': {
            'coercer': types.AW_MIMETYPE,
            'mapped_fields': [
                WeightedMapping(fields.Extension, probability=0.75)
            ],
            'generic_field': gf.GenericMimeType
        },
        'XMP:HistoryAction': {
            'coercer': types.AW_STRING,
            'multivalued': True
        },
        'XMP:HistoryChanged': {
            'coercer': types.AW_STRING,
            'multivalued': True
        },
        'XMP:HistoryInstanceID': {
            'coercer': types.AW_STRING,
            'multivalued': True
        },
        'XMP:HistoryParameters': {
            'coercer': types.AW_STRING,
            'multivalued': True
        },
        'XMP:HistorySoftwareAgent': {
            'coercer': types.AW_STRING,
            'multivalued': True
        },
        'XMP:HistoryWhen': {
            'coercer': types.AW_TIMEDATE,
            'multivalued': True
        },
        'XMP:Keywords': {
            'coercer': types.AW_STRING,
            'mapped_fields': [
                WeightedMapping(fields.Tags, probability=1),
                WeightedMapping(fields.Title, probability=0.5),
                WeightedMapping(fields.Description, probability=0.8)
            ],
            'generic_field': gf.GenericTags
        },
        'XMP:ManifestLinkForm': {
            'coercer': types.AW_STRING,
            'multivalued': True
        },
        'XMP:ManifestReferenceInstanceID': {
            'coercer': types.AW_STRING,
            'multivalued': True
        },
        'XMP:ManifestReferenceDocumentID': {
            'coercer': types.AW_STRING,
            'multivalued': True
        },
        'XMP:MetadataDate': {
            'coercer': types.AW_EXIFTOOLTIMEDATE,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=0.25),
                WeightedMapping(fields.Date, probability=0.25)
            ],
            'generic_field': gf.GenericDateModified
        },
        'XMP:ModifyDate': {
            'coercer': types.AW_EXIFTOOLTIMEDATE,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=0.25),
                WeightedMapping(fields.Date, probability=0.25)
            ],
            'generic_field': gf.GenericDateModified
        },
        'XMP:Producer': {
            'coercer': types.AW_STRING,
            'mapped_fields': [
                WeightedMapping(fields.Publisher, probability=0.25),
                WeightedMapping(fields.Author, probability=0.02),
                WeightedMapping(fields.Title, probability=0.01)
            ],
            'generic_field': gf.GenericProducer
        },
        'XMP:Subject': {
            'coercer': types.AW_STRING,
            'multivalued': True,
            'mapped_fields': [
                WeightedMapping(fields.Description, probability=1),
                WeightedMapping(fields.Tags, probability=0.8),
                WeightedMapping(fields.Title, probability=0.5)
            ],
            'generic_field': gf.GenericSubject,
        },
        'XMP:TagsList': {
            'coercer': types.AW_STRING,
            'mapped_fields': [
                WeightedMapping(fields.Tags, probability=1),
                WeightedMapping(fields.Title, probability=0.5),
                WeightedMapping(fields.Description, probability=0.8)
            ],
            'generic_field': gf.GenericTags
        },
        'XMP:Title': {
            'coercer': types.AW_STRING,
            'mapped_fields': [
                WeightedMapping(fields.Title, probability=1)
            ],
            'generic_field': gf.GenericTitle
        },
        'XMP:XMPToolkit': {'coercer': types.AW_STRING}
    }

    def __init__(self):
        super(ExiftoolMetadataExtractor, self).__init__()

    def extract(self, fileobject, **kwargs):
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
            _filtered_metadata = self._filter_raw_data(_raw_metadata)

            # Internal data format boundary.  Wrap "raw" data with type classes.
            metadata = self._to_internal_format(_filtered_metadata)
            return metadata

    def _filter_raw_data(self, raw_metadata):
        return {tag: value for tag, value in raw_metadata.items()
                if value is not None
                and not is_ignored_tagname(tag)
                and not is_binary_blob(value)
                and not is_bad_metadata(tag, value)}

    def _to_internal_format(self, raw_metadata):
        out = {}

        for tag_name, value in raw_metadata.items():
            coerced = self.coerce_field_value(tag_name, value)
            if coerced is not None:
                out[tag_name] = coerced

        return out

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
