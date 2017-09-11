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

try:
    import PyPDF2
    from PyPDF2.generic import (
        IndirectObject,
        TextStringObject
    )
    from PyPDF2.utils import (
        PyPdfError,
        PdfReadError
    )
except ImportError:
    PyPDF2 = None

from core import (
    fields,
    types,
    util
)
from extractors import (
    ExtractorError,
    ExtractedData,
)
from extractors.metadata.common import AbstractMetadataExtractor


class PyPDFMetadataExtractor(AbstractMetadataExtractor):
    handles_mime_types = ['application/pdf']
    meowuri_root = 'metadata.pypdf'

    tagname_type_lookup = {
        'Creator': ExtractedData(
            wrapper=types.AW_STRING,
            mapped_fields=[
                fields.WeightedMapping(fields.datetime, probability=1),
                fields.WeightedMapping(fields.date, probability=1)
            ]
        ),
        'CreationDate': ExtractedData(types.AW_PYPDFTIMEDATE),
        'Encrypted': ExtractedData(types.AW_BOOLEAN),
        'ModDate': ExtractedData(types.AW_PYPDFTIMEDATE),
        'NumberPages': ExtractedData(types.AW_INTEGER),
        'Paginated': ExtractedData(types.AW_BOOLEAN),
        'Producer': ExtractedData(types.AW_STRING),
        'Title': ExtractedData(types.AW_STRING),
    }

    def __init__(self):
        super(PyPDFMetadataExtractor, self).__init__()

    def _get_raw_metadata(self, source):
        try:
            return self._get_pypdf_data(source)
        except Exception as e:
            raise ExtractorError(e)

    def _get_pypdf_data(self, source):
        out = {}

        try:
            # NOTE(jonas): [encoding] Double-check PyPDF2 docs ..
            file_reader = PyPDF2.PdfFileReader(util.decode_(source), 'rb')
        except (OSError, PyPdfError) as e:
            raise ExtractorError(e)

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
                   if not isinstance(v, IndirectObject)}

            # Convert PyPDF values of type 'PyPDF2.generic.TextStringObject'
            out = {k: str(v) for k, v in out.items()}

            self._wrap_pypdf_data(out, 'author',
                                  doc_info.author, types.AW_STRING)
            self._wrap_pypdf_data(out, 'creator',
                                  doc_info.creator, types.AW_STRING)
            self._wrap_pypdf_data(out, 'producer',
                                  doc_info.producer, types.AW_STRING)
            self._wrap_pypdf_data(out, 'subject',
                                  doc_info.subject, types.AW_STRING)
            self._wrap_pypdf_data(out, 'title',
                                  doc_info.title, types.AW_STRING)
            self._wrap_pypdf_data(out, 'author_raw',
                                  doc_info.author_raw, types.AW_STRING)
            self._wrap_pypdf_data(out, 'creator_raw',
                                  doc_info.creator_raw, types.AW_STRING)
            self._wrap_pypdf_data(out, 'producer_raw',
                                  doc_info.producer_raw, types.AW_STRING)
            self._wrap_pypdf_data(out, 'subject_raw',
                                  doc_info.subject_raw, types.AW_STRING)
            self._wrap_pypdf_data(out, 'title_raw',
                                  doc_info.title_raw, types.AW_STRING)

        out.update({'Encrypted': file_reader.isEncrypted})

        try:
            num_pages = file_reader.getNumPages()
        except PdfReadError as e:
            # NOTE: This now wholly determines whether a pdf is readable.
            # Can getNumPages fail although the text is actually readable?
            self.log.warning(
                'PDF document might be encrypted and/or has restrictions'
                ' that prevent reading'
            )
            raise ExtractorError('PyPDF2.PdfReadError: "{!s}"'.format(e))
        else:
            out.update({'NumberPages': types.AW_INTEGER(num_pages)})
            out.update({'Paginated': True})

        # https://pythonhosted.org/PyPDF2/XmpInformation.html
        xmp_metadata = file_reader.getXmpMetadata()
        if xmp_metadata:
            self._wrap_pypdf_data(out, 'xmp_createDate',
                                  xmp_metadata.xmp_createDate,
                                  types.AW_TIMEDATE)
            self._wrap_pypdf_data(out, 'xmp_creatorTool',
                                  xmp_metadata.xmp_creatorTool,
                                  types.AW_STRING)
            self._wrap_pypdf_data(out, 'xmp_metadataDate',
                                  xmp_metadata.xmp_metadataDate,
                                  types.AW_TIMEDATE)
            self._wrap_pypdf_data(out, 'xmp_modifyDate',
                                  xmp_metadata.xmp_modifyDate,
                                  types.AW_TIMEDATE)
            self._wrap_pypdf_data(out, 'pdf_keywords',
                                  xmp_metadata.pdf_keywords,
                                  types.AW_STRING)
            self._wrap_pypdf_data(out, 'pdf_producer',
                                  xmp_metadata.pdf_producer,
                                  types.AW_STRING)
            self._wrap_pypdf_data(out, 'pdf_title',
                                  xmp_metadata.pdf_producer,
                                  types.AW_STRING)

        return out

    def _wrap_pypdf_data(self, out_dict, out_key, pypdf_data, wrapper):
        if pypdf_data is None:
            return
        if isinstance(pypdf_data, IndirectObject):
            return
        if isinstance(pypdf_data, TextStringObject):
            out_dict[out_key] = str(pypdf_data)
            return

        # TODO: [TD0087] Clean up messy (and duplicated) wrapping of "raw" data.
        try:
            wrapped = wrapper(pypdf_data)
        except types.AWTypeError:
            self.log.warning(
                'Wrapping PyPDF data raised AWTypeError for "{!s}" ({})'.format(
                    pypdf_data, type(pypdf_data))
            )
            return
        else:
            self.log.debug(
                'Wrapped PyPDF data "{!s}" ({}) into "{!s}" ({})'.format(
                    pypdf_data, type(pypdf_data), wrapped, type(wrapped))
            )
            out_dict[out_key] = wrapped

    @classmethod
    def check_dependencies(cls):
        return PyPDF2 is not None


