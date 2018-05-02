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
import re


_PATH_THIS_DIR = os.path.abspath(os.path.dirname(__file__))
_PATH_THIS_DIR_PARENT_PARENT = os.path.normpath(os.path.join(
    _PATH_THIS_DIR, os.pardir, os.pardir
))


def join_path_from_srcroot(*components):
    return os.path.normpath(os.path.join(
        _PATH_THIS_DIR_PARENT_PARENT, *components
    ))


PATH_TEST_FILES = join_path_from_srcroot('test_files')
PATH_TESTS_REGRESSION = join_path_from_srcroot('tests', 'regression')
PATH_TESTS_UNIT = join_path_from_srcroot('tests', 'unit')
PATH_AUTONAMEOW_SRCROOT = join_path_from_srcroot('autonameow')


PATH_USER_HOME = os.path.expanduser('~')


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

MEOWURI_FS_FILETAGS_DATETIME = 'extractor.filesystem.filetags.datetime'
MEOWURI_FS_FILETAGS_DESCRIPTION = 'extractor.filesystem.filetags.description'
MEOWURI_FS_FILETAGS_EXTENSION = 'extractor.filesystem.filetags.extension'
MEOWURI_FS_FILETAGS_FOLLOWS = 'extractor.filesystem.filetags.follows_filetags_convention'
MEOWURI_FS_FILETAGS_TAGS = 'extractor.filesystem.filetags.tags'

MEOWURI_FS_XPLAT_MIMETYPE = 'extractor.filesystem.xplat.mime_type'
MEOWURI_FS_XPLAT_ABSPATH_FULL = 'extractor.filesystem.xplat.abspath_full'
MEOWURI_FS_XPLAT_EXTENSION = 'extractor.filesystem.xplat.extension'
MEOWURI_FS_XPLAT_BASENAME_FULL = 'extractor.filesystem.xplat.basename_full'
MEOWURI_FS_XPLAT_BASENAME_PREFIX = 'extractor.filesystem.xplat.basename_prefix'
MEOWURI_FS_XPLAT_BASENAME_SUFFIX = 'extractor.filesystem.xplat.basename_suffix'
MEOWURI_FS_XPLAT_PATHNAME_FULL = 'extractor.filesystem.xplat.pathname_full'
MEOWURI_FS_XPLAT_PATHNAME_PARENT = 'extractor.filesystem.xplat.pathname_parent'

MEOWURI_GEN_CONTENTS_MIMETYPE = 'generic.contents.mime_type'
MEOWURI_GEN_CONTENTS_TEXT = 'generic.contents.text'
MEOWURI_GEN_METADATA_AUTHOR = 'generic.metadata.author'
MEOWURI_GEN_METADATA_CREATOR = 'generic.metadata.creator'
MEOWURI_GEN_METADATA_PRODUCER = 'generic.metadata.producer'
MEOWURI_GEN_METADATA_SUBJECT = 'generic.metadata.subject'
MEOWURI_GEN_METADATA_TAGS = 'generic.metadata.tags'
MEOWURI_GEN_METADATA_TITLE = 'generic.metadata.title'
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

MEOWURI_EXT_GUESSIT_DATE = 'extractor.filesystem.guessit.date'
MEOWURI_EXT_GUESSIT_TITLE = 'extractor.filesystem.guessit.title'
MEOWURI_EXT_GUESSIT_TYPE = 'extractor.filesystem.guessit.type'


ALL_FULL_MEOWURIS = frozenset([
    MEOWURI_AZR_FILENAME_DATETIME,
    MEOWURI_AZR_FILENAME_PUBLISHER,
    MEOWURI_AZR_FILENAME_TAGS,
    MEOWURI_AZR_FILENAME_TITLE,
    MEOWURI_FS_FILETAGS_DATETIME,
    MEOWURI_FS_FILETAGS_DESCRIPTION,
    MEOWURI_FS_FILETAGS_EXTENSION,
    MEOWURI_FS_FILETAGS_FOLLOWS,
    MEOWURI_FS_FILETAGS_TAGS,
    MEOWURI_FS_XPLAT_MIMETYPE,
    MEOWURI_FS_XPLAT_ABSPATH_FULL,
    MEOWURI_FS_XPLAT_EXTENSION,
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
    MEOWURI_GEN_METADATA_TITLE,
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
    MEOWURI_EXT_GUESSIT_DATE,
    MEOWURI_EXT_GUESSIT_TITLE,
    MEOWURI_EXT_GUESSIT_TYPE,
])

