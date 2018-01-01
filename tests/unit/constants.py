#!/usr/bin/env python3
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

import os

from util import encoding as enc

_THIS_DIR = os.path.abspath(os.path.dirname(__file__))
_PARENT_PARENT_DIR = os.path.normpath(os.path.join(
    _THIS_DIR, os.pardir, os.pardir
))
TEST_FILES_DIR = os.path.normpath(os.path.join(
    _PARENT_PARENT_DIR, 'test_files'
))
REGRESSIONTEST_DIR = os.path.normpath(os.path.join(
    _PARENT_PARENT_DIR, 'tests', 'regression'
))
AUTONAMEOW_SRCROOT_DIR = os.path.normpath(os.path.join(
    _PARENT_PARENT_DIR, enc.syspath('autonameow')
))


REGRESSIONTEST_DIR_BASENAMES = [
    b'0000_unittest_dummy',
    b'0001',
    b'0001_duplicate_inputpath',
    b'0002',
    b'0003_filetags',
    b'0004_add_extension',
    b'0005_add_extension'
]


ASSUMED_NONEXISTENT_BASENAME = b'not_a_file_surely'


# Full MeowURIs to various data resources.
MEOWURI_AZR_FILENAME_DATETIME = 'analyzer.filename.datetime'
MEOWURI_AZR_FILENAME_PUBLISHER = 'analyzer.filename.publisher'
MEOWURI_AZR_FILENAME_TAGS = 'analyzer.filename.tags'
MEOWURI_AZR_FILENAME_TITLE = 'analyzer.filename.title'

MEOWURI_AZR_FILETAGS_DATETIME = 'analyzer.filetags.datetime'
MEOWURI_AZR_FILETAGS_DESCRIPTION = 'analyzer.filetags.description'
MEOWURI_AZR_FILETAGS_EXTENSION = 'analyzer.filetags.extension'
MEOWURI_AZR_FILETAGS_FOLLOWS = 'analyzer.filetags.follows_filetags_convention'
MEOWURI_AZR_FILETAGS_TAGS = 'analyzer.filetags.tags'

MEOWURI_FS_XPLAT_MIMETYPE = 'extractor.filesystem.xplat.contents.mime_type'
MEOWURI_FS_XPLAT_ABSPATH_FULL = 'extractor.filesystem.xplat.abspath.full'
MEOWURI_FS_XPLAT_BASENAME_EXT = 'extractor.filesystem.xplat.basename.extension'
MEOWURI_FS_XPLAT_BASENAME_FULL = 'extractor.filesystem.xplat.basename.full'
MEOWURI_FS_XPLAT_BASENAME_PREFIX = 'extractor.filesystem.xplat.basename.prefix'
MEOWURI_FS_XPLAT_BASENAME_SUFFIX = 'extractor.filesystem.xplat.basename.suffix'
MEOWURI_FS_XPLAT_PATHNAME_FULL = 'extractor.filesystem.xplat.pathname.full'
MEOWURI_FS_XPLAT_PATHNAME_PARENT = 'extractor.filesystem.xplat.pathname.parent'

MEOWURI_GEN_CONTENTS_MIMETYPE = 'generic.contents.mime_type'
MEOWURI_GEN_CONTENTS_TEXT = 'generic.contents.text'
MEOWURI_GEN_METADATA_AUTHOR = 'generic.metadata.author'
MEOWURI_GEN_METADATA_CREATOR = 'generic.metadata.creator'
MEOWURI_GEN_METADATA_PRODUCER = 'generic.metadata.producer'
MEOWURI_GEN_METADATA_SUBJECT = 'generic.metadata.subject'
MEOWURI_GEN_METADATA_TAGS = 'generic.metadata.tags'
MEOWURI_GEN_METADATA_DATECREATED = 'generic.metadata.date_created'
MEOWURI_GEN_METADATA_DATEMODIFIED = 'generic.metadata.date_modified'

