# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg <autonameow@jonasjberg.com>
#   Source repository: https://github.com/jonasjberg/autonameow
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

from core.metadata.canonicalize import canonicalize_creatortool
from extractors import ExtractorError
from extractors.metadata.base import BaseMetadataExtractor
from thirdparty import pyexiftool
from util import process


IGNORED_EXIFTOOL_TAGNAMES = frozenset([
    'ExifTool:ExifToolVersion',
    'ExifTool:Warning',
    'Palm:CreatorBuildNumber',
    'Palm:CreatorBuildNumber2',
    'Palm:CreatorMajorVersion',
    'Palm:CreatorMinorVersion',
    'Palm:Watermark',
    'XML:CustomBooleanPropertyNameNo',  # not useful
    'XML:CustomBooleanPropertyNameYes',  # not useful
    'XML:CustomDateProperty1-1-2001',  # invalid or non-standard
    'XML:CustomNumberProperty42',  # not useful
    'XML:CustomTextPropertyValue',  # could be anything
    'XML:MyCustomBoolean',  # could be anything
    'XML:MyCustomNumber',  # could be anything
    'XML:MyCustomString',  # could be anything
    'XMP:Extracted-textStoriesNFKC_UTF8_Zlib_Base64',
    'XMP:PageImage',
    'XMP:ProfileBlob',
    'ZIP:ZipBitFlag',
    'ZIP:ZipCompression',
    'ZIP:ZipRequiredVersion',
])


# Metadata to ignore per field. Note that the values are set literals.
BAD_EXIFTOOL_METADATA = {
    'Palm:Author': {
        'Author',
        'Unknown',
    },
    'Palm:Contributor': {
        'calibre (2.85.1) [https://calibre-ebook.com]',
        'calibre (3.6.0) [https://calibre-ebook.com]',
    },
    'PDF:Author': {
        'Author',
        'First Edition',
        'Second Edition',
        'Third Edition',
    },
    'PDF:Subject': {
        'Subject',
    },
    'PDF:Title': {
        'DjVu Document',
        'Title',
    },
    'XMP:Author': {
        'Author',
        'Creator',
        'First Edition',
        'Second Edition',
        'Third Edition',
    },
    'XMP:Contributor': {
        'calibre (2.85.1) [https://calibre-ebook.com]',
        'calibre (3.6.0) [https://calibre-ebook.com]',
        'eCore v0.9.5.630 [ http://www.epubor.com/ecore.html ]',
        'Epubor',
        'http://www.epubor.com',
        'Ultimate',
    },
    'XMP:Creator': {
        'Author',
        'Creator',
        'First Edition',
        'Second Edition',
        'Third Edition',
    },
    'XMP:Description': {
        'Description',
        'Subject',
    },
    'XMP:Subject': {
        'Description',
        'Subject',
    },
    'XMP:Title': {
        'DjVu Document',
        'Title',
    },
}

# Metadata to ignore in all fields.
BAD_EXIFTOOL_METADATA_ANY_TAG = frozenset([
    ' 4<8=8AB@0B>@',
    '()',
    '--=--',
    '-=-',
    '-=--',
    '-|-  this layout: dynstab  -|-',
    '.',
    '0101:01:01 00:00:00+00:00',
    '4<8=8AB@0B>@',
    '\376\377\000A\000b\000D\000o',
    '\x104<8=8AB@0B>@',
    'Advanced PDF Repair at http://www.datanumen.com/apdfr/',
    'free-ebooks.net',
    'http://cncmanual.com/',
    'http://freepdf-books.com',
    'http://www.epubor.com',
    'MyStringValue',
    'test',
    'Toolkit http://www.activepdf.com',
    'Toolkit http://www.activepdf.com(Infix)',
    'Unknown',
    'UNKNOWN',
    'Value',
    'www.allitebooks.com',
    'www.ebook777.com',
    'www.free-ebooks.net',
    'www.it-ebooks.info',
    'www.itbookshub.com',
    'ÿþ',
    'ÿþA',
    'ÿþS',
    '박상현',
])


