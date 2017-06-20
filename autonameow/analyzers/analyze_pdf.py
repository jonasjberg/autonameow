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
import re
from datetime import datetime

from analyzers.analyzer import Analyzer
from core.util import dateandtime


class PdfAnalyzer(Analyzer):
    run_queue_priority = 1
    handles_mime_types = ['application/pdf']

    def __init__(self, file_object, add_results_callback, extracted_data):
        super(PdfAnalyzer, self).__init__(
            file_object, add_results_callback, extracted_data
        )
        self.add_results = add_results_callback

        self.meta_extractor = None

        self.exiftool = None
        self.exiftool_data = None

        self.metadata = None
        self.text = None

    def run(self):
        self.metadata = self.extracted_data.get('metadata.exiftool')
        self.text = self.extracted_data.get('contents.textual.raw_text')

    def __collect_results(self, query_string, src_dict, src_field, weight):
        if not src_dict:
            return []

        if src_field in src_dict:
            value = src_dict.get(src_field)
            return result_list_add(value, query_string, weight)
        else:
            return []

    def get_author(self):
        # TODO: Remove, use callbacks instead.
        results = []

        possible_authors = [
            ('metadata.exiftool.PDF:Author', self.exiftool_data,
             'PDF:Author', 1),
            ('metadata.exiftool.PDF:Creator', self.exiftool_data,
             'PDF:Creator', 0.8),
            ('metadata.exiftool.PDF:Producer', self.exiftool_data,
             'PDF:Producer', 0.8),
            ('metadata.exiftool.XMP:Creator', self.exiftool_data,
             'XMP:Creator', 0.8),
            ('metadata.pypdf.Author', self.metadata, 'Author', 1),
            ('metadata.pypdf.Creator', self.metadata, 'Creator', 0.8),
            ('metadata.pypdf.Producer', self.metadata, 'Producer', 0.5)]

        for query_string, source_dict, source_field, weight in possible_authors:
            results += self.__collect_results(query_string, source_dict,
                                              source_field, weight)
        return results

    def get_title(self):
        # TODO: Remove, use callbacks instead.
        results = []

        possible_titles = [
            ('metadata.exiftool.PDF:Title', self.exiftool_data,
             'PDF:Title', 1),
            ('metadata.exiftool.XMP:Title', self.exiftool_data,
             'XMP:Title', 8),
            ('metadata.exiftool.PDF:Subject', self.exiftool_data,
             'PDF:Subject', 0.25),
            ('metadata.pypdf.Title', self.metadata, 'Title', 1),
            ('metadata.pypdf.Subject', self.metadata, 'Creator', 0.25)]

        for query_string, source_dict, source_field, weight in possible_titles:
            results += self.__collect_results(query_string, source_dict,
                                              source_field, weight)

        return results

    def get_datetime(self):
        # TODO: Remove, use callbacks instead.
        results = []

        if self.metadata:
            metadata_datetime = self._get_metadata_datetime()
            if metadata_datetime:
                results += metadata_datetime

            if self.text:
                text_timestamps = self._get_datetime_from_text()
                if text_timestamps:
                    results += text_timestamps

        return results

    def get_tags(self):
        # TODO: Remove, use callbacks instead.
        raise NotImplementedError('Get "tags" from PdfAnalyzer')

    def get_publisher(self):
        # TODO: Remove, use callbacks instead.
        results = []

        possible_publishers = [
            ('metadata.exiftool.PDF:EBX_PUBLISHER', self.exiftool_data,
             'PDF:EBX_PUBLISHER', 1),
            ('metadata.exiftool.XMP:EbxPublisher', self.exiftool_data,
             'XMP:EbxPublisher', 1),
            ('metadata.pypdf.EBX_PUBLISHER', self.metadata,
             'EBX_PUBLISHER', 1)]

        for query_string, src_dict, src_field, weight in possible_publishers:
            results += self.__collect_results(query_string, src_dict,
                                              src_field, weight)
        return results

    def _get_metadata_datetime(self):
        """
        Extract date and time information from pdf metadata.
        :return: dict of datetime-objects
        """

        # TODO: This method is being moved to a function in 'metadata.py'.

        DATE_TAG_FIELDS = ['ModDate', 'CreationDate', 'ModDate']

        results = []
        for field in DATE_TAG_FIELDS:
            date = time = k = None
            if field in self.metadata:
                try:
                    k = self.metadata[field]
                    k = k.strip()
                except KeyError:
                    logging.error('KeyError for key [{}]'.format(field))
                    continue

            if k is None:
                logging.debug('Null value in metadata field [%s]' % field)
                continue

            found_match = False
            dt = None
            # Expected date format:             D:20121225235237+05'30'
            #
            # Regex search matches two groups:  D: 20121225235237 +05'30'
            #                                      ^            ^ ^     ^
            #                                      '------------' '-----'
            #                                            #1         #2
            #
            date_pattern_with_tz = re.compile('D:(\d{14})(\+\d{2}\'\d{2}\')')
            re_match_tz = date_pattern_with_tz.search(k)
            if re_match_tz:
                datetime_str = re_match_tz.group(1)
                timezone_str = re_match_tz.group(2)
                timezone_str = timezone_str.replace("'", "")
                logging.debug('datetime_str: %s' % datetime_str)
                logging.debug('timezone_str: %s' % timezone_str)

                try:
                    dt = datetime.strptime(datetime_str + timezone_str,
                                           "%Y%m%d%H%M%S%z")
                    found_match = True
                except ValueError:
                    logging.debug('Unable to parse aware datetime from '
                                  '[%s]' % field)

                if not found_match:
                    try:
                        dt = datetime.strptime(datetime_str, "%Y%m%d%H%M%S")
                        found_match = True
                    except ValueError:
                        logging.debug('Unable to parse naive datetime from '
                                      '[%s]' % field)

            # Try matching another pattern.
            date_pattern_no_tz = re.compile('D:(\d{14,14})Z')
            re_match = date_pattern_no_tz.search(k)
            if re_match:
                try:
                    dt = datetime.strptime(re_match.group(1), '%Y%m%d%H%M%S')
                    found_match = True
                except ValueError:
                    logging.debug('Unable to parse datetime from '
                                  'metadata field [%s]' % field)
                    continue

            if found_match:
                results.append({'value': dt,
                                'source': field,
                                'weight': 1})
                logging.debug('Extracted date/time from pdf metadata field '
                              '"{}": "{}"'.format(field, dt))

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

        # TODO: Fix conditional always evaluates to True ..
        # if matches == 0:
        if True:
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
