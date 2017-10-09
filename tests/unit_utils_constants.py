#!/usr/bin/env python3
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

import os

from core import util

_THIS_DIR = os.path.abspath(os.path.dirname(__file__))
_PARENT_DIR = os.path.normpath(os.path.join(_THIS_DIR, os.pardir))
TEST_FILES_DIR = os.path.normpath(os.path.join(_PARENT_DIR, 'test_files'))
AUTONAMEOW_SRCROOT_DIR = os.path.normpath(
    os.path.join(_PARENT_DIR, util.syspath('autonameow'))
)


ASSUMED_NONEXISTENT_BASENAME = b'not_a_file_surely'


# Full MeowURIs to various data resources.
MEOWURI_FS_XPLAT_MIMETYPE = 'extractor.filesystem.xplat.contents.mime_type'
MEOWURI_FS_XPLAT_BASENAME_EXT = 'extractor.filesystem.xplat.basename.extension'
MEOWURI_FS_XPLAT_BASENAME_FULL = 'extractor.filesystem.xplat.basename.full'
MEOWURI_FS_XPLAT_BASENAME_PREFIX = 'extractor.filesystem.xplat.basename.prefix'
MEOWURI_FS_XPLAT_BASENAME_SUFFIX = 'extractor.filesystem.xplat.basename.suffix'
MEOWURI_FS_XPLAT_PATHNAME_FULL = 'extractor.filesystem.xplat.pathname.full'
MEOWURI_GEN_CONTENTS_MIMETYPE = 'generic.contents.mime_type'
MEOWURI_GEN_CONTENTS_TEXT = 'generic.contents.text'
MEOWURI_EXT_EXIFTOOL_EXIFCREATEDATE = 'extractor.metadata.exiftool.EXIF:CreateDate'
MEOWURI_EXT_EXIFTOOL_EXIFDATETIMEORIGINAL = 'extractor.metadata.exiftool.EXIF:DateTimeOriginal'


# Constants used to construct dummy/mock test fixtures.
DUMMY_RAW_RULE_CONDITIONS = [
    # Part of Rule 1
    (MEOWURI_GEN_CONTENTS_MIMETYPE, 'application/pdf'),
    (MEOWURI_FS_XPLAT_BASENAME_EXT, 'pdf'),
    (MEOWURI_FS_XPLAT_BASENAME_FULL, 'gmail.pdf'),

    # Part of Rule 2
    (MEOWURI_GEN_CONTENTS_MIMETYPE, 'image/jpeg'),
    (MEOWURI_FS_XPLAT_BASENAME_FULL, 'smulan.jpg'),

    # Part of Rule 3
    (MEOWURI_GEN_CONTENTS_MIMETYPE, 'image/jpeg'),
    (MEOWURI_FS_XPLAT_BASENAME_EXT, 'jpg'),
    (MEOWURI_FS_XPLAT_BASENAME_FULL, 'DCIM*'),
    (MEOWURI_FS_XPLAT_PATHNAME_FULL, '~/Pictures/incoming'),
    (MEOWURI_EXT_EXIFTOOL_EXIFDATETIMEORIGINAL, 'Defined'),

    # Part of Rule 4
    (MEOWURI_GEN_CONTENTS_MIMETYPE, 'application/epub+zip'),
    (MEOWURI_FS_XPLAT_BASENAME_EXT, 'epub'),
    (MEOWURI_FS_XPLAT_BASENAME_FULL, '.*'),
    (MEOWURI_FS_XPLAT_PATHNAME_FULL, '.*'),
    ('extractor.metadata.exiftool.XMP-dc:Creator', 'Defined'),
]


DUMMY_RAW_RULE_DATA_SOURCES = [
    # Part of Rule 1
    {'datetime': 'extractor.metadata.exiftool.PDF:CreateDate',
     'extension': MEOWURI_FS_XPLAT_BASENAME_EXT,
     'title': MEOWURI_FS_XPLAT_BASENAME_PREFIX},

    # Part of Rule 2
    {'datetime': MEOWURI_EXT_EXIFTOOL_EXIFDATETIMEORIGINAL,
     'description': 'plugin.microsoft_vision.caption',
     'extension': MEOWURI_FS_XPLAT_BASENAME_EXT},

    # Part of Rule 3
    {'datetime': MEOWURI_EXT_EXIFTOOL_EXIFCREATEDATE,
     'description': 'plugin.microsoft_vision.caption',
     'extension': MEOWURI_FS_XPLAT_BASENAME_EXT},

    # Part of Rule 4
    {'author': 'extractor.metadata.exiftool.XMP-dc:CreatorFile-as',
     'datetime': 'extractor.metadata.exiftool.XMP-dc:Date',
     'extension': MEOWURI_FS_XPLAT_BASENAME_EXT,
     'publisher': 'extractor.metadata.exiftool.XMP-dc:Publisher',
     'title': 'extractor.metadata.exiftool.XMP-dc:Title'},
]


# Dummy internal data structure with (supposedly) valid fields and sources.
RESULTS_DATA_STRUCTURE = {
    'filesystem': {
        'basename': {
            'full': None,
            'prefix': None,
            'suffix': None,
            'extension': None,
            'derived_data': {
                'datetime': None,
            }
        },
        'pathname': {
            'full': None,
            'parent': None
        },
        'date_accessed': None,
        'date_created': None,
        'date_modified': None,
    },
    'contents': {
        'mime_type': None,
        'textual': {
            'raw_text': None,
            'paginated': False,
            'number_pages': None,
        },
        'visual': {
            'ocr_text': None,
            'ocr_description': None,
            'ocr_tags': None
        },
        'binary': {
            'placeholder_field': None,
        }
    },
    'extractor': {
        'metadata': {
            'exiftool': {
                'EXIF:DateTimeOriginal': None,
                'PDF:Author': None,
                'PDF:CreateDate': None,
                'PDF:Creator': None,
                'PDF:EBX_PUBLISHER': None,
                'PDF:Producer': None,
                'PDF:Subject': None,
                'PDF:Title': None,
                'XMP:Creator': None,
                'XMP:EbxPublisher': None,
                'XMP:Title': None,
                'XMP-dc:Creator': None,
                'XMP-dc:EbxPublisher': None,
                'XMP-dc:Title': None,
            },
        }
    },
    'metadata': {
        'pypdf': {
            'Author': None,
            'Creator': None,
            'Producer': None,
            'Subject': None,
            'Title': None,
            'EBX_PUBLISHER': None,
        }
    },
    'plugin': {
        'microsoft_vision': None,
        'guessit': None,
    }
}

# Static dummy data sources used in the 'Repository' unit tests.
__flat_results_data_structure = util.flatten_dict(RESULTS_DATA_STRUCTURE)
VALID_DATA_SOURCES = list(__flat_results_data_structure.keys())


# Sources to search for extractor classes.
EXTRACTOR_CLASS_PACKAGES = ['filesystem', 'metadata', 'text']
EXTRACTOR_CLASS_MODULES = []

# Various test files (hopefully) included with the sources.
DEFAULT_YAML_CONFIG_BASENAME = 'default_config.yaml'
