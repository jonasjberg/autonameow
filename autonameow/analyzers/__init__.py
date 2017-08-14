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

import inspect
import os
import sys

from core import (
    constants,
    exceptions
)
from core.fileobject import eval_magic_glob


# Analyzers are assumed to be located in the same directory as this file.
AUTONAMEOW_ANALYZER_PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, AUTONAMEOW_ANALYZER_PATH)


class BaseAnalyzer(object):
    """
    Top-level abstract base class for all content-specific analyzer classes.

    Includes common functionality and interfaces that must be implemented
    by inheriting analyzer classes.
    """
    run_queue_priority = None
    handles_mime_types = None

    def __init__(self, file_object, add_results_callback,
                 request_data_callback):
        self.file_object = file_object
        self.add_results = add_results_callback
        self.request_data = request_data_callback

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
        if field not in constants.ANALYSIS_RESULTS_FIELDS:
            raise exceptions.AnalysisResultsFieldError(field)

        _func_name = 'get_{}'.format(field)
        get_func = getattr(self, _func_name, False)
        if get_func and callable(get_func):
            return get_func()
        else:
            raise NotImplementedError(field)

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


def find_analyzer_files():
    """
    Finds Python source files assumed to be autonameow analyzers.

    Returns: List of basenames of any found analyzer source files.
    """
    analyzer_files = [x for x in os.listdir(AUTONAMEOW_ANALYZER_PATH)
                      if x.endswith('.py') and x.startswith('analyze_')
                      and x != '__init__.py']
    return analyzer_files


def suitable_analyzers_for(file_object):
    """
    Returns analyzer classes that can handle the given file object.

    Args:
        file_object: File to get analyzers for as an instance of 'FileObject'.

    Returns:
        A list of analyzer classes that can analyze the given file.
    """
    return [a for a in AnalyzerClasses if a.can_handle(file_object)]


def _get_implemented_analyzer_classes(analyzer_files):
    # Strip extensions.
    _to_import = [f[:-3] for f in analyzer_files]

    _analyzer_classes = []
    for analyzer_file in _to_import:
        __import__(analyzer_file, None, None)
        namespace = inspect.getmembers(sys.modules[analyzer_file],
                                       inspect.isclass)
        for _obj_name, _obj_type in namespace:
            if not issubclass(_obj_type, BaseAnalyzer):
                continue
            elif _obj_type == BaseAnalyzer:
                continue
            else:
                _analyzer_classes.append(_obj_type)

    return _analyzer_classes


analyzer_source_files = find_analyzer_files()


def get_analyzer_classes():
    """
    Get a list of all available analyzers as a list of "type".
    All classes inheriting from the "Analyzer" class are included.

    Returns:
        All available analyzer classes as a list of type.
    """
    return _get_implemented_analyzer_classes(analyzer_source_files)


def get_analyzer_classes_basename():
    """
    Get a list of class base names for all available analyzers.
    All classes inheriting from the "Analyzer" class are included.

    Returns:
        The base names of available analyzer classes as a list of strings.
    """
    return [c.__name__ for c in get_analyzer_classes()]


def get_query_strings():
    """
    Get the set of "query strings" for all analyzer classes.

    Returns:
        Unique analyzer query strings as a set.
    """
    out = set()
    # TODO: [TD0052] Implement gathering data on non-core modules at run-time
    # for a in AnalyzerClasses:
    #     if a.data_query_string:
    #         out.add(a.data_query_string)
    return out


AnalyzerClasses = get_analyzer_classes()
QueryStrings = get_query_strings()
