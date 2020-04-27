# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2020 Jonas Sjöberg <autonameow@jonasjberg.com>
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

import inspect
import logging
import os
import sys

from .common import AnalyzerError
from .common import BaseAnalyzer


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


def _get_implemented_analyzer_classes(analyzer_files):
    # Strip extensions.
    _to_import = [f[:-3] for f in analyzer_files]

    _analyzer_classes = list()
    for analyzer_file in _to_import:
        __import__(analyzer_file)
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
    Get a tuple of all available and any excluded analyzers.

    All classes inheriting from the "Analyzer" class are included if any and
    all dependencies are satisfied.

    Returns:
        A tuple of lists with included and excluded analyzer classes.
    """
    klasses = _get_implemented_analyzer_classes(analyzer_source_files)

    included = list()
    excluded = list()
    for klass in klasses:
        if klass.dependencies_satisfied():
            included.append(klass)
            log.debug('Included analyzer %s', klass)
        else:
            excluded.append(klass)
            log.debug('Excluded analyzer %s due to unmet dependencies', klass)
    return included, excluded


class AnalyzerRegistry(object):
    def __init__(self):
        self._all_providers = None
        self._excluded_providers = set()

    @property
    def all_providers(self):
        if self._all_providers is None:
            included, excluded = get_analyzer_classes()
            self._all_providers = set(included)
            self._excluded_providers.update(excluded)
        return self._all_providers

    @property
    def excluded_providers(self):
        return self._excluded_providers


registry = AnalyzerRegistry()
