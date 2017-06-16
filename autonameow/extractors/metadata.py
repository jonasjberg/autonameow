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
from PyPDF2.utils import (
    PyPdfError,
    PdfReadError
)

from core.exceptions import ExtractorError
from core.util import wrap_exiftool
from extractors.extractor import Extractor


class MetadataExtractor(Extractor):
    handles_mime_types = []
    data_query_string = None

    def __init__(self, source):
        super(MetadataExtractor, self).__init__(source)

        self._raw_metadata = None

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
        if not self._raw_metadata:
            try:
                log.debug('MetadataExtractor initial query for raw metadata ..')
                self._raw_metadata = self._get_raw_metadata()
            except ExtractorError as e:
                log.error('MetadataExtractor query FAILED: {!s}'.format(e))
                return False
            except NotImplementedError as e:
                log.debug('[WARNING] Called unimplemented code in {!s}: '
                          '{!s}'.format(self, e))
                return False

        if not field:
            log.debug('MetadataExtractor responding to query for all fields')
            return self._raw_metadata
        else:
            log.debug('MetadataExtractor responding to query for field: '
                      '"{!s}"'.format(field))
            return self._raw_metadata.get(field, False)

    def _get_raw_metadata(self):
        raise NotImplementedError('Must be implemented by inheriting classes.')


class ExiftoolMetadataExtractor(MetadataExtractor):
    """
    Extracts various types of metadata using "exiftool".
    """
    handles_mime_types = ['mp4', 'mov']
    data_query_string = 'metadata.exiftool'

    def __init__(self, source):
        super(ExiftoolMetadataExtractor, self).__init__(source)
        self._raw_metadata = None

    def _get_raw_metadata(self):
        try:
            return self.get_exiftool_data()
        except Exception as e:
            raise ExtractorError(e)

    def get_exiftool_data(self):
        with wrap_exiftool.ExifTool() as et:
            # Raises ValueError if an ExifTool instance isn't running.
            try:
                return et.get_metadata(self.source)
            except (AttributeError, ValueError, TypeError):
                raise


class PyPDFMetadataExtractor(MetadataExtractor):
    handles_mime_types = ['pdf']
    data_query_string = 'metadata.pypdf'

    def __init__(self, source):
        super(PyPDFMetadataExtractor, self).__init__(source)
        self._raw_metadata = None

    def _get_raw_metadata(self):
        try:
            return self.get_pypdf_data()
        except Exception as e:
            raise ExtractorError(e)

    def get_pypdf_data(self):
        out = {}

        try:
            file_reader = PyPDF2.PdfFileReader(self.source, 'rb')
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

            out.update({'encrypted': file_reader.isEncrypted})

            try:
                num_pages = file_reader.getNumPages()
            except PdfReadError:
                # PDF document might be encrypted with restrictions for reading.
                # TODO: Raise custom exception .. ?
                raise
            else:
                out.update({'number_pages': num_pages})

            # https://pythonhosted.org/PyPDF2/XmpInformation.html
            xmp_metadata = file_reader.getXmpMetadata()
            if xmp_metadata:
                xmp = {}
                for k, v in xmp_metadata.items():
                    if v:
                        xmp[k] = v

                out.update(xmp)

        return out
