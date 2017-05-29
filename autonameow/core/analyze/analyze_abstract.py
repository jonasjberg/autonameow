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
