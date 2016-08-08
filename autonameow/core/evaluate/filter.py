# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

import logging
from datetime import datetime


class ResultFilter(object):
    """
    Class ResultFilter handles filtering of the results gathered by file
    analysis by evaluating the results based on a set of filter rules.
    """
    def __init__(self):
        self.rules = {'ignore_years': [],
                      'ignore_before_year': None,
                      'ignore_after_year': None}

    def configure_filter(self, opts):
        # TODO: Fix this and overall filter handling.
        if opts.filter_ignore_years:
            for year in opts.filter_ignore_years:
                try:
                    dt = datetime.strptime(str(year), '%Y')
                except ValueError as e:
                    logging.warning('Erroneous date format: '
                                    '"{}"'.format(e.message))
                else:
                    if dt not in self.rules['ignore_years']:
                        self.rules['ignore_years'].append(dt)

            ignored_years = ', '.join((str(yr.year)
                                       for yr in self.rules['ignore_years']))
            logging.debug('Using filter: ignore date/time-information for these'
                          ' years: {}'.format(ignored_years))

        if opts.filter_ignore_to_year:
            try:
                dt = datetime.strptime(str(opts.filter_ignore_to_year),
                                       '%Y')
            except ValueError as e:
                logging.warning('Erroneous date format: {}'.format(e.message))
            else:
                logging.debug('Using filter: ignore date/time-information that'
                              ' predate year {}'.format(dt.year))
                self.rules['ignore_before_year'] = dt

        if opts.filter_ignore_from_year:
            try:
                dt = datetime.strptime(str(opts.filter_ignore_from_year),
                                       '%Y')
            except ValueError as e:
                logging.warning('Erroneous date format: {}'.format(e.message))
            else:
                logging.debug('Using filter: ignore date/time-information that'
                              ' follow year {}'.format(dt.year))
                self.rules['ignore_after_year'] = dt
