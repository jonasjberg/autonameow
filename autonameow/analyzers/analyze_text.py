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

from analyzers import BaseAnalyzer
from util import dateandtime


class TextAnalyzer(BaseAnalyzer):
    RUN_QUEUE_PRIORITY = 0.5
    HANDLES_MIME_TYPES = ['text/plain']

    # TODO: [TD0157] Look into analyzers 'FIELD_LOOKUP' attributes.

    def __init__(self, fileobject, config, request_data_callback):
        super().__init__(fileobject, config, request_data_callback)

        self.text = None

    def analyze(self):
        _maybe_text = self.request_any_textual_content()
        if not _maybe_text:
            return

        self.text = _maybe_text

        # TODO: [TD0102] Fix inconsistent results passed back by analyzers.
        # self._add_results('datetime', self.get_datetime())

    def get_datetime(self):
        results = []
        if self.text:
            text_timestamps = self._get_datetime_from_text()
            if text_timestamps:
                results += text_timestamps

        return results if results else None

    def _get_datetime_from_text(self):
        """
        Extracts date and time information from textual contents.
        :return: a list of dictionaries on the form:
                 [ { 'value': datetime.datetime(2016, 6, 5, 16, ..),
                     'source' : "Create date",
                     'weight'  : 1
                   }, .. ]
        """
        results = []
        text = self.text

        dt_regex = dateandtime.regex_search_str(text)
        if dt_regex:
            for dt in dt_regex:
                results.append({'value': dt,
                                'source': 'regex_search',
                                'weight': 0.25})
        else:
            self.log.debug('Unable to extract date/time-information from'
                           ' text file contents using regex search.')

        if isinstance(text, list):
            text = ' '.join(text)

        matches_brute = 0
        self.log.debug('Try getting datetime from text split by newlines')
        for t in text.split('\n'):
            dt_brute = dateandtime.bruteforce_str(t)
            if dt_brute:
                for dt in dt_brute:
                    matches_brute += 1
                    results.append({'value': dt,
                                    'source': 'bruteforce_search',
                                    'weight': 0.1})
        if matches_brute == 0:
            self.log.debug('Unable to extract date/time-information from'
                           ' text file contents using brute force search.')
        else:
            self.log.debug('Brute force search for date/time-information'
                           ' returned {} results.'.format(matches_brute))

        return results

    @classmethod
    def check_dependencies(cls):
        return True
