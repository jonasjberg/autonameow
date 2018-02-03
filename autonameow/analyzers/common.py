# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg
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

from core import constants as C
from core import providers
from core.exceptions import AutonameowException
from core.model.genericfields import get_field_class
from core.model import (
    force_meowuri,
    MeowURI
)
from util import (
    mimemagic,
    sanity
)


log = logging.getLogger(__name__)


class AnalyzerError(AutonameowException):
    """Irrecoverable error occurred when running a "analyzer" class."""


class BaseAnalyzer(object):
    """
    Top-level abstract base class for all content-specific analyzer classes.

    Includes common functionality and interfaces that must be implemented
    by inheriting analyzer classes.

    The analyzer classes must be re-created for every 'FileObject' that should
    be analyzed.  Compare this to the extractors that are instantiated once and
    take the 'FileObject' as an argument to the 'extract() method'.
    """
    # Optional priority as a float between 0-1. Used when sorting the run queue.
    RUN_QUEUE_PRIORITY = None

    # List of MIME types that this analyzer can handle.
    # Supports simple "globbing". Examples: ['image/*', 'application/pdf']
    HANDLES_MIME_TYPES = None

    # Last part of the full MeowURI ('filetags', 'filename', ..)
    MEOWURI_LEAF = C.UNDEFINED_MEOWURI_PART

    # Set at first call to 'meowuri_prefix()'.
    _meowuri_prefix = None

    # Dictionary with analyzer-specific information, keyed by the fields that
    # the analyzer produces. Stores information on types, etc..
    FIELD_LOOKUP = dict()

    # TODO: Hack ..
    # TODO: [TD0157] Look into analyzers 'FIELD_LOOKUP' attributes.
    coerce_field_value = providers.ProviderMixin.coerce_field_value

    def __init__(self, fileobject, config, request_data_callback):
        self.config = config
        self.fileobject = fileobject
        self.request_data = request_data_callback

        self.log = logging.getLogger(
            '{!s}.{!s}'.format(__name__, self.__module__)
        )

        self.results = dict()

    def run(self):
        """
        Starts an analysis and returns results from a specific analyzer.

        The return value is a dictionary keyed by "MeowURIs", storing (?) data.
        The data should be "safe", I.E. validated and converted to a suitable
        "internal format" --- text should be returned as Unicode strings, etc.

        Returns:
            All data produced gathered by the analyzer as a dict keyed by
            "MeowURIs", storing arbitrary data or lists of arbitrary data.

        Raises:
            AnalyzerError: The extraction could not be completed successfully.
        """
        self.analyze()
        return self.results

    def analyze(self):
        """
        Performs the analysis and stores data in instance attribute 'results'.

          NOTE: This method __MUST__ be implemented by inheriting classes!

        Implementing classes should make sure to catch all exceptions and
        re-raise an "AnalyzerError", passing any valuable information along.

        Only raise the "AnalyzerError" exception for irrecoverable errors.
        Otherwise, implementers should strive to return empty values of the
        expected type. The type coercers in 'types.py' could be useful here.

        Raises:
            AnalyzerError: The extraction could not be completed successfully.
        """
        raise NotImplementedError('Must be implemented by inheriting classes.')

    def _add_results(self, meowuri_leaf, data):
        """
        Stores results in an instance variable dict under a full MeowURI.

        Constructs a full "MeowURI" from the given 'meowuri_leaf' and the
        analyzer-specific MeowURI.

        Args:
            meowuri_leaf: Last part of the "MeowURI"; for example 'author',
                as a Unicode str.
            data: ?
        """
        if not data:
            return

        # TODO: [TD0146] Rework "generic fields". Possibly bundle in "records".
        # Map strings to generic field classes.
        sanity.check_isinstance(data, dict)
        _generic_field_string = data.get('generic_field')
        if _generic_field_string:
            _generic_field_klass = get_field_class(_generic_field_string)
            if _generic_field_klass:
                data['generic_field'] = _generic_field_klass
            else:
                data.pop('generic_field')

        meowuri_prefix = self.meowuri_prefix()
        uri = force_meowuri(meowuri_prefix, meowuri_leaf)
        if not uri:
            self.log.error(
                'Unable to construct full MeowURI from prefix "{!s}" '
                'and leaf "{!s}"'.format(meowuri_prefix, meowuri_leaf)
            )
            return

        _existing_data = self.results.get(uri)
        if _existing_data:
            if not isinstance(_existing_data, list):
                _existing_data = [_existing_data]
            self.results[uri] = _existing_data + [data]
        else:
            self.results[uri] = data

    def request_any_textual_content(self):
        _response = self.request_data(self.fileobject,
                                      'generic.contents.text')
        if not _response:
            return None

        text = None
        if isinstance(_response, list):
            for _r in _response:
                sanity.check_isinstance(_r, str)
                if _r:
                    text = _r
                    break
        else:
            sanity.check_isinstance(_response, str)
            if _response:
                text = _response

        if text is None:
            self.log.info('Requested data unavailable: "generic.contents.text"')
        return text

    def metainfo(self):
        # TODO: [TD0151] Fix inconsistent use of classes vs. class instances.
        return self.FIELD_LOOKUP

    @classmethod
    def meowuri_prefix(cls):
        """
        Returns: Analyzer-specific "MeowURI" root/prefix as a Unicode string.
        """
        if not cls._meowuri_prefix:
            _leaf = cls.__module__.split('_')[-1] or cls.MEOWURI_LEAF
            cls._meowuri_prefix = MeowURI(
                C.MEOWURI_ROOT_SOURCE_ANALYZERS, _leaf
            )
        return cls._meowuri_prefix

    @classmethod
    def can_handle(cls, fileobject):
        """
        Tests if this analyzer class can handle the given file.

        The analyzer is considered to be able to handle the given file if the
        file MIME type is listed in the class attribute 'HANDLES_MIME_TYPES'.

        Inheriting analyzer classes can override this method if they need
        to perform additional tests in order to determine if they can handle
        the given file object.
        If this method is __NOT__ overridden, the inheriting class must contain
        a class attribute with MIME-types (globs) as a list of Unicode strings.

        Args:
            fileobject: The file to test as an instance of 'FileObject'.

        Returns:
            True if the analyzer class can handle the given file, else False.
        """
        if cls.HANDLES_MIME_TYPES is None:
            raise NotImplementedError(
                'Classes without class attribute "HANDLES_MIME_TYPES" must '
                'implement (override) class method "can_handle"!'
            )
        sanity.check_isinstance(cls.HANDLES_MIME_TYPES, list)

        try:
            return mimemagic.eval_glob(fileobject.mime_type,
                                       cls.HANDLES_MIME_TYPES)
        except (TypeError, ValueError) as e:
            raise AnalyzerError(
                'Error evaluating "{!s}" MIME handling; {!s}'.format(cls, e)
            )

    @classmethod
    def check_dependencies(cls):
        """
        Tests if the analyzer can be used.

        This should be used to test that any dependencies required by the
        analyzer are met. This might be third party libraries or executables.

        Returns:
            True if the analyzer has everything it needs, else False.
        """
        raise NotImplementedError('Must be implemented by inheriting classes.')

    def __str__(self):
        return self.__class__.__name__
