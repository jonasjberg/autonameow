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
    PdfReadError
)

from core import (
    util,
    types
)
from core.exceptions import ExtractorError
from extractors import BaseExtractor


class AbstractMetadataExtractor(BaseExtractor):
    handles_mime_types = None
    data_query_string = None

    # Lookup table that maps extractor-specific field names to wrapper classes.
    tagname_type_lookup = {}

    def __init__(self, source):
        super(AbstractMetadataExtractor, self).__init__(source)

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
                self._perform_initial_extraction()
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

    def _perform_initial_extraction(self):
        self._raw_metadata = self._get_raw_metadata()

    def _to_internal_format(self, raw_metadata):
        out = {}
        for tag_name, value in raw_metadata.items():
            out[tag_name] = self._wrap_raw(tag_name, value)
        return out

    def _wrap_raw(self, tag_name, value):
        if tag_name in self.tagname_type_lookup:
            # First check the lookup table.
            return self.tagname_type_lookup[tag_name](value)
        else:
            # Fall back automatic type detection if not found in lookup table.
            wrapped = types.try_wrap(value)
            if wrapped is not None:
                return wrapped
            else:
                log.critical('Unhandled wrapping of tag name "{}" '
                             '(value: "{}")'.format(tag_name, value))
                return value

    def _get_raw_metadata(self):
        raise NotImplementedError('Must be implemented by inheriting classes.')


class PyPDFMetadataExtractor(AbstractMetadataExtractor):
    handles_mime_types = ['application/pdf']
    data_query_string = 'metadata.pypdf'

    tagname_type_lookup = {
        'Creator': types.AW_STRING,
        'CreationDate': types.AW_PYPDFTIMEDATE,
        'Encrypted': types.AW_BOOLEAN,
        'ModDate': types.AW_PYPDFTIMEDATE,
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

        return out