# Collected 2018-02-03 when running autonameow on all files in 'test_files'.
# Modified 2018-02-20 with changes to CrossPlatformFileSystemExtractor leaves.
DUMPED_MEOWURIS = frozenset([
    'analyzer.document.publisher',
    'analyzer.document.title',
    'analyzer.ebook.author',
    'analyzer.ebook.date',
    'analyzer.ebook.edition',
    'analyzer.ebook.publisher',
    'analyzer.ebook.title',
    'analyzer.filename.datetime',
    'analyzer.filename.edition',
    'analyzer.filename.extension',
    'analyzer.filename.publisher',
    # 'analyzer.filetags.datetime',  This is an extractor now
    # 'analyzer.filetags.description',  This is an extractor now
    # 'analyzer.filetags.extension',  This is an extractor now
    # 'analyzer.filetags.follows_filetags_convention',  This is an extractor now
    'extractor.filesystem.xplat.abspath_full',
    'extractor.filesystem.xplat.extension',
    'extractor.filesystem.xplat.basename_full',
    'extractor.filesystem.xplat.basename_prefix',
    'extractor.filesystem.xplat.basename_suffix',
    'extractor.filesystem.xplat.mime_type',
    'extractor.filesystem.xplat.date_accessed',
    'extractor.filesystem.xplat.date_created',
    'extractor.filesystem.xplat.date_modified',
    'extractor.filesystem.xplat.pathname_full',
    'extractor.filesystem.xplat.pathname_parent',
    'extractor.metadata.exiftool.EXIF:CreateDate',
    'extractor.metadata.exiftool.EXIF:DateTimeDigitized',
    'extractor.metadata.exiftool.EXIF:DateTimeOriginal',
    'extractor.metadata.exiftool.File:Directory',
    'extractor.metadata.exiftool.File:FileAccessDate',
    'extractor.metadata.exiftool.File:FileInodeChangeDate',
    'extractor.metadata.exiftool.File:FileModifyDate',
    'extractor.metadata.exiftool.File:FileName',
    'extractor.metadata.exiftool.File:FilePermissions',
    'extractor.metadata.exiftool.File:FileSize',
    'extractor.metadata.exiftool.File:FileType',
    'extractor.metadata.exiftool.File:FileTypeExtension',
    'extractor.metadata.exiftool.File:MIMEType',
    'extractor.metadata.exiftool.PDF:CreateDate',
    'extractor.metadata.exiftool.PDF:Creator',
    'extractor.metadata.exiftool.PDF:Linearized',
    'extractor.metadata.exiftool.PDF:ModifyDate',
    'extractor.metadata.exiftool.PDF:PDFVersion',
    'extractor.metadata.exiftool.PDF:PageCount',
    'extractor.metadata.exiftool.PDF:Producer',
    'extractor.metadata.exiftool.SourceFile',
    'extractor.text.epub.full',
    'extractor.text.pdf.full',
    'generic.contents.mime_type',
    'generic.contents.text',
    'generic.metadata.author',
    'generic.metadata.creator',
    'generic.metadata.date_created',
    'generic.metadata.date_modified',
    'generic.metadata.description',
    'generic.metadata.edition',
    'generic.metadata.producer',
    'generic.metadata.publisher',
    'generic.metadata.subject',
    'generic.metadata.tags',
    'generic.metadata.title',
])


DUMMY_MAPPED_MEOWURIS = list({
    'analyzer.document',
    'analyzer.ebook',
    'analyzer.filename',
    # 'analyzer.filetags',  This is an extractor now
    'extractor.filesystem.xplat',
    'extractor.filesystem.guessit',
    'extractor.metadata.exiftool',
    'extractor.metadata.jpeginfo',
    'extractor.text.pdf',
    'extractor.text.plain',
    'extractor.text.tesseractocr',
})


# Constants used to construct dummy/mock test fixtures.
DUMMY_RAW_RULE_CONDITIONS = [
    (MEOWURI_GEN_CONTENTS_MIMETYPE, 'application/pdf'),
    (MEOWURI_FS_XPLAT_EXTENSION, 'pdf'),
    (MEOWURI_FS_XPLAT_BASENAME_FULL, 'gmail.pdf'),

    (MEOWURI_FS_XPLAT_BASENAME_FULL, 'smulan.jpg'),

    (MEOWURI_GEN_CONTENTS_MIMETYPE, 'image/jpeg'),
    (MEOWURI_FS_XPLAT_EXTENSION, 'jpg'),
    (MEOWURI_FS_XPLAT_BASENAME_FULL, 'DCIM*'),
    (MEOWURI_FS_XPLAT_PATHNAME_FULL, '~/Pictures/incoming'),
    (MEOWURI_EXT_EXIFTOOL_EXIFDATETIMEORIGINAL, 'Defined'),

    (MEOWURI_GEN_CONTENTS_MIMETYPE, 'application/epub+zip'),
    (MEOWURI_FS_XPLAT_EXTENSION, 'epub'),
    (MEOWURI_FS_XPLAT_BASENAME_FULL, '.*'),
    (MEOWURI_FS_XPLAT_PATHNAME_FULL, '.*'),
    (MEOWURI_EXT_EXIFTOOL_XMPDCCREATOR, 'Defined'),
]


DUMMY_RAW_RULE_DATA_SOURCES = [
    # Part of Rule 1
    {'datetime': MEOWURI_EXT_EXIFTOOL_PDFCREATEDATE,
     'extension': MEOWURI_FS_XPLAT_EXTENSION,
     'title': MEOWURI_FS_XPLAT_BASENAME_PREFIX},

    # Part of Rule 2
    {'datetime': MEOWURI_EXT_EXIFTOOL_EXIFDATETIMEORIGINAL,
     'extension': MEOWURI_FS_XPLAT_EXTENSION},

    # Part of Rule 3
    {'datetime': [
        MEOWURI_EXT_EXIFTOOL_EXIFCREATEDATE,
        MEOWURI_EXT_EXIFTOOL_EXIFDATETIMEORIGINAL
     ],
     'extension': MEOWURI_FS_XPLAT_EXTENSION},

    # Part of Rule 4
    {'author': MEOWURI_EXT_EXIFTOOL_XMPDCCREATORFILEAS,
     'datetime': MEOWURI_EXT_EXIFTOOL_XMPDCDATE,
     'extension': MEOWURI_FS_XPLAT_EXTENSION,
     'publisher': MEOWURI_EXT_EXIFTOOL_XMPDCPUBLISHER,
     'title': MEOWURI_EXT_EXIFTOOL_XMPDCTITLE},
]


# Various test files (hopefully) included with the sources.
DEFAULT_YAML_CONFIG_BASENAME = 'default.yaml'


# This is not clearly defined otherwise.
BUILTIN_REGEX_TYPE = type(re.compile(''))
