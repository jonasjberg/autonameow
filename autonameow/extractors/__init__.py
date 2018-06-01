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

from .common import BaseMetadataExtractor
from .common import ExtractorError


log = logging.getLogger(__name__)


# Extractors are assumed to be located in the same directory as this file.
AUTONAMEOW_EXTRACTOR_PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, AUTONAMEOW_EXTRACTOR_PATH)

EXTRACTOR_CLASS_PACKAGES_FILESYSTEM = ['filesystem']
EXTRACTOR_CLASS_PACKAGES_METADATA = ['metadata']
EXTRACTOR_CLASS_PACKAGES = (EXTRACTOR_CLASS_PACKAGES_FILESYSTEM
                            + EXTRACTOR_CLASS_PACKAGES_METADATA)


def _find_extractor_classes_in_packages(packages):
    klasses = list()
    for package in packages:
        __import__(package)
        namespace = inspect.getmembers(sys.modules[package], inspect.isclass)
        for _obj_name, _obj_type in namespace:
            if not issubclass(_obj_type, BaseMetadataExtractor):
                continue
            if _obj_type == BaseMetadataExtractor:
                continue
            if _obj_name.startswith('Abstract'):
                continue
            klasses.append(_obj_type)
    return klasses


def collect_included_excluded_extractors(packages):
    klasses = _find_extractor_classes_in_packages(packages)

    excluded = list()
    included = list()
    for klass in klasses:
        if klass.dependencies_satisfied():
            included.append(klass)
        else:
            excluded.append(klass)
    return included, excluded


class ExtractorRegistry(object):
    def __init__(self):
        self._all_providers = None
        self._metadata_providers = None
        self._filesystem_providers = None
        self._excluded_providers = set()

    def _get_cached_or_collect(self, self_attribute, packages):
        if getattr(self, self_attribute) is None:
            self._collect_and_register(self_attribute, packages)
        return getattr(self, self_attribute)

    def _collect_and_register(self, self_attribute, packages):
        included, excluded = collect_included_excluded_extractors(packages)

        for included_klass in included:
            log.debug('Included extractor "{!s}"'.format(included_klass))
        for excluded_klass in excluded:
            log.info('Excluded extractor "{!s}" due to unmet dependencies'.format(excluded_klass))

        setattr(self, self_attribute, set(included))
        self._excluded_providers.update(excluded)

    @property
    def all_providers(self):
        return self._get_cached_or_collect('_all_providers',
                                           EXTRACTOR_CLASS_PACKAGES)

    @property
    def metadata_providers(self):
        return self._get_cached_or_collect('_metadata_providers',
                                           EXTRACTOR_CLASS_PACKAGES_METADATA)

    @property
    def filesystem_providers(self):
        return self._get_cached_or_collect('_filesystem_providers',
                                           EXTRACTOR_CLASS_PACKAGES_FILESYSTEM)

    @property
    def excluded_providers(self):
        return self._excluded_providers


registry = ExtractorRegistry()
