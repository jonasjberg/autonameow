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

import logging as log

import PyPDF2
import re
from PyPDF2.utils import (
    PdfReadError
)
from datetime import datetime

from core.exceptions import ExtractorError
from core.util import wrap_exiftool
from core import (
    util,
    types
)
from extractors.extractor import Extractor


class MetadataExtractor(Extractor):
    handles_mime_types = []
    data_query_string = None

    # Lookup table that maps extractor-specific field names to wrapper classes.
    tagname_type_lookup = {}

    def __init__(self, source):
        super(MetadataExtractor, self).__init__(source)

        self._raw_metadata = None
        self.metadata = None

    def query(self, field=None):
        """
        Queries this extractor for a specific field or all field if argument
        "field" is left unspecified.

        Args:
            field: Optional refinement of the query.
                All fields are returned by default.

        Returns:
            The specified fields or False if the extraction fails.
        """
        if not self.metadata:
            try:
                log.debug('{!s} received initial query ..'.format(self))
                self._raw_metadata = self._get_raw_metadata()
            except ExtractorError as e:
                log.error('{!s} query FAILED: {!s}'.format(self, e))
                return False
            except NotImplementedError as e:
                log.debug('[WARNING] Called unimplemented code in {!s}: '
                          '{!s}'.format(self, e))
                return False

        # Internal data format boundary.  Wrap "raw" data with type classes.
        self.metadata = self._to_internal_format(self._raw_metadata)

        if not field:
            log.debug('{!s} responding to query for all fields'.format(self))
            return self.metadata
        else:
            log.debug('{!s} responding to query for field: '
                      '"{!s}"'.format(self, field))
            return self.metadata.get(field, False)

    def _to_internal_format(self, raw_metadata):
        out = {}
        for tag_name, value in raw_metadata.items():
            out[tag_name] = self._wrap_raw(tag_name, value)
        return out

    def _wrap_raw(self, tag_name, value):
        if tag_name in self.tagname_type_lookup:
            return self.tagname_type_lookup[tag_name](value)
        else:
            wrapped = types.try_wrap(value)
            if wrapped is not None:
                return wrapped
            else:
                log.critical('Unhandled wrapping of tag name "{}" '
                             '(value: "{}")'.format(tag_name, value))
                return value

    def _get_raw_metadata(self):
        raise NotImplementedError('Must be implemented by inheriting classes.')


class ExiftoolMetadataExtractor(MetadataExtractor):
    """
    Extracts various types of metadata using "exiftool".
    """
    handles_mime_types = ['video/*', 'application/pdf', 'image/*',
                          'application/epub+zip', 'text/*']
    data_query_string = 'metadata.exiftool'

    # TODO: [TD0002] Wrap values in custom types.
    # TODO: [TD0044] Rework converting "raw data" to an internal format.
    tagname_type_lookup = {
        'Composite:Aperture': types.AW_FLOAT,
        'Composite:ImageSize': types.AW_STRING,
        'Composite:HyperfocalDistance': types.AW_FLOAT,
        'EXIF:CreateDate': types.AW_EXIFTOOLTIMEDATE,
        'EXIF:DateTimeDigitized': types.AW_EXIFTOOLTIMEDATE,
        'EXIF:DateTimeOriginal': types.AW_EXIFTOOLTIMEDATE,
        'EXIF:ExifVersion': types.AW_INTEGER,
        'EXIF:GainControl': types.AW_INTEGER,
        'EXIF:ImageDescription': types.AW_STRING,
        'EXIF:Make': types.AW_STRING,
        'EXIF:ModifyDate': types.AW_EXIFTOOLTIMEDATE,
        'EXIF:Software': types.AW_STRING,
        'EXIF:UserComment': types.AW_STRING,
        'ExifTool:Error': types.AW_STRING,
        'ExifTool:ExifToolVersion': types.AW_FLOAT,
        'File:Directory': types.AW_PATH,
        'File:FileAccessDate': types.AW_EXIFTOOLTIMEDATE,
        'File:FileInodeChangeDate': types.AW_EXIFTOOLTIMEDATE,
        'File:FileModifyDate': types.AW_EXIFTOOLTIMEDATE,
        'File:FileName': types.AW_PATH,
        'File:FilePermissions': types.AW_INTEGER,
        'File:FileSize': types.AW_INTEGER,
        'File:FileType': types.AW_STRING,
        'File:FileTypeExtension': types.AW_PATH,
        'File:ImageHeight': types.AW_INTEGER,
        'File:ImageWidth': types.AW_INTEGER,
        'File:MIMEType': types.AW_STRING,
        'PDF:CreateDate': types.AW_EXIFTOOLTIMEDATE,
        'PDF:Creator': types.AW_STRING,
        'PDF:Linearized': types.AW_BOOLEAN,
        'PDF:ModifyDate': types.AW_EXIFTOOLTIMEDATE,
        'PDF:PDFVersion': types.AW_FLOAT,
        'PDF:PageCount': types.AW_INTEGER,
        'PDF:Producer': types.AW_STRING,
        'SourceFile': types.AW_PATH,
    }

    def __init__(self, source):
        super(ExiftoolMetadataExtractor, self).__init__(source)
        self._raw_metadata = None

    def _get_raw_metadata(self):
        try:
            result = self._get_exiftool_data()
        except Exception as e:
            raise ExtractorError(e)
        else:
            return result

    def _get_exiftool_data(self):
        """
        Returns:
            Exiftool results as a dictionary of strings/ints/floats.
        """
        with wrap_exiftool.ExifTool() as et:
            # Raises ValueError if an ExifTool instance isn't running.
            try:
                return et.get_metadata(self.source)
            except (AttributeError, ValueError, TypeError):
                raise


