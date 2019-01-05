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

import logging
import os
import sys
from functools import lru_cache

from core import constants as C
from core.exceptions import FilesystemError
from core.model import MeowURI
from core.providers import ProviderMixin
from extractors import ExtractorError
from util import disk
from util import mimemagic


class BaseMetadataExtractor(ProviderMixin):
    """
    Top-level abstract base class for all metadata extractors.

    All metadata extractors must inherit from the 'BaseExtractor' class in
    order to be picked up by the registration mechanism.

    This class contains unimplemented methods that must be overridden by
    inheriting classes.

    NOTE: Extractors that setup any external processes or other resources that
          should be released at program exit or any errors must have a method
          'shutdown(self)' with appropriate behaviour for handling this.
    """
    # NOTE: Must be overridden by inheriting classes.
    # List of MIME types that this extractor can extract information from.
    # Supports simple "globbing". Examples: ['image/*', 'application/pdf']
    HANDLES_MIME_TYPES = None

    # Resource identifier "MeowURI" for the data returned by this extractor.
    # Middle part of the full MeowURI ('metadata', 'contents', 'filesystem', ..)
    # Optionally overridden by inheriting classes.
    MEOWURI_CHILD = C.MEOWURI_UNDEFINED_PART

    # Last part of the full MeowURI ('exiftool', 'xplat', ..)
    # Optionally overridden by inheriting classes.
    MEOWURI_LEAF = C.MEOWURI_UNDEFINED_PART

    # NOTE: Must be overridden by inheriting classes.
    # Controls whether the extractor is enabled and used by default.
    # Used to exclude slow running extractors from always being executed.
    # If the extractor is not enabled by the default, it must be explicitly
    # specified in order to be enqueued in the extractor run queue.
    IS_SLOW = False

    # Set at first call to 'meowuri_prefix()'.
    _meowuri_prefix = None

    def __init__(self):
        self.log = logging.getLogger(
            '{!s}.{!s}'.format(__name__, self.__module__)
        )

    @classmethod
    def meowuri_prefix(cls):
        if not cls._meowuri_prefix:
            def _undefined(attribute):
                return attribute == C.MEOWURI_UNDEFINED_PART

            _node = cls.MEOWURI_CHILD
            if _undefined(_node):
                _node = cls._meowuri_node_from_module_name()

            _leaf = cls.MEOWURI_LEAF
            if _undefined(_leaf):
                _leaf = cls._meowuri_leaf_from_module_name()

            cls._meowuri_prefix = MeowURI(
                C.MEOWURI_ROOT_SOURCE_EXTRACTORS, _node, _leaf
            )

        return cls._meowuri_prefix

    @classmethod
    def _meowuri_node_from_module_name(cls):
        try:
            _name = cls.__module__.split('.')[-2]

            # De-pluralize; 'extractors' --> 'extractor', etc.
            if _name.endswith('s'):
                return _name[:-1]
            return _name

        # "The base class for the exceptions that are raised when a key or
        # index used on a mapping or sequence is invalid: IndexError, KeyError.
        # This can be raised directly by codecs.lookup()." -- Python 3.6.1 docs
        except LookupError:
            return C.MEOWURI_UNDEFINED_PART

    @classmethod
    def _meowuri_leaf_from_module_name(cls):
        try:
            top_level_module_name = cls.__module__.split('.')[-1]
        except LookupError:
            return C.MEOWURI_UNDEFINED_PART
        else:
            if top_level_module_name.startswith('extractor_'):
                # Remove the leading 'extractor_' part.
                leaf = top_level_module_name[10:]
            else:
                leaf = top_level_module_name

            assert leaf, 'Empty MeowURI leaf: {} {!s}'.format(type(leaf), leaf)
            return leaf

    @classmethod
    def can_handle(cls, fileobject):
        """
        Tests if a specific extractor class can handle a given file object.

        The extractor is considered to be able to handle the file if the file
        MIME-type evaluates true for the globs defined in class attribute
        'HANDLES_MIME_TYPES'.

        Inheriting extractor classes can override this method if they need
        to perform additional tests in order to determine if they can handle
        a given file object.
        If this method is __NOT__ overridden, the inheriting class MUST contain
        a class attribute with MIME-types (globs) as a list of Unicode strings.

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

        assert isinstance(cls.HANDLES_MIME_TYPES, list)
        return cls._evaluate_mime_type_glob(fileobject)

    @classmethod
    def _evaluate_mime_type_glob(cls, fileobject):
        try:
            return mimemagic.eval_glob(fileobject.mime_type,
                                       cls.HANDLES_MIME_TYPES)
        except (TypeError, ValueError) as e:
            raise ExtractorError(
                'Error evaluating "{!s}" MIME handling; {!s}'.format(cls, e)
            )

    @classmethod
    def python_source_filepath(cls):
        return os.path.realpath(sys.modules[cls.__module__].__file__)

    @classmethod
    def fieldmeta_filepath(cls):
        return _fieldmeta_filepath_from_extractor_source_filepath(
            cls.python_source_filepath()
        )

    @classmethod
    @lru_cache()
    def metainfo_from_yaml_file(cls):
        filepath_fieldmeta = cls.fieldmeta_filepath()
        try:
            field_metainfo = disk.load_yaml_file(filepath_fieldmeta)
        except FilesystemError:
            field_metainfo = dict()
        return field_metainfo

    def extract(self, fileobject, **kwargs):
        """
        Extracts and returns data using a specific extractor.

          NOTE: This method __MUST__ be implemented by inheriting classes!

        The return value should be a dictionary keyed by "MeowURI leaves"
        matching the keys in the field meta data, defined in YAML-files.
        The data should be "safe", I.E. validated and coerced to a suitable
        "internal format" --- text should be returned as Unicode strings, etc.
        Use the type coercers in 'coercers.py'.

        Implementing classes should make sure to catch all exceptions and
        re-raise an 'ExtractorError', passing any valuable information along.
        Only raise the 'ExtractorError' exception for irrecoverable errors.
        Otherwise, implementers should strive to return empty values of the
        expected type. None is the universal "no value".

        Args:
            fileobject: Source of data from which to extract information as an
                        instance of 'FileObject'.

        Returns:
            All data produced gathered by the extractor as a dict keyed by
            "MeowURI leaves" (field names) storing arbitrary data.

        Raises:
            ExtractorError: The extraction could not be completed successfully.
        """
        raise NotImplementedError('Must be implemented by inheriting classes.')

    @classmethod
    def metainfo(cls):
        # TODO: [TD0151] Fix inconsistent use of classes vs. class instances.
        if cls not in _FIELD_META_CACHE:
            metainfo = cls.metainfo_from_yaml_file()
            _FIELD_META_CACHE[cls] = metainfo
        return dict(_FIELD_META_CACHE[cls])

    @classmethod
    def dependencies_satisfied(cls):
        """
        Checks if all dependencies required to use the extractor are available.

          NOTE: This method __MUST__ be implemented by inheriting classes!

        This should be used to test that any dependencies required by the
        extractor are available, like third party libraries or executables.

        Returns:
            True if all requirements are satisfied and the extractor is usable,
            otherwise False.
        """
        raise NotImplementedError('Must be implemented by inheriting classes.')

    @classmethod
    def name(cls):
        # TODO: [TD0151] Fix inconsistent use of classes vs. class instances.
        return cls.__name__

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)


def _fieldmeta_filepath_from_extractor_source_filepath(filepath):
    filepath_without_extension, _ = os.path.splitext(filepath)
    return os.path.realpath(os.path.normpath(
        filepath_without_extension + C.EXTRACTOR_FIELDMETA_BASENAME_SUFFIX
    ))


# Cached field meta info read from files, keyed by extractor classes.
_FIELD_META_CACHE = dict()
