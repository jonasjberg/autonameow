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

from core.util import wrap_exiftool
from extractors.extractor import Extractor


class MetadataExtractor(Extractor):
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
                self._raw_metadata = self._get_raw_metadata()
            except Exception as e:
                log.error('Metadata query FAILED: {!s}'.format(e))
                return False

        if not field:
            return self._raw_metadata
        else:
            return self._raw_metadata.get(field, False)

    def _get_raw_metadata(self):
        raise NotImplementedError


class ExiftoolMetadataExtractor(MetadataExtractor):
    """
    Extracts various types of metadata using "exiftool".
    """
    def __init__(self, source):
        super(ExiftoolMetadataExtractor, self).__init__(source)

        self._raw_metadata = None

    def _get_raw_metadata(self):
        return self.get_exiftool_data()

    def get_exiftool_data(self):
        with wrap_exiftool.ExifTool() as et:
            # Raises ValueError if an ExifTool instance isn't running.
            try:
                return et.get_metadata(self.source)
            except (ValueError, TypeError):
                raise


# get_exiftool_data("test_files/gmail.pdf"):
# ==========================================
# 'ExifTool:ExifToolVersion' (4367912672) = {float} 10.5
# 'File:Directory' (4367948080) = {str} '/Users/jonas/Dropbox/LNU/1DV430_IndividuelltProjekt/src/js224eh-project.git/test_files'
# 'File:FileAccessDate' (4367955048) = {str} '2017:06:03 22:27:50+02:00'
# 'File:FileInodeChangeDate' (4367966256) = {str} '2017:05:30 10:31:26+02:00'
# 'File:FileModifyDate' (4367954976) = {str} '2016:01:11 13:41:41+01:00'
# 'File:FileName' (4367947376) = {str} 'gmail.pdf'
# 'File:FilePermissions' (4367955120) = {int} 664
# 'File:FileSize' (4367948272) = {int} 141636
# 'File:FileType' (4367948208) = {str} 'PDF'
# 'File:FileTypeExtension' (4367955192) = {str} 'PDF'
# 'File:MIMEType' (4367948336) = {str} 'application/pdf'
# 'PDF:CreateDate' (4367948912) = {str} '2016:01:11 12:41:32+00:00'
# 'PDF:Creator' (4367948656) = {str} 'Chromium'
# 'PDF:Linearized' (4367948528) = {bool} False
# 'PDF:ModifyDate' (4367948976) = {str} '2016:01:11 12:41:32+00:00'
# 'PDF:PDFVersion' (4367948464) = {float} 1.4
# 'PDF:PageCount' (4367948592) = {int} 2
# 'PDF:Producer' (4367948784) = {str} 'Skia/PDF'
# 'SourceFile' (4367948144) = {str} '/Users/jonas/Dropbox/LNU/1DV430_IndividuelltProjekt/src/js224eh-project.git/test_files/gmail.pdf'

# get_exiftool_data("test_files/course.pdf"):
# ===========================================
# 'ExifTool:ExifToolVersion' (4396400352) = {float} 10.5
# 'File:Directory' (4396451696) = {str} '/Users/jonas/Dropbox/LNU/1DV430_IndividuelltProjekt/src/js224eh-project.git/test_files'
# 'File:FileAccessDate' (4396458968) = {str} '2017:06:03 23:14:29+02:00'
# 'File:FileInodeChangeDate' (4396466224) = {str} '2017:05:30 10:31:26+02:00'
# 'File:FileModifyDate' (4396458896) = {str} '2015:05:18 16:58:25+02:00'
# 'File:FileName' (4396451120) = {str} 'course.pdf'
# 'File:FilePermissions' (4396459040) = {int} 640
# 'File:FileSize' (4396452144) = {int} 10283
# 'File:FileType' (4396452080) = {str} 'PDF'
# 'File:FileTypeExtension' (4396459112) = {str} 'PDF'
# 'File:MIMEType' (4396452208) = {str} 'application/pdf'
# 'PDF:CreateDate' (4396452720) = {str} '2015:05:18 16:43:08+02:00'
# 'PDF:Creator' (4396452528) = {str} 'JasperReports (CourseReport)'
# 'PDF:Linearized' (4396452400) = {bool} False
# 'PDF:ModifyDate' (4396452656) = {str} '2015:05:18 16:43:08+02:00'
# 'PDF:PDFVersion' (4396452336) = {float} 1.4
# 'PDF:PageCount' (4396452464) = {int} 2
# 'PDF:Producer' (4396452592) = {str} 'iText 4.2.0 by 1T3XT'
# 'SourceFile' (4396452016) = {str} '/Users/jonas/Dropbox/LNU/1DV430_IndividuelltProjekt/src/js224eh-project.git/test_files/course.pdf'


class PyPDFMetadataExtractor(Extractor):
    def __init__(self, source):
        super(PyPDFMetadataExtractor, self).__init__(source)

        self.__raw_metadata = None

    def query(self, field=None):
        if not self.__raw_metadata:
            try:
                self.__raw_metadata = self.get_pypdf_data()
            except Exception as e:
                log.error('PyPDF invocation FAILED: {!s}'.format(e))
                return False

        if not field:
            return self.__raw_metadata
        else:
            return self.__raw_metadata.get(field, False)

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
