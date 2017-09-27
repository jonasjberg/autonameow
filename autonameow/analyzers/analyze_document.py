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


class DocumentAnalyzer(BaseAnalyzer):
    run_queue_priority = 1
    HANDLES_MIME_TYPES = ['application/pdf', 'text/*']

    def __init__(self, file_object, add_results_callback,
                 request_data_callback):
        super(DocumentAnalyzer, self).__init__(
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

        self.text = _response
        self._add_results('author', self.get_author())
        self._add_results('title', self.get_title())
        self._add_results('datetime', self.get_datetime())
        self._add_results('publisher', self.get_publisher())

    def __collect_results(self, meowuri, weight):
        value = self.request_data(self.file_object, meowuri)
        if value:
            return result_list_add(value, meowuri, weight)
        else:
            return []

    def get_author(self):
        results = []

        possible_authors = [
            ('generic.metadata.author', 1),
            ('generic.metadata.creator', 0.5),
            ('generic.metadata.producer', 0.1),
        ]
        for meowuri, weight, in possible_authors:
            results += self.__collect_results(meowuri, weight)

        return results if results else None

    def get_title(self):
        results = []

        possible_titles = [
            ('generic.metadata.title', 1),
            ('generic.metadata.subject', 0.25),
        ]
        for meowuri, weight in possible_titles:
            results += self.__collect_results(meowuri, weight)

        return results if results else None

    def get_datetime(self):
        results = []

        if self.text:
            text_timestamps = self._get_datetime_from_text()
            if text_timestamps:
                results += text_timestamps

        return results if results else None

    def get_tags(self):
        raise NotImplementedError('Get "tags" from PdfAnalyzer')

    def get_publisher(self):
        results = []

        possible_publishers = [
            ('extractor.metadata.exiftool.PDF:EBX_PUBLISHER', 1),
            ('extractor.metadata.exiftool.XMP:EbxPublisher', 1),
            ('extractor.metadata.pypdf.EBX_PUBLISHER', 1)
        ]
        for meowuri, weight in possible_publishers:
            results += self.__collect_results(meowuri, weight)

        return results if results else None

    def _is_gmail(self):
        """
        Check whether the text might be a "Gmail".
        :return: True if the text is a Gmail, else False
        """
        text = self.text
        if type(text) is list:
            text = ' '.join(text)

        if text.lower().find('gmail'):
            self.log.debug('Text might be a Gmail (contains "gmail")')
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
        self.log.debug('Try getting datetime from text split by newlines')
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
            self.log.debug('No matches. Trying with text split by whitespace')
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

    @classmethod
    def check_dependencies(cls):
        return True


def result_list_add(value, source, weight):
    return [{'value': value,
             'source': source,
             'weight': weight}]
