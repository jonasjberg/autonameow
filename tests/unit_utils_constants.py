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
