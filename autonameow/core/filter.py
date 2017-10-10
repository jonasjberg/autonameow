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

import logging
from datetime import datetime

from core import types


log = logging.getLogger(__name__)


class ResultFilter(object):
    """
    Class ResultFilter handles filtering of the results gathered by file
    analysis by evaluating the results based on a set of filter rules.
    """

    # TODO: [TD0035] This class needs a complete rewrite!

    # TODO: [TD0034] All filtering must be (re-)designed.

    def __init__(self):
        self.rules = {'ignore_years': [],
                      'ignore_before_year': None,
                      'ignore_after_year': None}

    def configure_filter(self, opts):
        # TODO: [TD0034][TD0035] Fix this and overall filter handling.
        if opts.get('filter_ignore_years'):
            for year in opts.get('filter_ignore_years', []):
                try:
                    dt = datetime.strptime(str(year), '%Y')
                except ValueError as e:
                    log.warning('Erroneous date format: "{!s}"'.format(e))
                else:
                    if dt not in self.rules['ignore_years']:
                        self.rules['ignore_years'].append(dt)

            ignored_years = ', '.join((str(yr.year)
                                       for yr in self.rules['ignore_years']))
            log.debug('Using filter: ignore date/time-information for these'
                      ' years: {}'.format(ignored_years))

        _filter_ignore_to_year = opts.get('filter_ignore_to_year')
        if _filter_ignore_to_year:
            _year_string = types.force_string(_filter_ignore_to_year)
            if _year_string:
                try:
                    dt = datetime.strptime(_year_string, '%Y')
                except ValueError as e:
                    log.warning('Erroneous date format: "{!s}"'.format(e))
                else:
                    log.debug('Using filter: ignore date/time-information that'
                              ' predate year {}'.format(dt.year))
                    self.rules['ignore_before_year'] = dt
            else:
                log.warning('Expected a non-empty string')

        _filter_ignore_from_year = opts.get('filter_ignore_from_year')
        if _filter_ignore_from_year:
            _year_string = types.force_string(_filter_ignore_from_year)
            if _year_string:
                try:
                    dt = datetime.strptime(_year_string, '%Y')
                except ValueError as e:
                    log.warning('Erroneous date format: "{!s}"'.format(e))
                else:
                    log.debug('Using filter: ignore date/time-information that'
                              ' follow year {}'.format(dt.year))
                    self.rules['ignore_after_year'] = dt
            else:
                log.warning('Expected a non-empty string')
