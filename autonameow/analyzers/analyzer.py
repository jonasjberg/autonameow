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

from core import (
    constants,
    exceptions
)
from core.fileobject import eval_magic_glob


class Analyzer(object):
    """
    Top-level abstract base class for all content-specific analyzer classes.

    Includes common functionality and interfaces that must be implemented
    by inheriting analyzer classes.
    """
    run_queue_priority = None
    handles_mime_types = None

    def __init__(self, file_object, add_results_callback, extracted_data):
        self.file_object = file_object
        self.add_results = add_results_callback
        self.extracted_data = extracted_data

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
        # TODO: Remove, use callbacks instead.
        if field not in constants.ANALYSIS_RESULTS_FIELDS:
            raise exceptions.AnalysisResultsFieldError(field)

        _func_name = 'get_{}'.format(field)
        get_func = getattr(self, _func_name, False)
        if callable(get_func):
            return get_func()
        else:
            raise NotImplementedError(field)

    def get_datetime(self):
        # TODO: Remove, use callbacks instead.
        raise NotImplementedError('Must be implemented by inheriting classes.')

    def get_title(self):
        # TODO: Remove, use callbacks instead.
        raise NotImplementedError('Must be implemented by inheriting classes.')

    def get_author(self):
        # TODO: Remove, use callbacks instead.
        raise NotImplementedError('Must be implemented by inheriting classes.')

    def get_tags(self):
        # TODO: Remove, use callbacks instead.
        raise NotImplementedError('Must be implemented by inheriting classes.')

    def get_publisher(self):
        # TODO: Remove, use callbacks instead.
        raise NotImplementedError('Must be implemented by inheriting classes.')

    @classmethod
    def can_handle(cls, file_object):
        """
        Tests if this analyzer class can handle the given file.

        The analyzer is considered to be able to handle the given file if the
        file MIME type is listed in the class attribute 'handles_mime_types'.

        Inheriting analyzer classes can override this method if they need
        to perform additional tests in order to determine if they can handle
        the given file object.

        Args:
            file_object: The file to test as an instance of 'FileObject'.

        Returns:
            True if the analyzer class can handle the given file, else False.
        """
        if eval_magic_glob(file_object.mime_type, cls.handles_mime_types):
            return True
        else:
            return False

    def __str__(self):
        return self.__class__.__name__


