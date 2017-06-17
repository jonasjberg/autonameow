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

from core import constants
from core.exceptions import AnalysisResultsFieldError


class Analyzer(object):
    """
    Abstract Analyzer base class.
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
            raise AnalysisResultsFieldError(field)

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

    def __str__(self):
        return self.__class__.__name__


def get_analyzer_classes():
    """
    Get a list of all available analyzers as a list of "type".
    All classes inheriting from the "Analyzer" class are included.

    Returns:
        All available analyzer classes as a list of type.
    """

    # TODO: Fix this! Used for instantiating analyzers so that they are
    # included in the global namespace and seen by 'get_analyzer_classes()'.

    from analyzers.analyze_filename import FilenameAnalyzer
    from analyzers.analyze_filesystem import FilesystemAnalyzer
    from analyzers.analyze_image import ImageAnalyzer
    from analyzers.analyze_pdf import PdfAnalyzer
    from analyzers.analyze_video import VideoAnalyzer

    return [klass for klass in globals()['Analyzer'].__subclasses__()]


def get_analyzer_classes_basename():
    """
    Get a list of class base names for all available analyzers.
    All classes inheriting from the "Analyzer" class are included.

    Returns:
        The base names of available analyzer classes as a list of strings.
    """
    return [c.__name__ for c in get_analyzer_classes()]


def get_instantiated_analyzers():
    """
    Get a list of all available analyzers as instantiated class objects.
    All classes inheriting from the "Analyzer" class are included.

    Returns:
        A list of class instances, one per subclass of "Analyzer".
    """
    # NOTE: These are instantiated with a None FileObject, which might be a
    #       problem and is surely not very pretty.
    return [klass(None, None, None) for klass in get_analyzer_classes()]
