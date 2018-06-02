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

    suitable_providers = could_get_plain_text_from(fileobject)
    for provider in suitable_providers:
        provider_instance = provider()

        with logs.log_runtime(log, str(provider)):
            try:
                result = provider_instance.extract_text(fileobject)
            except (ExtractorError, NotImplementedError) as e:
                log.error('Text extraction failed! Aborting extractor "{!s}":'
                          ' {!s}'.format(provider_instance, e))
                continue

        if result:
            # TODO: Make sure that the text is not empty or only whitespace.
            log.debug('Using result provided by "{!s}"'.format(provider_instance))
            break
        else:
            log.debug('Did not get anything from "{!s}"'.format(provider_instance))
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
