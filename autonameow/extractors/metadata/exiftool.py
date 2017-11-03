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
from core.model import WeightedMapping
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

    FIELD_LOOKUP = {
        'ASF:CreationDate': {
            'typewrap': types.AW_EXIFTOOLTIMEDATE,
            'multiple': False,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            'generic_field': gf.GenericDateCreated
        },
        'ASF:ImageHeight': {'typewrap': types.AW_INTEGER},
        'ASF:ImageWidth': {'typewrap': types.AW_INTEGER},
        'ASF:VideoCodecName': {'typewrap': types.AW_STRING},
        'Composite:Aperture': {'typewrap': types.AW_FLOAT},
        'Composite:ImageSize': {'typewrap': types.AW_STRING},
        'Composite:Megapixels': {'typewrap': types.AW_FLOAT},
        'Composite:HyperfocalDistance': {'typewrap': types.AW_FLOAT},
        'EXIF:CreateDate': {
            'typewrap': types.AW_EXIFTOOLTIMEDATE,
            'multiple': False,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            'generic_field': gf.GenericDateCreated
        },
        'EXIF:DateTimeDigitized': {
            'typewrap': types.AW_EXIFTOOLTIMEDATE,
            'multiple': False,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            'generic_field': gf.GenericDateCreated
        },
        'EXIF:DateTimeOriginal': {
            'typewrap': types.AW_EXIFTOOLTIMEDATE,
            'multiple': False,
            'mapped_fields': [
               WeightedMapping(fields.DateTime, probability=1),
               WeightedMapping(fields.Date, probability=1)
            ],
            'generic_field': gf.GenericDateCreated
        },
        'EXIF:ExifVersion': {'typewrap': types.AW_INTEGER},
        'EXIF:GainControl': {'typewrap': types.AW_INTEGER},
        # TODO: Handle GPS date/time-information.
        #       EXIF:GPSTimeStamp: '12:07:59'
        #       EXIF:GPSDateStamp: '2016:03:26'

        # 'EXIF:GPSTimeStamp': {
        #     'typewrap': types.AW_EXIFTOOLTIMEDATE,
        #     'mapped_fields': [
        #         fields.WeightedMapping(fields.Time, probability=1),
        #     ]
        # },
        'EXIF:GPSDateStamp': {
            'typewrap': types.AW_EXIFTOOLTIMEDATE,
            'mapped_fields': [
                WeightedMapping(fields.Date, probability=1),
            ],
            'generic_field': gf.GenericDateCreated
        },
        'EXIF:ImageDescription': {
            'typewrap': types.AW_STRING,
            'mapped_fields': [
                WeightedMapping(fields.Description, probability=1),
                WeightedMapping(fields.Tags, probability=0.5),
                WeightedMapping(fields.Title, probability=0.25)
            ],
            'generic_field': gf.GenericDescription
        },
        'EXIF:ExifImageHeight': {'typewrap': types.AW_INTEGER},
        'EXIF:ExifImageWidth': {'typewrap': types.AW_INTEGER},
        'EXIF:Make': {'typewrap': types.AW_STRING},
        'EXIF:Model': {'typewrap': types.AW_STRING},
        'EXIF:ModifyDate': {
            'typewrap': types.AW_EXIFTOOLTIMEDATE,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=0.25),
                WeightedMapping(fields.Date, probability=0.25)
            ],
            'generic_field': gf.GenericDateModified
        },
        'EXIF:Software': {'typewrap': types.AW_STRING},
        'EXIF:UserComment': {
            'typewrap': types.AW_STRING,
            'mapped_fields': [
                WeightedMapping(fields.Description, probability=0.5),
                WeightedMapping(fields.Tags, probability=0.5)
            ],
            'generic_field': gf.GenericDescription
        },
        'File:Comment': {
            'typewrap': types.AW_STRING,
            'mapped_fields': [
                WeightedMapping(fields.Description, probability=0.5),
                WeightedMapping(fields.Tags, probability=0.5)
            ],
            'generic_field': gf.GenericDescription
        },
        'File:Directory': {'typewrap': types.AW_PATH},
        'File:FileAccessDate': {
            'typewrap': types.AW_EXIFTOOLTIMEDATE,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=0.01),
                WeightedMapping(fields.Date, probability=0.01)
            ],
            'generic_field': gf.GenericDateModified
        },
        'File:FileInodeChangeDate': {
            'typewrap': types.AW_EXIFTOOLTIMEDATE,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=0.01),
                WeightedMapping(fields.Date, probability=0.01)
            ],
            'generic_field': gf.GenericDateModified
        },
        'File:FileModifyDate': {
            'typewrap': types.AW_EXIFTOOLTIMEDATE,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=0.25),
                WeightedMapping(fields.Date, probability=0.25)
            ],
            'generic_field': gf.GenericDateModified
        },
        'File:FileName': {'typewrap': types.AW_PATH},
        'File:FilePermissions': {'typewrap': types.AW_INTEGER},
        'File:FileSize': {'typewrap': types.AW_INTEGER},
        'File:FileType': {'typewrap': types.AW_STRING},
        'File:FileTypeExtension': {'typewrap': types.AW_PATHCOMPONENT},
        'File:ImageHeight': {'typewrap': types.AW_INTEGER},
        'File:ImageWidth': {'typewrap': types.AW_INTEGER},
        'File:MIMEType': {
            'typewrap': types.AW_MIMETYPE,
            'mapped_fields': [
                WeightedMapping(fields.Extension, probability=1)
            ],
            'generic_field': gf.GenericMimeType
        },
        'PDF:Author': {
            'typewrap': types.AW_STRING,
            'mapped_fields': [
                WeightedMapping(fields.Author, probability=1),
            ],
            'generic_field': gf.GenericAuthor
        },
        'PDF:CreateDate': {
            'typewrap': types.AW_EXIFTOOLTIMEDATE,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            'generic_field': gf.GenericDateCreated
        },
        'PDF:Creator': {
            'typewrap': types.AW_STRING,
            'mapped_fields': [
                WeightedMapping(fields.Creator, probability=1),
                WeightedMapping(fields.Author, probability=0.025),
                WeightedMapping(fields.Publisher, probability=0.02),
                WeightedMapping(fields.Title, probability=0.01)
            ],
            'generic_field': gf.GenericCreator
        },
        'PDF:Keywords': {
            'typewrap': types.AW_STRING,
            'multiple': True,
            'mapped_fields': [
                WeightedMapping(fields.Tags, probability=1),
            ],
            'generic_field': gf.GenericTags
        },
        'PDF:Linearized': {'typewrap': types.AW_BOOLEAN},
        'PDF:ModifyDate': {
            'typewrap': types.AW_EXIFTOOLTIMEDATE,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=0.25),
                WeightedMapping(fields.Date, probability=0.25)
            ],
            'generic_field': gf.GenericDateModified
        },
        'PDF:PDFVersion': {'typewrap': types.AW_FLOAT},
        'PDF:PageCount': {'typewrap': types.AW_INTEGER},
        'PDF:Producer': {
            'typewrap': types.AW_STRING,
            'mapped_fields': [
                WeightedMapping(fields.Publisher, probability=0.25),
                WeightedMapping(fields.Author, probability=0.02),
                WeightedMapping(fields.Title, probability=0.01)
            ],
            'generic_field': gf.GenericProducer
        },
        'PDF:Subject': {
            'typewrap': types.AW_STRING,
            'multiple': True,
            'mapped_fields': [
                WeightedMapping(fields.Description, probability=1),
                WeightedMapping(fields.Tags, probability=0.8),
                WeightedMapping(fields.Title, probability=0.5)
            ],
            'generic_field': gf.GenericSubject,
        },
        'PDF:Title': {
            'typewrap': types.AW_STRING,
            'mapped_fields': [
                WeightedMapping(fields.Title, probability=1)
            ],
            'generic_field': gf.GenericTitle
        },
        'PDF:Trapped': {'typewrap': types.AW_BOOLEAN},
        'SourceFile': {'typewrap': types.AW_PATH},
        'QuickTime:CompatibleBrands': {
            'typewrap': types.AW_STRING,
            'multiple': True
        },
        'QuickTime:CreateDate': {
            'typewrap': types.AW_EXIFTOOLTIMEDATE,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            'generic_field': gf.GenericDateCreated
        },
        'QuickTime:CreationDate': {
            'typewrap': types.AW_EXIFTOOLTIMEDATE,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            'generic_field': gf.GenericDateCreated
        },
        'QuickTime:ModifyDate': {
            'typewrap': types.AW_EXIFTOOLTIMEDATE,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=0.5),
                WeightedMapping(fields.Date, probability=0.5)
            ],
            'generic_field': gf.GenericDateModified
        },
        'QuickTime:CreationDate-und-SE': {
            'typewrap': types.AW_EXIFTOOLTIMEDATE,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            'generic_field': gf.GenericDateCreated
        },
        'QuickTime:TrackCreateDate': {
            'typewrap': types.AW_EXIFTOOLTIMEDATE,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            'generic_field': gf.GenericDateCreated
        },
        'QuickTime:TrackModifyDate': {
            'typewrap': types.AW_EXIFTOOLTIMEDATE,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=0.5),
                WeightedMapping(fields.Date, probability=0.5)
            ],
            'generic_field': gf.GenericDateModified
        },
        'QuickTime:MediaCreateDate': {
            'typewrap': types.AW_EXIFTOOLTIMEDATE,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            'generic_field': gf.GenericDateCreated
        },
        'QuickTime:MediaModifyDate': {
            'typewrap': types.AW_EXIFTOOLTIMEDATE,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=0.5),
                WeightedMapping(fields.Date, probability=0.5)
            ],
            'generic_field': gf.GenericDateModified
        },
        'XMP:About': {'typewrap': types.AW_STRING},
        'XMP:CreateDate': {
            'typewrap': types.AW_EXIFTOOLTIMEDATE,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=1),
                WeightedMapping(fields.Date, probability=1)
            ],
            'generic_field': gf.GenericDateCreated
        },
        'XMP:Creator': {
            'typewrap': types.AW_STRING,
            'mapped_fields': [
                WeightedMapping(fields.Author, probability=1),
                WeightedMapping(fields.Creator, probability=0.5),
                WeightedMapping(fields.Publisher, probability=0.02),
                WeightedMapping(fields.Title, probability=0.01)
            ],
            'generic_field': gf.GenericAuthor
        },
        'XMP:CreatorTool': {
            'typewrap': types.AW_STRING,
            'mapped_fields': [
                WeightedMapping(fields.Creator, probability=1),
                WeightedMapping(fields.Author, probability=0.025),
                WeightedMapping(fields.Publisher, probability=0.02),
                WeightedMapping(fields.Title, probability=0.01)
            ],
            'generic_field': gf.GenericCreator
        },
        'XMP:DocumentID': {'typewrap': types.AW_STRING},
        'XMP:Format': {
            'typewrap': types.AW_MIMETYPE,
            'mapped_fields': [
                WeightedMapping(fields.Extension, probability=0.75)
            ],
            'generic_field': gf.GenericMimeType
        },
        'XMP:HistoryAction': {
            'typewrap': types.AW_STRING,
            'multiple': True
        },
        'XMP:HistoryChanged': {
            'typewrap': types.AW_STRING,
            'multiple': True
        },
        'XMP:HistoryInstanceID': {
            'typewrap': types.AW_STRING,
            'multiple': True
        },
        'XMP:HistoryParameters': {
            'typewrap': types.AW_STRING,
            'multiple': True
        },
        'XMP:HistorySoftwareAgent': {
            'typewrap': types.AW_STRING,
            'multiple': True
        },
        'XMP:HistoryWhen': {
            'typewrap': types.AW_TIMEDATE,
            'multiple': True
        },
        'XMP:Keywords': {
            'typewrap': types.AW_STRING,
            'mapped_fields': [
                WeightedMapping(fields.Tags, probability=1),
                WeightedMapping(fields.Title, probability=0.5),
                WeightedMapping(fields.Description, probability=0.8)
            ],
            'generic_field': gf.GenericTags
        },
        'XMP:ManifestLinkForm': {
            'typewrap': types.AW_STRING,
            'multiple': True
        },
        'XMP:ManifestReferenceInstanceID': {
            'typewrap': types.AW_STRING,
            'multiple': True
        },
        'XMP:ManifestReferenceDocumentID': {
            'typewrap': types.AW_STRING,
            'multiple': True
        },
        'XMP:MetadataDate': {
            'typewrap': types.AW_EXIFTOOLTIMEDATE,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=0.25),
                WeightedMapping(fields.Date, probability=0.25)
            ],
            'generic_field': gf.GenericDateModified
        },
        'XMP:ModifyDate': {
            'typewrap': types.AW_EXIFTOOLTIMEDATE,
            'mapped_fields': [
                WeightedMapping(fields.DateTime, probability=0.25),
                WeightedMapping(fields.Date, probability=0.25)
            ],
            'generic_field': gf.GenericDateModified
        },
        'XMP:Producer': {
            'typewrap': types.AW_STRING,
            'mapped_fields': [
                WeightedMapping(fields.Publisher, probability=0.25),
                WeightedMapping(fields.Author, probability=0.02),
                WeightedMapping(fields.Title, probability=0.01)
            ],
            'generic_field': gf.GenericProducer
        },
        'XMP:Subject': {
            'typewrap': types.AW_STRING,
            'multiple': True,
            'mapped_fields': [
                WeightedMapping(fields.Description, probability=1),
                WeightedMapping(fields.Tags, probability=0.8),
                WeightedMapping(fields.Title, probability=0.5)
            ],
            'generic_field': gf.GenericSubject,
        },
        'XMP:TagsList': {
            'typewrap': types.AW_STRING,
            'mapped_fields': [
                WeightedMapping(fields.Tags, probability=1),
                WeightedMapping(fields.Title, probability=0.5),
                WeightedMapping(fields.Description, probability=0.8)
            ],
            'generic_field': gf.GenericTags
        },
        'XMP:Title': {
            'typewrap': types.AW_STRING,
            'mapped_fields': [
                WeightedMapping(fields.Title, probability=1)
            ],
            'generic_field': gf.GenericTitle
        },
        'XMP:XMPToolkit': {'typewrap': types.AW_STRING}
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
            _coerced = self.coerce_field_value(tag_name, value)
            if _coerced:
                out[tag_name] = _coerced

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
