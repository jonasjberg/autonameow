# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

import io
import logging

from unidecode import unidecode

from core.analyze.analyze_abstract import AbstractAnalyzer
from core.util import dateandtime


class TextAnalyzer(AbstractAnalyzer):
    # @Overrides attribute in AbstractAnalyzer
    run_queue_priority = 0.5

    def __init__(self, file_object):
        super(TextAnalyzer, self).__init__(file_object)
        self.applies_to_mime = ['txt', 'md']

        self.text = None

    # @Overrides method in AbstractAnalyzer
    def run(self):
        # Extract the textual contents.
        logging.debug('Extracting text contents ..')
        self.text = self._extract_text_content()

    # @Overrides method in AbstractAnalyzer
    def get_author(self):
        # TODO: Implement.
        pass

    # @Overrides method in AbstractAnalyzer
    def get_title(self):
        # TODO: Implement.
        pass

    # @Overrides method in AbstractAnalyzer
    def get_datetime(self):
        result = []
        if self.text:
            text_timestamps = self._get_datetime_from_text()
            if text_timestamps:
                result += text_timestamps

        return result

    # @Overrides method in AbstractAnalyzer
    def get_tags(self):
        # TODO: Implement.
        pass

    def _extract_text_content(self):
        """
        Extract the plain text contents of a text file as strings.
        :return: False or text content as strings
        """
        content = self._get_file_lines()
        # Fix encoding and replace Swedish characters.
        # content = content.encode('utf-8', 'ignore')
        # content = content.replace('\xc3\xb6', 'o').replace('\xc3\xa4', 'a').replace('\xc3\xa5', 'a')

        decoded_content = []
        for line in content:
            # Collapse whitespace.
            # '\xa0' is non-breaking space in Latin1 (ISO 8859-1), also chr(160).
            line = unidecode(line)
            line = " ".join(line.replace("\xa0", " ").strip().split())
            decoded_content.append(line)

        if decoded_content:
            # TODO: Determine what gets extracted **REALLY** ..
            logging.debug('Extracted {} words/lines (??) of '
                          'content'.format(len(content)))
            return decoded_content
        else:
            logging.warn('Unable to extract text contents.')
            return None

    def _is_gmail(self):
        text = self.text
        if type(text) is list:
            text = ' '.join(text)

        if text.lower().find('gmail'):
            logging.debug('Text might be a Gmail (contains "gmail")')
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
            logging.debug('Unable to extract date/time-information '
                          'from text file contents using regex search.')

        if type(text) == list:
            text = ' '.join(text)

        matches_brute = 0
        logging.debug('Try getting datetime from text split by newlines')
        for t in text.split('\n'):
            dt_brute = dateandtime.bruteforce_str(t)
            if dt_brute:
                for dt in dt_brute:
                    matches_brute += 1
                    results.append({'value': dt,
                                    'source': 'bruteforce_search',
                                    'weight': 0.1})
        if matches_brute == 0:
            logging.debug('Unable to extract date/time-information '
                          'from text file contents using brute force search.')
        else:
            logging.debug('Brute force search of text file contents for '
                          'date/time-information returned {} '
                          'results.'.format(matches_brute))

        return results

    def _get_file_lines(self):
        fn = self.file_object.path
        with io.open(fn, 'r', encoding='utf8') as f:
            contents = f.read().split('\n')
            if contents:
                logging.info('Successfully read {} lines from '
                             '"{}"'.format(len(contents), str(fn)))
                return contents
            else:
                logging.error('Got empty file "{}"'.format(fn))
                return None
