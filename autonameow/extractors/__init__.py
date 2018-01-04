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

import inspect
import logging
import os
import sys

from .common import (
    BaseExtractor,
    ExtractorError,
)


log = logging.getLogger(__name__)


# Extractors are assumed to be located in the same directory as this file.
AUTONAMEOW_EXTRACTOR_PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, AUTONAMEOW_EXTRACTOR_PATH)


# TODO: [TD0127] Clean up boundaries/interface to the 'extractors' package.


def find_extractor_module_files():
    """
    Finds Python source files assumed to be autonameow extractors.

    Returns: List of found extractor source files basenames.
    """
    extractor_files = [
        x for x in os.listdir(AUTONAMEOW_EXTRACTOR_PATH)
        if x.endswith('.py')
        and x != '__init__.py'
        and x != '__pycache__'
        and x != 'common.py'
        and not x.startswith('.')
    ]
    return extractor_files


def _get_package_classes(packages):
    klasses = []
    _abstract_extractor_classes = []

    for package in packages:
        __import__(package, None, None)
        namespace = inspect.getmembers(sys.modules[package],
                                       inspect.isclass)
        for _obj_name, _obj_type in namespace:
            if not issubclass(_obj_type, BaseExtractor):
                continue
            if _obj_type == BaseExtractor:
                continue
            if _obj_name.startswith('Abstract'):
                _abstract_extractor_classes.append(_obj_type)
            else:
                klasses.append(_obj_type)

    return _abstract_extractor_classes, klasses


def _get_module_classes(modules):
    # Strip extensions from file names.
    _to_import = [f[:-3] for f in modules]

    _extractor_classes = []
    _abstract_extractor_classes = []
    for extractor_file in _to_import:
        __import__(extractor_file, None, None)
        namespace = inspect.getmembers(sys.modules[extractor_file],
                                       inspect.isclass)
        for _obj_name, _obj_type in namespace:
            if not issubclass(_obj_type, BaseExtractor):
                continue
            if _obj_type == BaseExtractor:
                continue
            if _obj_name.startswith('Abstract'):
                _abstract_extractor_classes.append(_obj_type)
            else:
                _extractor_classes.append(_obj_type)

    return _abstract_extractor_classes, _extractor_classes


def get_extractor_classes(packages, modules):
    _p_abstract, _p_implemented = _get_package_classes(packages)
    _m_abstract, _m_implemented = _get_module_classes(modules)

    _implemented = _p_implemented + _m_implemented

    out = []
    for klass in _implemented:
        if klass.check_dependencies():
            out.append(klass)
        else:
            log.info('Excluding extractor "{!s}" due to unmet dependencies'.format(klass))

    for o in out:
        log.debug('Registered extractor class: "{!s}"'.format(o))

    return out


_extractor_module_files = find_extractor_module_files()
ProviderClasses = get_extractor_classes(
    packages=['filesystem', 'metadata', 'text'],
    modules=_extractor_module_files
)
