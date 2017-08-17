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
from PyPDF2.utils import PdfReadError

from core import (
    types,
    util,
    exceptions
)
from extractors.metadata import AbstractMetadataExtractor


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
        'Title': types.AW_STRING,
    }

    def __init__(self, source):
        super(PyPDFMetadataExtractor, self).__init__(source)
        self._raw_metadata = None

    def _get_raw_metadata(self):
        try:
            return self._get_pypdf_data()
        except Exception as e:
            raise exceptions.ExtractorError(e)

    def _get_pypdf_data(self):
        out = {}

        try:
            # NOTE(jonas): [encoding] Double-check PyPDF2 docs ..
            file_reader = PyPDF2.PdfFileReader(util.decode_(self.source), 'rb')
        except OSError:
            raise exceptions.ExtractorError('Unable to read file with PyPDF2')
        else:

            # Notes on 'getDocumentInfo' from the PyPDF2 source documentation:
            #
            # All text properties of the document metadata have *two*
            # properties, eg. author and author_raw. The non-raw property will
            # always return a ``TextStringObject``, making it ideal for a case
            # where the metadata is being displayed. The raw property can
            # sometimes return a ``ByteStringObject``, if PyPDF2 was unable to
            # decode the string's text encoding; this requires additional
            # safety in the caller and therefore is not as commonly accessed.
            doc_info = file_reader.getDocumentInfo()
            if doc_info:
                # Remove any leading '/' from all dict keys.
                # Skip entries starting with "IndirectObject(" ..
                # TODO: Cleanup this filtering.
                out = {k.lstrip('\/'): v for k, v in doc_info.items()
                       if not is_indirectobject(v)}

                # Convert PyPDF values of type 'PyPDF2.generic.TextStringObject'
                out = {k: str(v) for k, v in out.items()}

                _wrap_pypdf_string(out, 'author', doc_info.author)
                _wrap_pypdf_string(out, 'creator', doc_info.creator)
                _wrap_pypdf_string(out, 'producer', doc_info.producer)
                _wrap_pypdf_string(out, 'subject', doc_info.subject)
                _wrap_pypdf_string(out, 'title', doc_info.title)
                _wrap_pypdf_string(out, 'author_raw', doc_info.author_raw)
                _wrap_pypdf_string(out, 'creator_raw', doc_info.creator_raw)
                _wrap_pypdf_string(out, 'producer_raw', doc_info.producer_raw)
                _wrap_pypdf_string(out, 'subject_raw', doc_info.subject_raw)
                _wrap_pypdf_string(out, 'title_raw', doc_info.title_raw)

            out.update({'Encrypted': file_reader.isEncrypted})

            try:
                num_pages = file_reader.getNumPages()
            except PdfReadError:
                # PDF document might be encrypted with restrictions for reading.
                # TODO: Raise custom exception .. ?
                pass
            else:
                out.update({'NumberPages': num_pages})
                out.update({'Paginated': True})

            # https://pythonhosted.org/PyPDF2/XmpInformation.html
            xmp_metadata = file_reader.getXmpMetadata()
            if xmp_metadata:
                xmp = {}
                for k, v in xmp_metadata.items():
                    if v:
                        xmp[k] = types.try_wrap(v)

                out.update(xmp)

        return out


def is_indirectobject(pypdf_data):
    # TODO: Fix any performance/untidyness issues.
    from PyPDF2.generic import IndirectObject
    return isinstance(pypdf_data, IndirectObject)


def is_textstringobject(pypdf_data):
    # TODO: Fix any performance/untidyness issues.
    from PyPDF2.generic import TextStringObject
    return isinstance(pypdf_data, TextStringObject)


def _wrap_pypdf_string(out_dict, out_key, pypdf_data):
    if pypdf_data is None:
        return
    if is_indirectobject(pypdf_data):
        return
    if is_textstringobject(pypdf_data):
        pypdf_data = str(pypdf_data)

    try:
        wrapped = types.AW_STRING(pypdf_data)
    except exceptions.AWTypeError:
        log.warning(
            '_wrap_pypdf_string raised a AWTypeError for "{!s}" ({})'.format(
                pypdf_data, type(pypdf_data))
        )
        return
    else:
        log.debug(
            '_wrap_pypdf_string wrapped "{!s}" ({}) into "{!s}" ({})'.format(
                pypdf_data, type(pypdf_data), wrapped, type(wrapped))
        )
        out_dict[out_key] = wrapped
