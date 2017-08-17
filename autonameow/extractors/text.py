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

import logging as log

from core import exceptions
from extractors import BaseExtractor


class AbstractTextExtractor(BaseExtractor):
    def __init__(self, source):
        super(AbstractTextExtractor, self).__init__(source)

        self._raw_text = None

    def query(self, field=None):
        # TODO: [TD0057] Will text extractors be queried for anything but text?
        if not self._raw_text:
            try:
                log.debug('{!s} received initial query ..'.format(self))
                self._perform_initial_extraction()
            except exceptions.ExtractorError as e:
                log.error('{!s} query FAILED; Error: {!s}'.format(self, e))
                raise
            except NotImplementedError as e:
                log.debug('[WARNING] Called unimplemented code in {!s}: '
                          '{!s}'.format(self, e))
                raise exceptions.ExtractorError

        if not field:
            # TODO: [TD0057] Fix this. Look over the entire 'query' method.
            log.debug('{!s} responding to query for all fields'.format(self))
            return self._raw_text
        else:
            log.debug('{!s} ignoring query for field (returning all fields):'
                      ' "{!s}"'.format(self, field))
            return self._raw_text

    def _perform_initial_extraction(self):
        self._raw_text = self._get_raw_text()

    def _get_raw_text(self):
        raise NotImplementedError('Must be implemented by inheriting classes.')
