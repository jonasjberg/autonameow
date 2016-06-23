# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

import io
import logging

from unidecode import unidecode

from analyze.analyze_abstract import AbstractAnalyzer
from util import dateandtime


class TextAnalyzer(AbstractAnalyzer):
    def __init__(self, file_object, filters):
        super(TextAnalyzer, self).__init__(file_object, filters)

        # Extract the textual contents.
        logging.debug('Extracting text contents ..')
        self.text_contents = self._extract_text_content()

    def get_author(self):
        # TODO: Implement.
        pass

    def get_title(self):
        # TODO: Implement.
        pass

    def get_datetime(self):
        result = []
        if self.text_contents:
            text_timestamps = self._get_datetime_from_text()
            if text_timestamps:
                # self.filter_datetime(text_timestamps)
                result.append(text_timestamps)

        return result

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

    def _get_datetime_from_text(self):
        """
        Extracts date and time information from textual contents.
        :return: a list of dictionaries on the form:
                 [ { 'datetime': datetime.datetime(2016, 6, 5, 16, ..),
                     'source' : "Create date",
                     'weight'  : 1
                   }, .. ]
        """
        results = []
        text = self.text_contents

        dt_regex = dateandtime.regex_search_str(text)
        if dt_regex:
            for dt in dt_regex:
                results.append({'datetime': dt,
                                'source': 'regex_search',
                                'weight': 0.25})
        else:
            logging.warning('Unable to extract date/time-information '
                            'from text file contents using regex search.')

        if type(text) == list:
            text = ' '.join(text)
        dt_brute = dateandtime.bruteforce_str(text)
        if dt_brute:
            for dt in dt_brute:
                results.append({'datetime': dt,
                                'source': 'bruteforce_search',
                                'weight': 0.1})
        else:
            logging.warning('Unable to extract date/time-information '
                            'from text file contents using brute force search.')

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
