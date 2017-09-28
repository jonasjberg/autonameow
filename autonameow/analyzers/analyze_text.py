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

from analyzers import BaseAnalyzer
from core.util import dateandtime


class TextAnalyzer(BaseAnalyzer):
    run_queue_priority = 0.5
    HANDLES_MIME_TYPES = ['text/plain']

    def __init__(self, file_object, add_results_callback,
                 request_data_callback):
        super(TextAnalyzer, self).__init__(
            file_object, add_results_callback, request_data_callback
        )

        self.text = None

    def run(self):
        _response = self.request_data(self.file_object,
                                      'generic.contents.text')
        if _response is None:
            self.log.info(
                'Required data unavailable ("generic.contents.text")'
            )
            return

        if isinstance(_response, list):
            for _r in _response:
                if _r.value and len(_r.value) > 0:
                    self.text = _r.value
                    break
        else:
            if _response.value and len(_response.value) > 0:
                self.text = _response.value

        if self.text is None:
            self.log.info(
                'Required data unavailable ("generic.contents.text")'
            )
            return

        # Pass results through callback function provided by the 'Analysis'.
        self._add_results('author', self.get_author())
        self._add_results('title', self.get_title())
        self._add_results('datetime', self.get_datetime())

    def get_author(self):
        pass

    def get_title(self):
        pass

    def get_datetime(self):
        results = []
        if self.text:
            text_timestamps = self._get_datetime_from_text()
            if text_timestamps:
                results += text_timestamps

        return results if results else None

    def get_tags(self):
        pass

    def _is_gmail(self):
        text = self.text
        if type(text) is list:
            text = ' '.join(text)

        if text.lower().find('gmail'):
            self.log.debug('Text might be a Gmail (contains "gmail")')
            return

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

        if type(text) == list:
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
