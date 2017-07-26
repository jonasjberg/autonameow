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

from analyzers import BaseAnalyzer
from core.util import dateandtime


class PdfAnalyzer(BaseAnalyzer):
    run_queue_priority = 1
    handles_mime_types = ['application/pdf']

    def __init__(self, file_object, add_results_callback, extracted_data):
        super(PdfAnalyzer, self).__init__(
            file_object, add_results_callback, extracted_data
        )
        self.add_results = add_results_callback

        self.text = None

    def _add_results(self, label, data):
        query_string = 'analysis.pdfanalyzer.{}'.format(label)
        logging.debug('{} passed "{}" to "add_results" callback'.format(
            self, query_string)
        )
        self.add_results(query_string, data)

    def run(self):
        self.text = self.extracted_data.get('contents.textual.raw_text')

        # Pass results through callback function provided by the 'Analysis'.
        self._add_results('author', self.get_author())
        self._add_results('title', self.get_title())
        self._add_results('datetime', self.get_datetime())
        self._add_results('publisher', self.get_publisher())

    def __collect_results(self, query_string, weight):
        value = self.extracted_data.get(query_string)
        if value:
            return result_list_add(value, query_string, weight)
        else:
            return []

    def get_author(self):
        results = []

        possible_authors = [
            ('metadata.exiftool.PDF:Author', 1),
            ('metadata.exiftool.PDF:Creator', 0.8),
            ('metadata.exiftool.PDF:Producer', 0.8),
            ('metadata.exiftool.XMP:Creator', 0.8),
            ('metadata.pypdf.Author', 1),
            ('metadata.pypdf.Creator',  0.8),
            ('metadata.pypdf.Producer',  0.5)
        ]
        for query_string, weight, in possible_authors:
            results += self.__collect_results(query_string, weight)

        return results

    def get_title(self):
        results = []

        possible_titles = [
            ('metadata.exiftool.PDF:Title', 1),
            ('metadata.exiftool.XMP:Title', 8),
            ('metadata.exiftool.PDF:Subject', 0.25),
            ('metadata.pypdf.Title', 1),
            ('metadata.pypdf.Subject', 0.25)
        ]
        for query_string, weight in possible_titles:
            results += self.__collect_results(query_string, weight)

        return results

    def get_datetime(self):
        results = []

        if self.text:
            text_timestamps = self._get_datetime_from_text()
            if text_timestamps:
                results += text_timestamps

        return results

    def get_tags(self):
        # TODO: [TD0005] Remove, use callbacks instead.
        raise NotImplementedError('Get "tags" from PdfAnalyzer')

    def get_publisher(self):
        results = []

        possible_publishers = [
            ('metadata.exiftool.PDF:EBX_PUBLISHER', 1),
            ('metadata.exiftool.XMP:EbxPublisher', 1),
            ('metadata.pypdf.EBX_PUBLISHER', 1)
        ]
        for query_string, weight in possible_publishers:
            results += self.__collect_results(query_string, weight)

        return results

    def _is_gmail(self):
        """
        Check whether the text might be a "Gmail".
        :return: True if the text is a Gmail, else False
        """
        text = self.text
        if type(text) is list:
            text = ' '.join(text)

        if text.lower().find('gmail'):
            logging.debug('Text might be a Gmail (contains "gmail")')
            return True
        else:
            return False

    def _get_datetime_from_text(self):
        """
        Extracts date and time information from the documents textual content.
        :return: a list of dictionaries on the form:
                 [ { 'value': datetime.datetime(2016, 6, 5, 16, ..),
                     'source' : 'content',
                     'weight'  : 0.1
                   }, .. ]
        """
        results = []
        text = self.text
        if type(text) == list:
            text = ' '.join(text)

        dt_regex = dateandtime.regex_search_str(text)
        if dt_regex:
            if isinstance(dt_regex, list):
                for e in dt_regex:
                    results.append({'value': e,
                                    'source': 'text_content_regex',
                                    'weight': 0.25})
            else:
                results.append({'value': dt_regex,
                                'source': 'text_content_regex',
                                'weight': 0.25})

        # TODO: Temporary premature return skips brute force search ..
        return results

        matches = 0
        text_split = text.split('\n')
        logging.debug('Try getting datetime from text split by newlines')
        for t in text_split:
            dt_brute = dateandtime.bruteforce_str(t)
            if dt_brute:
                matches += 1
                if isinstance(dt_brute, list):
                    for e in dt_brute:
                        results.append({'value': e,
                                        'source': 'text_content_brute',
                                        'weight': 0.1})
                else:
                    results.append({'value': dt_brute,
                                    'source': 'text_content_brute',
                                    'weight': 0.1})

        if matches == 0:
            logging.debug('No matches. Trying with text split by whitespace')
            text_split = text.split()
            for t in text_split:
                dt_brute = dateandtime.bruteforce_str(t)
                if dt_brute:
                    matches += 1
                    if isinstance(dt_brute, list):
                        for e in dt_brute:
                            results.append({'value': e,
                                            'source': 'text_content_brute',
                                            'weight': 0.1})
                    else:
                        results.append({'value': dt_brute,
                                        'source': 'text_content_brute',
                                        'weight': 0.1})

        return results


def result_list_add(value, source, weight):
    return [{'value': value,
             'source': source,
             'weight': weight}]