MEOWURI_EXT_EXIFTOOL_EXIFCREATEDATE = 'extractor.metadata.exiftool.EXIF:CreateDate'
MEOWURI_EXT_EXIFTOOL_EXIFDATETIMEORIGINAL = 'extractor.metadata.exiftool.EXIF:DateTimeOriginal'
MEOWURI_EXT_EXIFTOOL_PDFCREATEDATE = 'extractor.metadata.exiftool.PDF:CreateDate'
MEOWURI_EXT_EXIFTOOL_PDFCREATOR = 'extractor.metadata.exiftool.PDF:Creator'
MEOWURI_EXT_EXIFTOOL_PDFMODIFYDATE = 'extractor.metadata.exiftool.PDF:ModifyDate'
MEOWURI_EXT_EXIFTOOL_PDFPRODUCER = 'extractor.metadata.exiftool.PDF:Producer'
MEOWURI_EXT_EXIFTOOL_XMPDCCREATOR = 'extractor.metadata.exiftool.XMP-dc:Creator'
MEOWURI_EXT_EXIFTOOL_XMPDCCREATORFILEAS = 'extractor.metadata.exiftool.XMP-dc:CreatorFile-as'
MEOWURI_EXT_EXIFTOOL_XMPDCDATE = 'extractor.metadata.exiftool.XMP-dc:Date'
MEOWURI_EXT_EXIFTOOL_XMPDCPUBLISHER = 'extractor.metadata.exiftool.XMP-dc:Publisher'
MEOWURI_EXT_EXIFTOOL_XMPDCTITLE = 'extractor.metadata.exiftool.XMP-dc:Title'
MEOWURI_EXT_EXIFTOOL_QTCREATIONDATE = 'extractor.metadata.exiftool.QuickTime:CreationDate'

MEOWURI_PLU_MSVISION_CAPTION = 'plugin.microsoft_vision.caption'
MEOWURI_PLU_GUESSIT_DATE = 'plugin.guessit.date'
MEOWURI_PLU_GUESSIT_TITLE = 'plugin.guessit.title'
MEOWURI_PLU_GUESSIT_TYPE = 'plugin.guessit.type'


ALL_FULL_MEOWURIS = frozenset([
    MEOWURI_AZR_FILENAME_DATETIME,
    MEOWURI_AZR_FILENAME_PUBLISHER,
    MEOWURI_AZR_FILENAME_TAGS,
    MEOWURI_AZR_FILENAME_TITLE,
    MEOWURI_AZR_FILETAGS_DATETIME,
    MEOWURI_AZR_FILETAGS_DESCRIPTION,
    MEOWURI_AZR_FILETAGS_EXTENSION,
    MEOWURI_AZR_FILETAGS_FOLLOWS,
    MEOWURI_AZR_FILETAGS_TAGS,
    MEOWURI_FS_XPLAT_MIMETYPE,
    MEOWURI_FS_XPLAT_ABSPATH_FULL,
    MEOWURI_FS_XPLAT_BASENAME_EXT,
    MEOWURI_FS_XPLAT_BASENAME_FULL,
    MEOWURI_FS_XPLAT_BASENAME_PREFIX,
    MEOWURI_FS_XPLAT_BASENAME_SUFFIX,
    MEOWURI_FS_XPLAT_PATHNAME_FULL,
    MEOWURI_FS_XPLAT_PATHNAME_PARENT,
    MEOWURI_GEN_CONTENTS_MIMETYPE,
    MEOWURI_GEN_CONTENTS_TEXT,
    MEOWURI_GEN_METADATA_AUTHOR,
    MEOWURI_GEN_METADATA_CREATOR,
    MEOWURI_GEN_METADATA_PRODUCER,
    MEOWURI_GEN_METADATA_SUBJECT,
    MEOWURI_GEN_METADATA_TAGS,
    MEOWURI_GEN_METADATA_DATECREATED,
    MEOWURI_GEN_METADATA_DATEMODIFIED,
    MEOWURI_EXT_EXIFTOOL_EXIFCREATEDATE,
    MEOWURI_EXT_EXIFTOOL_EXIFDATETIMEORIGINAL,
    MEOWURI_EXT_EXIFTOOL_PDFCREATEDATE,
    MEOWURI_EXT_EXIFTOOL_PDFCREATOR,
    MEOWURI_EXT_EXIFTOOL_PDFMODIFYDATE,
    MEOWURI_EXT_EXIFTOOL_PDFPRODUCER,
    MEOWURI_EXT_EXIFTOOL_XMPDCCREATOR,
    MEOWURI_EXT_EXIFTOOL_XMPDCCREATORFILEAS,
    MEOWURI_EXT_EXIFTOOL_XMPDCDATE,
    MEOWURI_EXT_EXIFTOOL_XMPDCPUBLISHER,
    MEOWURI_EXT_EXIFTOOL_XMPDCTITLE,
    MEOWURI_EXT_EXIFTOOL_QTCREATIONDATE,
    MEOWURI_PLU_GUESSIT_DATE,
    MEOWURI_PLU_GUESSIT_TITLE,
    MEOWURI_PLU_GUESSIT_TYPE,
    MEOWURI_PLU_MSVISION_CAPTION,
])


