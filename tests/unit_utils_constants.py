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


# Constants used to construct dummy/mock test fixtures.
DUMMY_RAW_RULE_CONDITIONS = [
    # Part of Rule 1
    ('filesystem.contents.mime_type', 'application/pdf'),
    ('filesystem.basename.extension', 'pdf'),
    ('filesystem.basename.full', 'gmail.pdf'),

    # Part of Rule 2
    ('filesystem.contents.mime_type', 'image/jpeg'),
    ('filesystem.basename.full', 'smulan.jpg'),

    # Part of Rule 3
    ('filesystem.contents.mime_type', 'image/jpeg'),
    ('filesystem.basename.extension', 'jpg'),
    ('filesystem.basename.full', 'DCIM*'),
    ('filesystem.pathname.full', '~/Pictures/incoming'),
    ('metadata.exiftool.EXIF:DateTimeOriginal', 'Defined'),

    # Part of Rule 4
    ('filesystem.contents.mime_type', 'application/epub+zip'),
    ('filesystem.basename.extension', 'epub'),
    ('filesystem.basename.full', '.*'),
    ('filesystem.pathname.full', '.*'),
    ('metadata.exiftool.XMP-dc:Creator', 'Defined'),
]


DUMMY_RAW_RULE_DATA_SOURCES = [
    # Part of Rule 1
    {'datetime': 'metadata.exiftool.PDF:CreateDate',
     'extension': 'filesystem.basename.extension',
     'title': 'filesystem.basename.prefix'},

    # Part of Rule 2
    {'datetime': 'metadata.exiftool.EXIF:DateTimeOriginal',
     'description': 'plugin.microsoft_vision.caption',
     'extension': 'filesystem.basename.extension'},

    # Part of Rule 3
    {'datetime': 'metadata.exiftool.EXIF:CreateDate',
     'description': 'plugin.microsoft_vision.caption',
     'extension': 'filesystem.basename.extension'},

    # Part of Rule 4
    {'author': 'metadata.exiftool.XMP-dc:CreatorFile-as',
     'datetime': 'metadata.exiftool.XMP-dc:Date',
     'extension': 'filesystem.basename.extension',
     'publisher': 'metadata.exiftool.XMP-dc:Publisher',
     'title': 'metadata.exiftool.XMP-dc:Title'},
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
