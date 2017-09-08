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

import logging

from core import (
    util,
    types
)
from core.exceptions import AutonameowException
from core.fileobject import FileObject


log = logging.getLogger(__name__)


class ExtractorError(AutonameowException):
    """An error generated by any "Extractor" subclasses during extraction."""


class BaseExtractor(object):
    """
    Top-level abstract base class for all filetype-specific extractor classes.

    Includes common functionality and interfaces that must be implemented
    by inheriting extractor classes.

    All "extractors" must inherit from the 'BaseExtractor' class. This class
    is never used directly -- it is an abstract class that defines interfaces
    that must be implemented by inheriting classes.

    Currently, there is also an additional layer of abstraction/inheritance/
    (indirection..) between the 'BaseExtractor' and the *actual *REAL**
    extractor classes that are used at runtime.

    Current inheritance hierarchy:

        (abstract)  @ BaseExtractor
                    |
        (abstract)  +--* AbstractTextExtractor
                    |  |
                    |  +--* ImageOCRTextExtractor
                    |  '--* PdfTextExtractor
                    |
        (abstract)  '--* AbstractMetadataExtractor
                       |
                       +--* ExiftoolMetadataExtractor
                       '--* PyPDFMetadataExtractor

    The abstract extractors defines additional interfaces, extending the base.
    It is pretty messy and should be redesigned and simplified at some point ..
    """

    # List of MIME types that this extractor can extract information from.
    # Supports simple "globbing". Examples: ['image/*', 'application/pdf']
    handles_mime_types = None

    # Resource identifier "MeowURI" for the data returned by this extractor.
    # Example:  'metadata.exiftool'
    meowuri_root = None

    # Controls whether the extractor is enabled and used by default.
    # Used to exclude slow running extractors from always being executed.
    # If the extractor is not enabled by the default, it must be explicitly
    # specified in order to be enqueued in the extractor run queue.
    is_slow = False

    def __init__(self, source):
        """
        Creates a extractor instance acting on the specified source data.

        Args:
            source: Source of data from which to extract information as a
                byte string path (internal path format)
        """
        # Make sure the 'source' paths are in the "internal bytestring" format.
        # The is-None-check below is for unit tests that pass a None 'source'.
        if source is not None and not isinstance(source, FileObject):
            assert(isinstance(source, bytes))
        self.source = source

        self.log = logging.getLogger(
            '{!s}.{!s}'.format(__name__, self.__module__)
        )

    def execute(self, **kwargs):
        """
        Starts extracting data using the extractor.

        Keyword argument "field" is optional. All data is returned by default.
        If the data is text, is should be returned as Unicode strings.

        Implementing classes should make sure to catch all exceptions and
        re-raise an "ExtractorError", passing any valuable information along.
        Only raise the "ExtractorError" exception for any irrecoverable errors.
        Otherwise, implementers should strive to return empty values of the
        same type as that of the expected, valid data.

        Keyword Args:
            field: Return only data matching this field.
                Field format and type is defined by the extractor class.

        Returns:
            All data gathered by the extractor if no field is specified.
            Else the data matching the specified field.

        Raises:
            ExtractorError: The extraction could not be completed successfully.
        """
        raise NotImplementedError('Must be implemented by inheriting classes.')

    @classmethod
    def can_handle(cls, file_object):
        """
        Tests if this extractor class can handle the given file.

        The extractor is considered to be able to handle the given file if the
        file MIME type is listed in the class attribute 'handles_mime_types'.

        Inheriting extractor classes can override this method if they need
        to perform additional tests in order to determine if they can handle
        the given file object.

        Args:
            file_object: The file to test as an instance of 'FileObject'.

        Returns:
            True if the extractor class can extract data from the given file,
            else False.
        """
        if cls.handles_mime_types is None:
            raise NotImplementedError('Must be defined by inheriting classes.')

        try:
            return util.eval_magic_glob(file_object.mime_type,
                                        cls.handles_mime_types)
        except (TypeError, ValueError) as e:
            log.error('Error evaluating "{!s}" MIME handling; {!s}'.format(cls,
                                                                           e))
            return False

    @classmethod
    def check_dependencies(cls):
        """
        Tests if the extractor can be used.

        This should be used to test that any dependencies required by the
        extractor are met. This might be third party libraries or executables.

        Returns:
            True if the extractor has everything it needs, else False.
        """
        raise NotImplementedError('Must be implemented by inheriting classes.')

    @classmethod
    def __str__(cls):
        return cls.__name__

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)


class ExtractedData(object):
    """
    Instances of this class wrap some extracted data with extra information.

    Extractors can specify which (if any) name template fields that the item
    is compatible with. For instance, date/time-information is could be used
    to populate the 'datetime' name template field.
    """
    def __init__(self, wrapper, mapped_fields=None):
        self.wrapper = wrapper

        if mapped_fields is not None:
            self.field_map = mapped_fields
        else:
            self.field_map = []

        self._data = None

    def __call__(self, raw_value):
        if self.wrapper:
            try:
                self._data = self.wrapper(raw_value)
            except types.AWTypeError as e:
                log.warning(e)
                raise
        else:
            # Fall back automatic type detection if 'wrapper' is unspecified.
            from core.config.configuration import Configuration
            wrapped = types.try_wrap(Configuration)
            if wrapped is None:
                # log.critical(
                #     'Unhandled wrapping of tag name "{}" (type: {!s} '
                #     ' value: "{!s}")'.format(tag_name, type(value), value)
                # )
                self._data = raw_value
            else:
                self._data = wrapped

        return self

    @property
    def value(self):
        return self._data

    def maps_field(self, field):
        for mapping in self.field_map:
            if field == mapping.field:
                return True
        return False

    def __str__(self):
        return '{!s}("{!s}")  FieldMap: {!s}"'.format(
            self.wrapper, self.value, self.field_map
        )

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if (self.wrapper == other.wrapper
                and self.field_map == other.field_map
                and self.value == other.value):
            return True
        return False