DUMMY_MAPPED_MEOWURIS = list({
    'analyzer.document',
    'analyzer.ebook',
    'analyzer.filename',
    'analyzer.filetags',
    'analyzer.image',
    'analyzer.text',
    'analyzer.video',
    'extractor.filesystem.xplat',
    'extractor.metadata.exiftool',
    'extractor.metadata.jpeginfo',
    'extractor.text.pdftotext',
    'extractor.text.plain',
    'extractor.text.tesseractocr',
    'plugin.guessit',
})


# Constants used to construct dummy/mock test fixtures.
DUMMY_RAW_RULE_CONDITIONS = [
    (MEOWURI_GEN_CONTENTS_MIMETYPE, 'application/pdf'),
    (MEOWURI_FS_XPLAT_BASENAME_EXT, 'pdf'),
    (MEOWURI_FS_XPLAT_BASENAME_FULL, 'gmail.pdf'),

    (MEOWURI_FS_XPLAT_BASENAME_FULL, 'smulan.jpg'),

    (MEOWURI_GEN_CONTENTS_MIMETYPE, 'image/jpeg'),
    (MEOWURI_FS_XPLAT_BASENAME_EXT, 'jpg'),
    (MEOWURI_FS_XPLAT_BASENAME_FULL, 'DCIM*'),
    (MEOWURI_FS_XPLAT_PATHNAME_FULL, '~/Pictures/incoming'),
    (MEOWURI_EXT_EXIFTOOL_EXIFDATETIMEORIGINAL, 'Defined'),

    (MEOWURI_GEN_CONTENTS_MIMETYPE, 'application/epub+zip'),
    (MEOWURI_FS_XPLAT_BASENAME_EXT, 'epub'),
    (MEOWURI_FS_XPLAT_BASENAME_FULL, '.*'),
    (MEOWURI_FS_XPLAT_PATHNAME_FULL, '.*'),
    (MEOWURI_EXT_EXIFTOOL_XMPDCCREATOR, 'Defined'),
]


DUMMY_RAW_RULE_DATA_SOURCES = [
    # Part of Rule 1
    {'datetime': MEOWURI_EXT_EXIFTOOL_PDFCREATEDATE,
     'extension': MEOWURI_FS_XPLAT_BASENAME_EXT,
     'title': MEOWURI_FS_XPLAT_BASENAME_PREFIX},

    # Part of Rule 2
    {'datetime': MEOWURI_EXT_EXIFTOOL_EXIFDATETIMEORIGINAL,
     'description': MEOWURI_PLU_MSVISION_CAPTION,
     'extension': MEOWURI_FS_XPLAT_BASENAME_EXT},

    # Part of Rule 3
    {'datetime': [
        MEOWURI_EXT_EXIFTOOL_EXIFCREATEDATE,
        MEOWURI_EXT_EXIFTOOL_EXIFDATETIMEORIGINAL
     ],
     'description': MEOWURI_PLU_MSVISION_CAPTION,
     'extension': MEOWURI_FS_XPLAT_BASENAME_EXT},

    # Part of Rule 4
    {'author': MEOWURI_EXT_EXIFTOOL_XMPDCCREATORFILEAS,
     'datetime': MEOWURI_EXT_EXIFTOOL_XMPDCDATE,
     'extension': MEOWURI_FS_XPLAT_BASENAME_EXT,
     'publisher': MEOWURI_EXT_EXIFTOOL_XMPDCPUBLISHER,
     'title': MEOWURI_EXT_EXIFTOOL_XMPDCTITLE},
]


# Sources to search for extractor classes.
EXTRACTOR_CLASS_PACKAGES = ['filesystem', 'metadata', 'text']
EXTRACTOR_CLASS_MODULES = []

# Various test files (hopefully) included with the sources.
DEFAULT_YAML_CONFIG_BASENAME = 'default.yaml'
