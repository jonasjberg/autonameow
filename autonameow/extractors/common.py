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

from core import util
from core.exceptions import AutonameowException
from core.fileobject import FileObject
from core.util import sanity
from core import constants as C


class ExtractorError(AutonameowException):
    """An error generated by any "Extractor" subclasses during extraction."""


class BaseExtractor(object):
    """
    Top-level abstract base class for all filetype-specific extractor classes.

    Includes common functionality and interfaces that must be implemented
    by inheriting extractor classes.

    All "extractors" must inherit from the 'BaseExtractor' class. This class
    is abstract and serves to define interfaces that actual extractor classes
    must implement --- it is never used directly.

    Currently, there is also an additional layer of abstraction/inheritance/
    (indirection..) between the 'BaseExtractor' and the *actual *REAL**
    extractor classes that are used at runtime.

    Current inheritance hierarchy:

        (abstract)  @ BaseExtractor
                    |
        (abstract)  +--* AbstractTextExtractor
                    |  |
                    |  +--* TesseractOCRTextExtractor
                    |  '--* PdfTextExtractor
                    |
                    +--* ExiftoolMetadataExtractor
                    '--* PyPDFMetadataExtractor

    The abstract extractors defines additional interfaces, extending the base.
    It is pretty messy and should be redesigned and simplified at some point ..
    """

    # List of MIME types that this extractor can extract information from.
    # Supports simple "globbing". Examples: ['image/*', 'application/pdf']
    HANDLES_MIME_TYPES = None

    # Resource identifier "MeowURI" for the data returned by this extractor.
    # Middle part of the full MeowURI ('metadata', 'contents', 'filesystem', ..)
    MEOWURI_NODE = C.UNDEFINED_MEOWURI_PART

    # Last part of the full MeowURI ('exiftool', 'pypdf', 'xplat', ..)
    MEOWURI_LEAF = C.UNDEFINED_MEOWURI_PART

    # Controls whether the extractor is enabled and used by default.
    # Used to exclude slow running extractors from always being executed.
    # If the extractor is not enabled by the default, it must be explicitly
    # specified in order to be enqueued in the extractor run queue.
    is_slow = False

    def __init__(self):
        self.log = logging.getLogger(
            '{!s}.{!s}'.format(__name__, self.__module__)
        )

    def __call__(self, fileobject, **kwargs):
        """
        Extracts and returns data using a specific extractor.

          NOTE: This method __MUST__ be implemented by inheriting classes!

        The return value should be a dictionary keyed by "MeowURIs", storing
        data. The stored data can be either single elements or lists.
        The data should be "safe", I.E. validated and converted to a suitable
        "internal format" --- text should be returned as Unicode strings.

        Implementing classes should make sure to catch all exceptions and
        re-raise an "ExtractorError", passing any valuable information along.

        Only raise the "ExtractorError" exception for irrecoverable errors.
        Otherwise, implementers should strive to return empty values of the
        expected type. The type coercers in 'types.py' could be useful here.

        Args:
            fileobject: Source of data from which to extract information as an
                        instance of 'FileObject'.

        Returns:
            All data gathered by the extractor, as a dictionary.

        Raises:
            ExtractorError: The extraction could not be completed successfully.
        """
        sanity.check_isinstance(fileobject, FileObject)

        extracted_data = self.execute(fileobject, **kwargs)
        return extracted_data

    @classmethod
    def meowuri(cls):
        def _undefined(attribute):
            return attribute == C.UNDEFINED_MEOWURI_PART

        _node = cls.MEOWURI_NODE
        if _undefined(_node):
            _node = cls._meowuri_node_from_module_name()

        _leaf = cls.MEOWURI_LEAF
        if _undefined(_leaf):
            _leaf = cls._meowuri_leaf_from_module_name()

        return '{root}{sep}{node}{sep}{leaf}'.format(
            root=C.MEOWURI_ROOT_SOURCE_EXTRACTORS, sep=C.MEOWURI_SEPARATOR,
            node=_node, leaf=_leaf
        )

    @classmethod
    def _meowuri_node_from_module_name(cls):
        try:
            _name = cls.__module__.split('.')[-2]

            # De-pluralize; 'extractors' --> 'extractor', etc.
            if _name.endswith('s'):
                return _name[:-1]
            else:
                return _name

        except LookupError:
            return C.UNDEFINED_MEOWURI_PART

    @classmethod
    def _meowuri_leaf_from_module_name(cls):
        try:
            return cls.__module__.split('.')[-1]
        except LookupError:
            return C.UNDEFINED_MEOWURI_PART

    @classmethod
    def can_handle(cls, fileobject):
        """
        Tests if a specific extractor class can handle a given file object.

        The extractor is considered to be able to handle the file if the
        file MIME-type is listed in the class attribute 'HANDLES_MIME_TYPES'.

        Inheriting extractor classes can override this method if they need
        to perform additional tests in order to determine if they can handle
        a given file object.

        Args:
            fileobject: The file to test as an instance of 'FileObject'.

        Returns:
            True if the extractor class can extract data from the given file,
            else False.
        """
        if cls.HANDLES_MIME_TYPES is None:
            raise NotImplementedError(
                'Classes without class attribute "HANDLES_MIME_TYPES" must '
                'implement (override) class method "can_handle"!'
            )

        try:
            return util.eval_magic_glob(fileobject.mime_type,
                                        cls.HANDLES_MIME_TYPES)
        except (TypeError, ValueError) as e:
            raise ExtractorError(
                'Error evaluating "{!s}" MIME handling; {!s}'.format(cls, e)
            )

    def execute(self, fileobject, **kwargs):
        """
        Extracts and returns data using a specific extractor.

          NOTE: This method __MUST__ be implemented by inheriting classes!

        The return value should be a dictionary keyed by "MeowURIs", storing
        data. The stored data can be either single elements or lists.
        The data should be "safe", I.E. validated and converted to a suitable
        "internal format" --- text should be returned as Unicode strings.

        Implementing classes should make sure to catch all exceptions and
        re-raise an "ExtractorError", passing any valuable information along.

        Only raise the "ExtractorError" exception for irrecoverable errors.
        Otherwise, implementers should strive to return empty values of the
        expected type. The type coercers in 'types.py' could be useful here.

        Args:
            fileobject: Source of data from which to extract information as an
                        instance of 'FileObject'.

        Returns:
            All data produced gathered by the extractor as a dict keyed by
            "MeowURIs", storing arbitrary data or lists of arbitrary data.

        Raises:
            ExtractorError: The extraction could not be completed successfully.
        """
        raise NotImplementedError('Must be implemented by inheriting classes.')

    @classmethod
    def check_dependencies(cls):
        """
        Tests if the extractor can be used.

          NOTE: This method __MUST__ be implemented by inheriting classes!

        This should be used to test that any dependencies required by the
        extractor are met, like third party libraries or executables.

        Returns:
            True if any and all dependencies are satisfied and the extractor
            is usable, else False.
        """
        raise NotImplementedError('Must be implemented by inheriting classes.')

    @classmethod
    def __str__(cls):
        return cls.__name__

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)