class ExiftoolMetadataExtractor(BaseMetadataExtractor):
    """
    Extracts various types of metadata using "exiftool".
    """
    HANDLES_MIME_TYPES = [
        'application/epub+zip',
        'application/msword',
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'image/*',
        'text/*',
        'video/*',
    ]
    IS_SLOW = False

    def __init__(self):
        super().__init__()

        self._exiftool = None
        self._initialize_exiftool_instance()

    def extract(self, fileobject, **kwargs):
        return self._get_metadata(fileobject.abspath)

    def shutdown(self):
        self._shutdown_exiftool_instance()

    def _initialize_exiftool_instance(self):
        # Instantiate at first use and remain available for re-use for any
        # additional extraction. Make sure it is properly closed at program
        # exit to prevent any kind of resource leaks.
        try:
            et = pyexiftool.ExifTool()
            et.start()
        except (OSError, ValueError) as e:
            # ValueError can be raised by 'pyexiftool' when aborting with CTRL-C.
            #
            #     self._process.stdin.write(b"-stay_open\nFalse\n")
            #     ValueError: write to closed file
            #
            raise ExtractorError(e)
        else:
            self._exiftool = et

    def _shutdown_exiftool_instance(self):
        if self._exiftool:
            try:
                self._exiftool.terminate()
            except BrokenPipeError:
                # "thirdparty/pyexiftool/exiftool.py", line 185, in terminate
                #     self._process.stdin.flush()
                # BrokenPipeError: [Errno 32] Broken pipe
                pass

            self._exiftool = None

    def _get_exiftool_data(self, filepath):
        """
        Returns:
            Exiftool results as a dictionary of strings/ints/floats.
        """
        assert self._exiftool
        try:
            try:
                return self._exiftool.get_metadata(filepath)
            except (AttributeError, ValueError, TypeError) as e:
                # Raises ValueError if an ExifTool instance isn't running.
                raise ExtractorError(e)
        except (OSError, ValueError) as e:
            # ValueError can be raised by 'pyexiftool' when aborting with CTRL-C.
            #
            #     self._process.stdin.write(b"-stay_open\nFalse\n")
            #     ValueError: write to closed file
            #
            raise ExtractorError(e)

    def _get_metadata(self, filepath):
        raw_metadata = self._get_exiftool_data(filepath)
        if not raw_metadata:
            return dict()

        filtered_metadata = self._filter_raw_data(raw_metadata)
        metadata = self._to_internal_format(filtered_metadata)
        # TODO: [TD0034] Filter out known bad data.
        # TODO: [TD0035] Use per-extractor, per-field, etc., blacklists?
        return metadata

    def _filter_raw_data(self, raw_metadata):
        # TODO: [TD0034] Filter out known bad data.
        # TODO: [TD0035] Use per-extractor, per-field, etc., blacklists?
        return {tag: value for tag, value in raw_metadata.items()
                if value is not None
                and not is_empty_string(value)
                and not is_ignored_tagname(tag)
                and not is_binary_blob(value)
                and not is_bad_metadata(tag, value)}

    def _to_internal_format(self, raw_metadata):
        coerced_metadata = dict()

        for field, value in raw_metadata.items():
            coerced = self.coerce_field_value(field, value)
            # Empty strings are being passed through. But if we test with
            # 'if coerced', any False booleans, 0, etc. would be discarded.
            # Filtering must be field-specific.
            if coerced is not None:
                filtered = _filter_coerced_value(coerced)
                if filtered is not None:
                    coerced_metadata[field] = filtered

        return coerced_metadata

    @classmethod
    def can_handle(cls, fileobject):
        return bool(
            cls._evaluate_mime_type_glob(fileobject)
            or is_kindle_ebook(fileobject)
        )

    @classmethod
    def dependencies_satisfied(cls):
        return process.is_executable('exiftool') and pyexiftool is not None


def is_kindle_ebook(fileobject):
    return bool(
        fileobject.mime_type == 'application/octet-stream'
        and fileobject.basename_suffix in (b'azw3', b'azw4')
    )


def is_bad_metadata(tag_name, value):
    if isinstance(value, list):
        return bool(any(
            v in BAD_EXIFTOOL_METADATA_ANY_TAG
            or v in BAD_EXIFTOOL_METADATA.get(tag_name, set())
            for v in value
        ))
    return bool(
        value in BAD_EXIFTOOL_METADATA_ANY_TAG
        or value in BAD_EXIFTOOL_METADATA.get(tag_name, set())
    )


def is_binary_blob(value):
    return isinstance(value, str) and 'use -b option to extract' in value


def is_ignored_tagname(tagname):
    return bool(tagname in IGNORED_EXIFTOOL_TAGNAMES)


def is_empty_string(value):
    if isinstance(value, (str, bytes)) and not value.strip():
        return True
    return False


def _filter_coerced_value(value):
    # TODO: [TD0034] Remove duplicated functionality (coercers normalize?)
    def __filter_value(_value):
        if not isinstance(_value, (bytes, str)):
            return _value
        return _value if _value.strip() else None

    if not isinstance(value, list):
        return __filter_value(value)
    else:
        assert isinstance(value, list)
        list_of_non_empty_values = [v for v in value if __filter_value(v)]
        if list_of_non_empty_values:
            return list_of_non_empty_values
    return None
