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

import io
import logging as log

from unidecode import unidecode

from analyzers import BaseAnalyzer
from core.util import dateandtime


class TextAnalyzer(BaseAnalyzer):
    run_queue_priority = 0.5
    handles_mime_types = ['text/plain']

    def __init__(self, file_object, add_results_callback, extracted_data):
        super(TextAnalyzer, self).__init__(
            file_object, add_results_callback, extracted_data
        )
        self.add_results = add_results_callback

        self.text = None

    def _add_results(self, label, data):
        query_string = 'analysis.text_analyzer.{}'.format(label)
        log.debug('{} passed "{}" to "add_results" callback'.format(
            self, query_string)
        )
        self.add_results(query_string, data)

    def run(self):
        self.text = self._extract_text_content()

        # Pass results through callback function provided by the 'Analysis'.
        self._add_results('author', self.get_author())
        self._add_results('title', self.get_title())
        self._add_results('datetime', self.get_datetime())

    def get_author(self):
        pass

    def get_title(self):
        pass

    def get_datetime(self):
        result = []
        if self.text:
            text_timestamps = self._get_datetime_from_text()
            if text_timestamps:
                result += text_timestamps

        return result

    def get_tags(self):
        pass

    # TODO: [TD0006] Move all text extraction to functions in 'extract_text.py'.
    def _extract_text_content(self):
        """
        Extract the plain text contents of a text file as strings.
        :return: False or text content as strings
        """
        content = self._get_file_lines()
        # NOTE: Handle encoding properly

        decoded_content = []
        for line in content:
            # Collapse whitespace.
            # '\xa0' is non-breaking space in Latin1 (ISO 8859-1), also chr(160)
            line = unidecode(line)
            line = " ".join(line.replace("\xa0", " ").strip().split())
            decoded_content.append(line)

        if decoded_content:
            # TODO: Determine what gets extracted **REALLY** ..
            log.debug('Extracted {} words/lines (??) of content'.format(
                len(content)))
            return decoded_content
        else:
            log.warning('Unable to extract text contents.')
            return None

    def _is_gmail(self):
        text = self.text
        if type(text) is list:
            text = ' '.join(text)

        if text.lower().find('gmail'):
            log.debug('Text might be a Gmail (contains "gmail")')
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
            log.debug('Unable to extract date/time-information from text file '
                      'contents using regex search.')

        if type(text) == list:
            text = ' '.join(text)

        matches_brute = 0
        log.debug('Try getting datetime from text split by newlines')
        for t in text.split('\n'):
            dt_brute = dateandtime.bruteforce_str(t)
            if dt_brute:
                for dt in dt_brute:
                    matches_brute += 1
                    results.append({'value': dt,
                                    'source': 'bruteforce_search',
                                    'weight': 0.1})
        if matches_brute == 0:
            log.debug('Unable to extract date/time-information from text file '
                      'contents using brute force search.')
        else:
            log.debug('Brute force search for date/time-information returned '
                      '{} results.'.format(matches_brute))

        return results

    # TODO: [TD0006] Move all text extraction to functions in 'extract_text.py'.
    def _get_file_lines(self):
        fn = self.file_object.abspath
        with io.open(fn, 'r', encoding='utf8') as f:
            contents = f.read().split('\n')
            if contents:
                log.info('Successfully read {} lines from "{}"'.format(
                    len(contents), str(fn)))
                return contents
            else:
                log.error('Got empty file "{}"'.format(fn))
                return None
