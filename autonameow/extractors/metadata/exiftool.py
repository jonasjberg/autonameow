# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg
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
    'PDF:Author': {'Author', 'Unknown'},
    'PDF:Subject': {'Subject', 'Unknown'},
    'PDF:Title': {'Title', 'Unknown'},
    'XMP:Author': {'Author', 'Creator', 'Unknown'},
    'XMP:Creator': {'Author', 'Creator', 'Unknown'},
    'XMP:Description': {'Subject', 'Description', 'Unknown'},
    'XMP:Subject': {'Subject', 'Description', 'Unknown'},
    'XMP:Title': {'Title', 'Unknown'}
}


class ExiftoolMetadataExtractor(BaseExtractor):
    """
    Extracts various types of metadata using "exiftool".
    """
    HANDLES_MIME_TYPES = [
        'video/*', 'application/pdf', 'image/*', 'application/epub+zip',
        'text/*', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ]
    IS_SLOW = False

    # TODO: [TD0178] Store only strings in 'FIELD_LOOKUP'.
    FIELD_LOOKUP = {
        'ASF:CreationDate': {
            'coercer': 'aw_exiftooltimedate',
            'multivalued': 'false',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'DateTime', 'probability': 1}},
                {'WeightedMapping': {'field': 'Date', 'probability': 1}},
            ],
            'generic_field': 'date_created'
        },
        'ASF:ImageHeight': {
            'coercer': 'aw_integer',
            'multivalued': 'false'
        },
        'ASF:ImageWidth': {
            'coercer': 'aw_integer',
            'multivalued': 'false'
        },
        'ASF:VideoCodecName': {
            'coercer': 'aw_string',
            'multivalued': 'false'
        },
        'Composite:Aperture': {
            'coercer': 'aw_float',
            'multivalued': 'false'
        },
        'Composite:ImageSize': {
            'coercer': 'aw_string',
            'multivalued': 'false'
        },
        'Composite:Megapixels': {
            'coercer': 'aw_float',
            'multivalued': 'false'
        },
        'Composite:HyperfocalDistance': {
            'coercer': 'aw_float',
            'multivalued': 'false'
        },
        'EXIF:CreateDate': {
            'coercer': 'aw_exiftooltimedate',
            'multivalued': 'false',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'DateTime', 'probability': 1}},
                {'WeightedMapping': {'field': 'Date', 'probability': 1}},
            ],
            'generic_field': 'date_created'
        },
        'EXIF:DateTimeDigitized': {
            'coercer': 'aw_exiftooltimedate',
            'multivalued': 'false',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'DateTime', 'probability': 1}},
                {'WeightedMapping': {'field': 'Date', 'probability': 1}},
            ],
            'generic_field': 'date_created'
        },
        'EXIF:DateTimeOriginal': {
            'coercer': 'aw_exiftooltimedate',
            'multivalued': 'false',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'DateTime', 'probability': 1}},
                {'WeightedMapping': {'field': 'Date', 'probability': 1}},
            ],
            'generic_field': 'date_created'
        },
        'EXIF:ExifVersion': {
            'coercer': 'aw_integer',
            'multivalued': 'false'
        },
        'EXIF:GainControl': {
            'coercer': 'aw_integer',
            'multivalued': 'false'
        },
        # TODO: Handle GPS date/time-information.
        #       EXIF:GPSTimeStamp: '12:07:59'
        #       EXIF:GPSDateStamp: '2016:03:26'

        # 'EXIF:GPSTimeStamp': {
        #     'coercer': 'aw_exiftooltimedate',
        #     'mapped_fields': [
        #         {'WeightedMapping': {'field': 'Date', 'probability': 1}},
        #     ]
        # },
        'EXIF:GPSDateStamp': {
            'coercer': 'aw_exiftooltimedate',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Date', 'probability': 1}},
            ],
            'generic_field': 'date_created'
        },
        'EXIF:ImageDescription': {
            'coercer': 'aw_string',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Description', 'probability': 1}},
                {'WeightedMapping': {'field': 'Tags', 'probability': 0.5}},
                {'WeightedMapping': {'field': 'Title', 'probability': 0.25}},
            ],
            'generic_field': 'description'
        },
        'EXIF:ExifImageHeight': {
            'coercer': 'aw_integer',
            'multivalued': 'false'
        },
        'EXIF:ExifImageWidth': {
            'coercer': 'aw_integer',
            'multivalued': 'false'
        },
        'EXIF:Make': {
            'coercer': 'aw_string',
            'multivalued': 'false'
        },
        'EXIF:Model': {
            'coercer': 'aw_string',
            'multivalued': 'false'
        },
        'EXIF:ModifyDate': {
            'coercer': 'aw_exiftooltimedate',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'DateTime', 'probability': 0.25}},
                {'WeightedMapping': {'field': 'Date', 'probability': 0.25}},
            ],
            'generic_field': 'date_modified'
        },
        'EXIF:Software': {
            'coercer': 'aw_string',
            'multivalued': 'false'
        },
        'EXIF:UserComment': {
            'coercer': 'aw_string',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Description', 'probability': 0.5}},
                {'WeightedMapping': {'field': 'Tags', 'probability': 0.5}},
            ],
            'generic_field': 'description'
        },
        'File:Comment': {
            'coercer': 'aw_string',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Description', 'probability': 0.5}},
                {'WeightedMapping': {'field': 'Tags', 'probability': 0.5}},
            ],
            'generic_field': 'description'
        },
        'File:Directory': {'coercer': 'aw_path'},
        'File:FileAccessDate': {
            'coercer': 'aw_exiftooltimedate',
            'multivalued': 'false',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'DateTime', 'probability': 0.01}},
                {'WeightedMapping': {'field': 'Date', 'probability': 0.01}},
            ],
            'generic_field': 'date_modified'
        },
        'File:FileInodeChangeDate': {
            'coercer': 'aw_exiftooltimedate',
            'multivalued': 'false',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'DateTime', 'probability': 0.01}},
                {'WeightedMapping': {'field': 'Date', 'probability': 0.01}},
            ],
            'generic_field': 'date_modified'
        },
        'File:FileModifyDate': {
            'coercer': 'aw_exiftooltimedate',
            'multivalued': 'false',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'DateTime', 'probability': 0.25}},
                {'WeightedMapping': {'field': 'Date', 'probability': 0.25}},
            ],
            'generic_field': 'date_modified'
        },
        'File:FileName': {
            'coercer': 'aw_path',
            'multivalued': 'false'
        },
        'File:FilePermissions': {
            'coercer': 'aw_integer',
            'multivalued': 'false'
        },
        'File:FileSize': {
            'coercer': 'aw_integer',
            'multivalued': 'false'
        },
        'File:FileType': {
            'coercer': 'aw_string',
            'multivalued': 'false'
        },
        'File:FileTypeExtension': {
            'coercer': 'aw_pathcomponent',
            'multivalued': 'false'
        },
        'File:ImageHeight': {
            'coercer': 'aw_integer',
            'multivalued': 'false'
        },
        'File:ImageWidth': {
            'coercer': 'aw_integer',
            'multivalued': 'false'
        },
        'File:MIMEType': {
            'coercer': 'aw_mimetype',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Extension', 'probability': 1}},
            ],
            'generic_field': 'mime_type'
        },
        'PDF:Author': {
            'coercer': 'aw_string',
            'multivalued': 'true',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Author', 'probability': 1}},
            ],
            'generic_field': 'author'
        },
        'PDF:CreateDate': {
            'coercer': 'aw_exiftooltimedate',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'DateTime', 'probability': 1}},
                {'WeightedMapping': {'field': 'Date', 'probability': 1}},
            ],
            'generic_field': 'date_created'
        },
        'PDF:Creator': {
            'coercer': 'aw_string',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Creator', 'probability': 1}},
                {'WeightedMapping': {'field': 'Author', 'probability': 0.025}},
                {'WeightedMapping': {'field': 'Publisher', 'probability': 0.02}},
                {'WeightedMapping': {'field': 'Title', 'probability': 0.01}},
            ],
            'generic_field': 'creator'
        },
        'PDF:Keywords': {
            'coercer': 'aw_string',
            'multivalued': 'true',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Tags', 'probability': 1}},
            ],
            'generic_field': 'tags'
        },
        'PDF:Linearized': {
            'coercer': 'aw_boolean',
            'multivalued': 'false'
        },
        'PDF:ModifyDate': {
            'coercer': 'aw_exiftooltimedate',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'DateTime', 'probability': 0.25}},
                {'WeightedMapping': {'field': 'Date', 'probability': 0.25}},
            ],
            'generic_field': 'date_modified'
        },
        'PDF:PDFVersion': {
            'coercer': 'aw_float',
            'multivalued': 'false'
        },
        'PDF:PageCount': {
            'coercer': 'aw_integer',
            'multivalued': 'false'
        },
        'PDF:Producer': {
            'coercer': 'aw_string',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Publisher', 'probability': 0.25}},
                {'WeightedMapping': {'field': 'Author', 'probability': 0.02}},
                {'WeightedMapping': {'field': 'Title', 'probability': 0.01}},
            ],
            'generic_field': 'producer'
        },
        'PDF:Subject': {
            'coercer': 'aw_string',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Description', 'probability': 1}},
                {'WeightedMapping': {'field': 'Tags', 'probability': 0.8}},
                {'WeightedMapping': {'field': 'Title', 'probability': 0.5}},
            ],
            'generic_field': 'subject',
        },
        'PDF:Title': {
            'coercer': 'aw_string',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Title', 'probability': 1}}
            ],
            'generic_field': 'title'
        },
        'PDF:Trapped': {
            'coercer': 'aw_boolean',
            'multivalued': 'false'
        },
        'SourceFile': {
            'coercer': 'aw_path',
            'multivalued': 'false'
        },
        'QuickTime:CompatibleBrands': {
            'coercer': 'aw_string',
            'multivalued': 'true'
        },
        'QuickTime:CreateDate': {
            'coercer': 'aw_exiftooltimedate',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'DateTime', 'probability': 1}},
                {'WeightedMapping': {'field': 'Date', 'probability': 1}}
            ],
            'generic_field': 'date_created'
        },
        'QuickTime:CreationDate': {
            'coercer': 'aw_exiftooltimedate',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'DateTime', 'probability': 1}},
                {'WeightedMapping': {'field': 'Date', 'probability': 1}}
            ],
            'generic_field': 'date_created'
        },
        'QuickTime:ModifyDate': {
            'coercer': 'aw_exiftooltimedate',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'DateTime', 'probability': 0.5}},
                {'WeightedMapping': {'field': 'Date', 'probability': 0.5}},
            ],
            'generic_field': 'date_modified'
        },
        'QuickTime:CreationDate-und-SE': {
            'coercer': 'aw_exiftooltimedate',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'DateTime', 'probability': 1}},
                {'WeightedMapping': {'field': 'Date', 'probability': 1}}
            ],
            'generic_field': 'date_created'
        },
        'QuickTime:TrackCreateDate': {
            'coercer': 'aw_exiftooltimedate',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'DateTime', 'probability': 1}},
                {'WeightedMapping': {'field': 'Date', 'probability': 1}}
            ],
            'generic_field': 'date_created'
        },
        'QuickTime:TrackModifyDate': {
            'coercer': 'aw_exiftooltimedate',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'DateTime', 'probability': 0.5}},
                {'WeightedMapping': {'field': 'Date', 'probability': 0.5}},
            ],
            'generic_field': 'date_modified'
        },
        'QuickTime:MediaCreateDate': {
            'coercer': 'aw_exiftooltimedate',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'DateTime', 'probability': 1}},
                {'WeightedMapping': {'field': 'Date', 'probability': 1}}
            ],
            'generic_field': 'date_created'
        },
        'QuickTime:MediaModifyDate': {
            'coercer': 'aw_exiftooltimedate',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'DateTime', 'probability': 0.5}},
                {'WeightedMapping': {'field': 'Date', 'probability': 0.5}},
            ],
            'generic_field': 'date_modified'
        },
        'RTF:Author': {
            'coercer': 'aw_string',
            'multivalued': 'true',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Author', 'probability': 1.0}},
                {'WeightedMapping': {'field': 'Publisher', 'probability': 0.1}},
            ],
            'generic_field': 'author'
        },
        'RTF:Company': {
            'coercer': 'aw_string',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Author', 'probability': 0.6}},
                {'WeightedMapping': {'field': 'Publisher', 'probability': 0.5}},
                {'WeightedMapping': {'field': 'Creator', 'probability': 0.1}},
            ]
        },
        'RTF:CreateDate': {
            'coercer': 'aw_exiftooltimedate',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'DateTime', 'probability': 1.0}},
                {'WeightedMapping': {'field': 'Date', 'probability': 1.0}},
            ],
            'generic_field': 'date_created'
        },
        'RTF:LastModifiedBy': {
            'coercer': 'aw_string',
            'multivalued': 'true',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Author', 'probability': 0.8}},
                {'WeightedMapping': {'field': 'Publisher', 'probability': 0.1}},
            ],
            'generic_field': 'author'
        },
        'RTF:LastPrinted': {
            'coercer': 'aw_string',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'DateTime', 'probability': 0.01}},
                {'WeightedMapping': {'field': 'Date', 'probability': 0.01}},
            ]
        },
        'RTF:ModifyDate': {
            'coercer': 'aw_exiftooltimedate',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'DateTime', 'probability': 0.25}},
                {'WeightedMapping': {'field': 'Date', 'probability': 0.25}},
            ],
            'generic_field': 'date_modified'
        },
        'RTF:Title': {
            'coercer': 'aw_string',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Title', 'probability': 1}},
            ],
            'generic_field': 'title'
        },
        'XML:Application': {
            'coercer': 'aw_string',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Creator', 'probability': 1}},
                {'WeightedMapping': {'field': 'Author', 'probability': 0.025}},
                {'WeightedMapping': {'field': 'Publisher', 'probability': 0.02}},
                {'WeightedMapping': {'field': 'Title', 'probability': 0.01}},
            ],
            'generic_field': 'creator'
        },
        'XML:Company': {
            'coercer': 'aw_string',
            'multivalued': 'true',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Author', 'probability': 0.6}},
                {'WeightedMapping': {'field': 'Publisher', 'probability': 0.5}},
                {'WeightedMapping': {'field': 'Creator', 'probability': 0.1}},
            ],
            'generic_field': 'author'
        },
        'XML:CreateDate': {
            'coercer': 'aw_exiftooltimedate',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'DateTime', 'probability': 1}},
                {'WeightedMapping': {'field': 'Date', 'probability': 1}},
            ],
            'generic_field': 'date_created'
        },
        # Typically a username.
        'XML:LastModifiedBy': {
            'coercer': 'aw_string',
            'multivalued': 'true',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Author', 'probability': 0.9}},
                {'WeightedMapping': {'field': 'Publisher', 'probability': 0.5}},
                {'WeightedMapping': {'field': 'Creator', 'probability': 0.1}},
            ],
            'generic_field': 'author'
        },
        'XML:ModifyDate': {
            'coercer': 'aw_exiftooltimedate',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'DateTime', 'probability': 1}},
                {'WeightedMapping': {'field': 'Date', 'probability': 1}},
            ],
            'generic_field': 'date_modified'
        },
        'XML:TitlesOfParts': {
            'coercer': 'aw_string',
            'multivalued': 'true',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Title', 'probability': 0.7}},
            ]
        },
        'XMP:About': {'coercer': 'aw_string'},
        'XMP:Contributor': {
            'coercer': 'aw_string',
            'multivalued': 'true',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Author', 'probability': 0.5}},
                {'WeightedMapping': {'field': 'Creator', 'probability': 0.5}},
                {'WeightedMapping': {'field': 'Publisher', 'probability': 0.02}},
            ],
            'generic_field': 'author'
        },
        'XMP:CreateDate': {
            'coercer': 'aw_exiftooltimedate',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'DateTime', 'probability': 1}},
                {'WeightedMapping': {'field': 'Date', 'probability': 1}},
            ],
            'generic_field': 'date_created'
        },
        'XMP:Creator': {
            'coercer': 'aw_string',
            'multivalued': 'true',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Creator', 'probability': 1}},
                {'WeightedMapping': {'field': 'Author', 'probability': 0.75}},
                {'WeightedMapping': {'field': 'Publisher', 'probability': 0.02}},
                {'WeightedMapping': {'field': 'Title', 'probability': 0.01}},
            ],
            'generic_field': 'author'
        },
        'XMP:CreatorFile-as': {
            'coercer': 'aw_string',
            'multivalued': 'true',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Creator', 'probability': 1}},
                {'WeightedMapping': {'field': 'Author', 'probability': 0.75}},
                {'WeightedMapping': {'field': 'Publisher', 'probability': 0.03}},
                {'WeightedMapping': {'field': 'Title', 'probability': 0.02}},
            ],
            'generic_field': 'author'
        },
        'XMP:CreatorTool': {
            'coercer': 'aw_string',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Creator', 'probability': 1}},
                {'WeightedMapping': {'field': 'Author', 'probability': 0.025}},
                {'WeightedMapping': {'field': 'Publisher', 'probability': 0.02}},
                {'WeightedMapping': {'field': 'Title', 'probability': 0.01}},
            ],
            'generic_field': 'creator'
        },
        'XMP:Date': {
            'coercer': 'aw_exiftooltimedate',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'DateTime', 'probability': 1}},
                {'WeightedMapping': {'field': 'Date', 'probability': 1}},
            ],
            'generic_field': 'date_created'
        },
        'XMP:Description': {
            # TODO: Possibly HTML; <p>TEXT</p>, HTML-encoded characters, etc.
            'coercer': 'aw_string',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Description', 'probability': 1}},
                {'WeightedMapping': {'field': 'Tags', 'probability': 0.5}},
            ],
            'generic_field': 'description'
        },
        'XMP:DocumentID': {
            'coercer': 'aw_string',
            'multivalued': 'false'
        },
        'XMP:EntryAuthorName': {
            'coercer': 'aw_string',
            'multivalued': 'true',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Author', 'probability': 1}},
                {'WeightedMapping': {'field': 'Creator', 'probability': 0.5}},
                {'WeightedMapping': {'field': 'Publisher', 'probability': 0.02}},
                {'WeightedMapping': {'field': 'Title', 'probability': 0.01}},
            ],
            'generic_field': 'author'
        },
        'XMP:EntryIssued': {
            'coercer': 'aw_exiftooltimedate',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'DateTime', 'probability': 1}},
                {'WeightedMapping': {'field': 'Date', 'probability': 1}},
            ],
            'generic_field': 'date_created'
        },
        'XMP:EntryTitle': {
            'coercer': 'aw_string',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Title', 'probability': 1}},
            ],
            'generic_field': 'title'
        },
        'XMP:EntrySummary': {
            'coercer': 'aw_string',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Description', 'probability': 0.5}},
                {'WeightedMapping': {'field': 'Tags', 'probability': 0.5}},
            ],
            'generic_field': 'description'
        },
        'XMP:Format': {
            'coercer': 'aw_mimetype',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Extension', 'probability': 0.75}},
            ],
            'generic_field': 'mime_type'
        },
        'XMP:HistoryAction': {
            'coercer': 'aw_string',
            'multivalued': 'true'
        },
        'XMP:HistoryChanged': {
            'coercer': 'aw_string',
            'multivalued': 'true'
        },
        'XMP:HistoryInstanceID': {
            'coercer': 'aw_string',
            'multivalued': 'true'
        },
        'XMP:HistoryParameters': {
            'coercer': 'aw_string',
            'multivalued': 'true'
        },
        'XMP:HistorySoftwareAgent': {
            'coercer': 'aw_string',
            'multivalued': 'true'
        },
        'XMP:HistoryWhen': {
            'coercer': 'aw_timedate',
            'multivalued': 'true'
        },
        'XMP:Identifier': {
            'coercer': 'aw_string',
        },
        'XMP:Keywords': {
            'coercer': 'aw_string',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Tags', 'probability': 1}},
                {'WeightedMapping': {'field': 'Title', 'probability': 0.5}},
                {'WeightedMapping': {'field': 'Description', 'probability': 0.8}},
            ],
            'generic_field': 'tags'
        },
        'XMP:ManifestLinkForm': {
            'coercer': 'aw_string',
            'multivalued': 'true'
        },
        'XMP:ManifestReferenceInstanceID': {
            'coercer': 'aw_string',
            'multivalued': 'true'
        },
        'XMP:ManifestReferenceDocumentID': {
            'coercer': 'aw_string',
            'multivalued': 'true'
        },
        'XMP:MetadataDate': {
            'coercer': 'aw_exiftooltimedate',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'DateTime', 'probability': 0.25}},
                {'WeightedMapping': {'field': 'Date', 'probability': 0.25}},
            ],
            'generic_field': 'date_modified'
        },
        'XMP:ModifyDate': {
            'coercer': 'aw_exiftooltimedate',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'DateTime', 'probability': 0.25}},
                {'WeightedMapping': {'field': 'Date', 'probability': 0.25}},
            ],
            'generic_field': 'date_modified'
        },
        'XMP:Producer': {
            'coercer': 'aw_string',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Publisher', 'probability': 0.25}},
                {'WeightedMapping': {'field': 'Author', 'probability': 0.02}},
                {'WeightedMapping': {'field': 'Title', 'probability': 0.01}},
            ],
            'generic_field': 'producer'
        },
        'XMP:Publisher': {
            'coercer': 'aw_string',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Publisher', 'probability': 1}},
                {'WeightedMapping': {'field': 'Author', 'probability': 0.5}},
                {'WeightedMapping': {'field': 'Creator', 'probability': 0.2}},
                {'WeightedMapping': {'field': 'Title', 'probability': 0.01}},
            ],
            'generic_field': 'publisher'
        },
        'XMP:Rights': {
            'coercer': 'aw_string',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Publisher', 'probability': 0.5}},
                {'WeightedMapping': {'field': 'Author', 'probability': 0.5}},
            ],
        },
        'XMP:Subject': {
            #
            # TODO: Handle unexpected list with ISBN. Example;
            #
            # Tag: "XMP:Subject" Value: "['ISBN-13:', 9781847197283]"
            #
            'coercer': 'aw_string',
            'multivalued': 'true',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Description', 'probability': 1}},
                {'WeightedMapping': {'field': 'Tags', 'probability': 0.8}},
                {'WeightedMapping': {'field': 'Title', 'probability': 0.5}},
            ],
            'generic_field': 'subject',
        },
        'XMP:TagsList': {
            'coercer': 'aw_string',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Tags', 'probability': 1}},
                {'WeightedMapping': {'field': 'Title', 'probability': 0.5}},
                {'WeightedMapping': {'field': 'Description', 'probability': 0.8}},
            ],
            'generic_field': 'tags'
        },
        'XMP:Title': {
            'coercer': 'aw_string',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Title', 'probability': 1}},
            ],
            'generic_field': 'title'
        },
        'XMP:XMPToolkit': {
            'coercer': 'aw_string',
            'multivalued': 'false'
        }
    }

    def extract(self, fileobject, **kwargs):
        self.log.debug('{!s}: Starting extraction'.format(self))
        source = fileobject.abspath

        try:
            _metadata = self._get_metadata(source)
        except ValueError as e:
            raise ExtractorError('Possible bug in "pyexiftool": {!s}'.format(e))

        self.log.debug('{!s}: Completed extraction'.format(self))
        return _metadata

    def _get_metadata(self, source):
        _raw_metadata = _get_exiftool_data(source)
        if _raw_metadata:
            _filtered_metadata = self._filter_raw_data(_raw_metadata)

            # Internal data format boundary.  Wrap "raw" data with type classes.
            metadata = self._to_internal_format(_filtered_metadata)
            return metadata

        return dict()

    def _filter_raw_data(self, raw_metadata):
        # TODO: [TD0034] Filter out known bad data.
        # TODO: [TD0035] Use per-extractor, per-field, etc., blacklists?
        return {tag: value for tag, value in raw_metadata.items()
                if value is not None
                and not is_ignored_tagname(tag)
                and not is_binary_blob(value)
                and not is_bad_metadata(tag, value)}

    def _to_internal_format(self, raw_metadata):
        coerced_metadata = dict()

        for field, value in raw_metadata.items():
            coerced = self.coerce_field_value(field, value)
            # TODO: [TD0034] Filter out known bad data.
            # TODO: [TD0035] Use per-extractor, per-field, etc., blacklists?
            # Empty strings are being passed through. But if we test with
            # 'if coerced', any False booleans, 0, etc. would be discarded.
            # Filtering must be field-specific.
            if coerced is not None:
                filtered = _filter_coerced_value(coerced)
                if filtered is not None:
                    coerced_metadata[field] = filtered

        return coerced_metadata

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
    try:
        with pyexiftool.ExifTool() as et:
            try:
                return et.get_metadata(source)
            except (AttributeError, ValueError, TypeError) as e:
                # Raises ValueError if an ExifTool instance isn't running.
                raise ExtractorError(e)
    except (OSError, ValueError) as e:
        # 'OSError: [Errno 12] Cannot allocate memory'
        # This apparently happens, not sure if it is a bug in 'pyexiftool' or
        # if the repository or something else grows way too large when running
        # with a lot of files ..
        # TODO: [TD0131] Limit repository size!
        #
        # ValueError can be raised by 'pyexiftool' when aborting with CTRL-C.
        #
        #     self._process.stdin.write(b"-stay_open\nFalse\n")
        #     ValueError: write to closed file
        #
        raise ExtractorError(e)


def _filter_coerced_value(value):
    # TODO: [TD0034] Remove duplicated functionality (coercers normalize?)
    def __filter_value(_value):
        if isinstance(_value, str):
            return _value if _value.strip() else None
        else:
            return _value

    if not isinstance(value, list):
        return __filter_value(value)
    else:
        assert isinstance(value, list)
        list_of_non_empty_values = [v for v in value if __filter_value(v)]
        if list_of_non_empty_values:
            return list_of_non_empty_values
    return None
