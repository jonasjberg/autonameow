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

from core.config.constants import ANALYSIS_RESULTS_FIELDS
from core.exceptions import AnalysisResultsFieldError


class AbstractAnalyzer(object):
    """
    Abstract Analyzer base class.
    All methods must be implemented by inheriting classes.
    """
    run_queue_priority = None

    def __init__(self, file_object):
        self.file_object = file_object
        self.applies_to_mime = None

    def run(self):
        """
        Starts the analysis performed by this analyzer.
        """
        raise NotImplementedError

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
        if field not in ANALYSIS_RESULTS_FIELDS:
            raise AnalysisResultsFieldError(field)

        _func_name = 'get_{}'.format(field)
        get_func = getattr(self, _func_name, False)
        if callable(get_func):
            return get_func()
        else:
            raise NotImplementedError(field)

    def get_datetime(self):
        raise NotImplementedError

    def get_title(self):
        raise NotImplementedError

    def get_author(self):
        raise NotImplementedError

    def get_tags(self):
        raise NotImplementedError

    def get_publisher(self):
        raise NotImplementedError


def get_analyzer_classes():
    """
    Get a list of all available analyzers as a list of "type".
    All classes inheriting from the "AbstractAnalyzer" class are included.

    Returns:
        All available analyzer classes as a list of type.
    """
    return [klass for klass in globals()['AbstractAnalyzer'].__subclasses__()]


def get_analyzer_classes_basename():
    """
    Get a list of class base names for all available analyzers.
    All classes inheriting from the "AbstractAnalyzer" class are included.

    Returns:
        The base names of available analyzer classes as a list of strings.
    """
    return [c.__name__ for c in get_analyzer_classes()]


def get_instantiated_analyzers():
    """
    Get a list of all available analyzers as instantiated class objects.
    All classes inheriting from the "AbstractAnalyzer" class are included.

    Returns:
        A list of class instances, one per subclass of "AbstractAnalyzer".
    """
    # NOTE: These are instantiated with a None FIleObject, which might be a
    #       problem and is surely not very pretty.
    return [klass(None) for klass in get_analyzer_classes()]


def get_analyzer_mime_mappings():
    """
    Provides a mapping of which analyzers should apply to which mime types.

    Returns:
        Dictionary of strings or list of strings.
        The dictionary is keyed by the class names of all analyzers,
        storing the class variable 'applies_to_mime' from each analyzer.
    """
    analyzer_mime_mappings = {}
    for azr in get_instantiated_analyzers():
        analyzer_mime_mappings[azr.__class__] = azr.applies_to_mime
    return analyzer_mime_mappings