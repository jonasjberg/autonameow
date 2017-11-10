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

from core import constants as C
from core import (
    exceptions,
    providers,
    util
)
from core.exceptions import AutonameowException
from core.model import ExtractedData


class AnalyzerError(AutonameowException):
    """Irrecoverable error occurred when running a "analyzer" class."""


class BaseAnalyzer(object):
    """
    Top-level abstract base class for all content-specific analyzer classes.

    Includes common functionality and interfaces that must be implemented
    by inheriting analyzer classes.
    """
    RUN_QUEUE_PRIORITY = None

    # List of MIME types that this analyzer can handle.
    # Supports simple "globbing". Examples: ['image/*', 'application/pdf']
    HANDLES_MIME_TYPES = None

    # Last part of the full MeowURI ('filetags', 'filename', ..)
    MEOWURI_LEAF = C.UNDEFINED_MEOWURI_PART

    # Dictionary with analyzer-specific information, keyed by the fields that
    # the analyzer produces. Stores information on types, etc..
    FIELD_LOOKUP = {}

    # TODO: Hack ..
    coerce_field_value = providers.ProviderMixin.coerce_field_value

    def __init__(self, fileobject, config,
                 add_results_callback, request_data_callback):
        self.config = config
        self.fileobject = fileobject
        self.add_results = add_results_callback
        self.request_data = request_data_callback

        self.log = logging.getLogger(
            '{!s}.{!s}'.format(__name__, self.__module__)
        )

    def run(self):
        """
        Starts the analysis performed by this analyzer.
        """
        raise NotImplementedError('Must be implemented by inheriting classes.')

    def get(self, field):
        """
        Wrapper method allows calling 'a.get_FIELD()' as 'a.get("FIELD")'.

        This method simply calls other methods by assembling the method name
        to call from the prefix 'get_' and the given "field" as the postfix.

        Args:
            field: Name of the field to get.  Must be included in
                ANALYSIS_RESULTS_FIELDS, else an exception is raised.

        Returns:
            Equivalent to calling 'a.get_FIELD()'

        Raises:
            AnalysisResultsFieldError: Error caused by invalid argument "field",
                which must be included in ANALYSIS_RESULTS_FIELDS.
        """
        if field not in C.ANALYSIS_RESULTS_FIELDS:
            raise exceptions.AnalysisResultsFieldError(field)

        _func_name = 'get_{}'.format(field)
        get_func = getattr(self, _func_name, False)
        if get_func and callable(get_func):
            return get_func()
        else:
            raise NotImplementedError(field)

    def _add_results(self, meowuri_leaf, data):
        """
        Used by analyzer classes to store results data in the repository.

        Constructs a full "MeowURI" from the given 'meowuri_leaf' and the
        analyzer-specific MeowURI.

        Args:
            meowuri_leaf: Last part of the "MeowURI"; for example 'author',
                as a Unicode str.
            data: A list of dicts, each containing some data, source and weight.
        """
        # TODO: [TD0122] Move away from using callbacks to store results.
        if data is None:
            return

        _meowuri = '{}.{}'.format(self.meowuri_prefix(), meowuri_leaf)
        self.log.debug(
            '{!s} passing "{}" to "add_results" callback'.format(self, _meowuri)
        )
        self.add_results(self.fileobject, _meowuri, data)

    def request_any_textual_content(self):
        _response = self.request_data(self.fileobject,
                                      'generic.contents.text')
        if _response is None:
            return None

        text = None
        if isinstance(_response, list):
            for _r in _response:
                assert isinstance(_r, ExtractedData)
                if _r.value and len(_r.value) > 0:
                    text = _r.value
                    break
        else:
            assert isinstance(_response, ExtractedData)
            if _response.value and len(_response.value) > 0:
                text = _response.value

        if text is not None:
            return text
        else:
            self.log.info(
                'Required data unavailable ("generic.contents.text")'
            )

    def metainfo(self, *args, **kwargs):
        return self.FIELD_LOOKUP

    @classmethod
    def meowuri_prefix(cls):
        """
        Returns: Analyzer-specific "MeowURI" root/prefix as a Unicode string.
        """
        _leaf = cls.__module__.split('_')[-1] or cls.MEOWURI_LEAF

        return '{root}{sep}{leaf}'.format(
            root=C.MEOWURI_ROOT_SOURCE_ANALYZERS, sep=C.MEOWURI_SEPARATOR,
            leaf=_leaf
        )

    @classmethod
    def can_handle(cls, fileobject):
        """
        Tests if this analyzer class can handle the given file.

        The analyzer is considered to be able to handle the given file if the
        file MIME type is listed in the class attribute 'HANDLES_MIME_TYPES'.

        Inheriting analyzer classes can override this method if they need
        to perform additional tests in order to determine if they can handle
        the given file object.

        Args:
            fileobject: The file to test as an instance of 'FileObject'.

        Returns:
            True if the analyzer class can handle the given file, else False.
        """
        if util.mimemagic.eval_glob(fileobject.mime_type,
                                    cls.HANDLES_MIME_TYPES):
            return True
        else:
            return False

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

    @classmethod
    def __str__(cls):
        return cls.__name__
