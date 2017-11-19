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
import logging
import os
import sys

from .common import (
    AnalyzerError,
    BaseAnalyzer
)


# Analyzers are assumed to be located in the same directory as this file.
AUTONAMEOW_ANALYZER_PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, AUTONAMEOW_ANALYZER_PATH)


log = logging.getLogger(__name__)


# TODO: [TD0126] Clean up boundaries/interface to the 'analyzers' package.


def find_analyzer_files():
    """
    Finds Python source files assumed to be autonameow analyzers.

    Returns: List of basenames of any found analyzer source files.
    """
    analyzer_files = [x for x in os.listdir(AUTONAMEOW_ANALYZER_PATH)
                      if x.endswith('.py') and x.startswith('analyze_')]
    return analyzer_files


def suitable_analyzers_for(fileobject):
    """
    Returns analyzer classes that can handle the given file object.

    Args:
        fileobject: File to get analyzers for as an instance of 'FileObject'.

    Returns:
        A list of analyzer classes that can analyze the given file.
    """
    return [a for a in AnalyzerClasses if a.can_handle(fileobject)]


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
    klasses = _get_implemented_analyzer_classes(analyzer_source_files)

    out = []
    for klass in klasses:
        if klass.check_dependencies():
            out.append(klass)
        else:
            log.warning('Excluding analyzer "{!s}" due to unmet '
                        'dependencies'.format(klass))
    return out


def map_meowuri_to_analyzers():
    """
    Returns a mapping of the analyzer classes "meowURIs" and classes.

    Each analyzer class defines 'MEOWURI_ROOT' which is used as the
    first part of all data returned by the analyzer.

    Returns: A dictionary where the keys are "meowURIs" and the values
        are lists of analyzer classes.
    """
    out = {}

    for klass in AnalyzerClasses:
        _meowuri = klass.meowuri_prefix()
        if not _meowuri:
            log.error(
                'Got None from "{!s}.meowuri_prefix()"'.format(klass.__name__)
            )
            continue

        if _meowuri in out:
            out[_meowuri].append(klass)
        else:
            out[_meowuri] = [klass]

    return out


AnalyzerClasses = get_analyzer_classes()
MeowURIClassMap = map_meowuri_to_analyzers()
