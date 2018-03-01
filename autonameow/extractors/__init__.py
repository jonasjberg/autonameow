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

EXTRACTOR_CLASS_PACKAGES = ['filesystem', 'metadata', 'text']
EXTRACTOR_CLASS_PACKAGES_TEXT = ['text']
EXTRACTOR_CLASS_PACKAGES_METADATA = ['metadata']


def _find_extractor_classes_in_packages(packages):
    klasses = []
    for package in packages:
        __import__(package)
        namespace = inspect.getmembers(sys.modules[package], inspect.isclass)
        for _obj_name, _obj_type in namespace:
            if not issubclass(_obj_type, BaseExtractor):
                continue
            if _obj_type == BaseExtractor:
                continue
            if _obj_name.startswith('Abstract'):
                continue
            klasses.append(_obj_type)
    return klasses


def get_extractor_classes(packages):
    klasses = _find_extractor_classes_in_packages(packages)

    out = []
    for klass in klasses:
        if klass.check_dependencies():
            out.append(klass)
            log.debug('Registered extractor class: "{!s}"'.format(klass))
        else:
            log.info('Excluded extractor "{!s}" due to unmet dependencies'.format(klass))
    return out


def dump_extractor_field_lookups():
    global ProviderClasses
    from core import types
    from util import disk
    # import pdb
    # pdb.set_trace()

    # TODO: [temporary][debug] Store only strings in 'FIELD_LOOKUP'.

    for provider in ProviderClasses:
        _prefix = str(provider.meowuri_prefix())
        prefix = types.AW_PATHCOMPONENT(_prefix)
        extension = types.AW_PATHCOMPONENT('.yaml')
        dest = disk.joinpaths(
            b'/Users/jonas/PycharmProjects/autonameow.git/autonameow/extractors/',
            prefix + extension,
        )
        p = provider()
        field_lookup_data = p.metainfo()
        del p
        disk.write_yaml_file(dest, field_lookup_data)


ProviderClasses = get_extractor_classes(EXTRACTOR_CLASS_PACKAGES)
TextProviderClasses = get_extractor_classes(EXTRACTOR_CLASS_PACKAGES_TEXT)
MetadataProviderClasses = get_extractor_classes(EXTRACTOR_CLASS_PACKAGES_METADATA)


# dump_extractor_field_lookups()