class PyPDFMetadataExtractor(MetadataExtractor):
    handles_mime_types = ['application/pdf']
    data_query_string = 'metadata.pypdf'

    # TODO: [TD0002] Wrap values in custom types.
    # TODO: [TD0044] Rework converting "raw data" to an internal format.
    tagname_type_lookup = {
        'Creator': types.AW_STRING,
        'CreationDate': types.AW_TIMEDATE,
        'Encrypted': types.AW_BOOLEAN,
        'ModDate': types.AW_TIMEDATE,
        'NumberPages': types.AW_INTEGER,
        'Paginated': types.AW_BOOLEAN,
        'Producer': types.AW_STRING,
    }

    def __init__(self, source):
        super(PyPDFMetadataExtractor, self).__init__(source)
        self._raw_metadata = None

    def _get_raw_metadata(self):
        try:
            return self._get_pypdf_data()
        except Exception as e:
            raise ExtractorError(e)

    def _get_pypdf_data(self):
        out = {}

        try:
            # NOTE(jonas): [encoding] Double-check PyPDF2 docs ..
            file_reader = PyPDF2.PdfFileReader(util.decode_(self.source), 'rb')
        except Exception:
            # TODO: Raise custom exception .. ?
            raise
        else:
            doc_info = file_reader.getDocumentInfo()
            if doc_info:
                # Remove any leading '/' from all dict keys.
                out = {k.lstrip('\/'): v for k, v in doc_info.items()}

                # Convert PyPDF values of type 'PyPDF2.generic.TextStringObject'
                out = {k: str(v) for k, v in out.items()}

            out.update({'Encrypted': file_reader.isEncrypted})

            try:
                num_pages = file_reader.getNumPages()
            except PdfReadError:
                # PDF document might be encrypted with restrictions for reading.
                # TODO: Raise custom exception .. ?
                raise
            else:
                out.update({'NumberPages': num_pages})
                out.update({'Paginated': True})

            # https://pythonhosted.org/PyPDF2/XmpInformation.html
            xmp_metadata = file_reader.getXmpMetadata()
            if xmp_metadata:
                xmp = {}
                for k, v in xmp_metadata.items():
                    if v:
                        xmp[k] = v

                out.update(xmp)

        # TODO: [TD0044] Convert date/time-information to 'datetime' objects.
        # TODO: [TD0002] Wrap values in custom types.
        convert_datetime_field(out, 'CreationDate')
        convert_datetime_field(out, 'ModDate')

        return out


def convert_datetime_field(pypdf_data, field):
    # TODO: [TD0044] This will be done a lot, needs refactoring!
    if field in pypdf_data:
        try:
            datetime_object = to_datetime(pypdf_data[field])
            # wrapped = types.TimeDate(pypdf_data[field])
        except ValueError:
            return
        else:
            pypdf_data[field] = datetime_object
            # pypdf_data[field] = wrapped


def to_datetime(pypdf_string):
    # TODO: [TD0044] This will be done a lot, needs refactoring!
    #
    # Expected date format:           D:20121225235237 +05'30'
    #                                   ^____________^ ^_____^
    # Regex search matches two groups:        #1         #2
    #
    # 'D:20160111124132+00\\'00\\''
    if not pypdf_string:
        raise ValueError('Got empty/None string from PyPDF')

    found_match = False

    log.debug('to_datetime got raw PyPDF string: "{!s}"'.format(pypdf_string))

    if "'" in pypdf_string:
        pypdf_string = pypdf_string.replace("'", '')

    re_datetime_tz = re.compile('D:(\d{14})(\+\d{2}\'\d{2}\')')
    re_match_tz = re_datetime_tz.search(pypdf_string)
    if re_match_tz:
        datetime_str = re_match_tz.group(1)
        timezone_str = re_match_tz.group(2)
        timezone_str = timezone_str.replace("'", "")

        try:
            dt = datetime.strptime(str(datetime_str + timezone_str),
                                   "%Y%m%d%H%M%S%z")
            found_match = True
        except ValueError:
            pass

        if not found_match:
            try:
                dt = datetime.strptime(datetime_str, "%Y%m%d%H%M%S")
                found_match = True
            except ValueError:
                log.debug('Unable to convert to naive datetime: '
                          '"{}"'.format(pypdf_string))

    # Try matching another pattern.
    re_datetime_no_tz = re.compile(r'D:(\d{14})')
    re_match = re_datetime_no_tz.search(pypdf_string)
    if re_match:
        try:
            dt = datetime.strptime(re_match.group(1), '%Y%m%d%H%M%S')
            found_match = True
        except ValueError:
            pass

    if found_match:
        return dt
    else:
        raise ValueError
