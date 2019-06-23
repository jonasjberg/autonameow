# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2019 Jonas Sjöberg <autonameow@jonasjberg.com>
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
import sys
from functools import lru_cache

from core import logs
from extractors import ExtractorError
from extractors.text.base import BaseTextExtractor


log = logging.getLogger(__name__)


# TODO: [TD0027] Add text extractor for Word Documents.
# TODO: [TD0064] Add text extractor for DjVu E-books ('djvutxt'?)


def could_get_plain_text_from(fileobject):
    available_text_extractors, _ = collect_included_excluded_text_extractors()
    return [
        x for x in available_text_extractors if x.can_handle(fileobject)
    ]


def get_plain_text(fileobject):
    result = None

    suitable_extractors = could_get_plain_text_from(fileobject)
    log.debug('Text extractors that can handle the current file: %d',
              len(suitable_extractors))

    for extractor in suitable_extractors:
        extractor_instance = _get_pooled_instance(extractor)

        with logs.log_runtime(log, str(extractor)):
            try:
                result = extractor_instance.extract_text(fileobject)
            except (ExtractorError, NotImplementedError) as e:
                log.error('Text extraction failed! Aborting %s :: %s',
                          extractor_instance, e)
                continue

        # TODO: Make sure that the text is not empty or only whitespace.
        if result:
            log.debug('Using text returned by %s', extractor_instance)
            break
        else:
            log.debug('Got empty result from %s', extractor_instance)
            continue

    return result


def _find_text_extractor_classes(module_name='text'):
    __import__(module_name)
    namespace = inspect.getmembers(sys.modules[module_name], inspect.isclass)

    klasses = list()
    for _obj_name, _obj_type in namespace:
        if not issubclass(_obj_type, BaseTextExtractor):
            continue

        if _obj_type == BaseTextExtractor:
            # Ignore the base class.
            continue

        klasses.append(_obj_type)

    return klasses


@lru_cache()
def collect_included_excluded_text_extractors():
    klasses = _find_text_extractor_classes()

    excluded = set()
    included = set()
    for klass in klasses:
        if klass.dependencies_satisfied():
            included.add(klass)
        else:
            excluded.add(klass)

    return included, excluded


# Instantiate each extractor only once and then re-use the instances.
# Prevents needlessly re-creating caches and their underlying persistence.
_INSTANCE_POOL = dict()


def _get_pooled_instance(klass):
    instance = _INSTANCE_POOL.get(klass)
    if not instance:
        instance = klass()
        _INSTANCE_POOL[klass] = instance
    return instance
