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

from analyzers.analyzer import Analyzer


# Analyzers are assumed to be located in the same directory as this file.
AUTONAMEOW_ANALYZER_PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, AUTONAMEOW_ANALYZER_PATH)


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
            if not issubclass(_obj_type, Analyzer):
                continue
            elif _obj_type == Analyzer:
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


AnalyzerClasses = get_analyzer_classes()
