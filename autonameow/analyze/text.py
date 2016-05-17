# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

import io
import logging

from unidecode import unidecode

from analyze.common import AnalyzerBase
from util import dateandtime


class TextAnalyzer(AnalyzerBase):
    def __init__(self, file_object, filters):
        self.file_object = file_object
        self.filters = filters

        self.author = None
        self.title = None
        self.publisher = None

    def run(self):
        """
        Run this analyzer.
        This method is common to all analyzers.
        :return:
        """

        text_contents = self.extract_text_content()
        if text_contents:
            # print(text_contents)
            text_timestamps = self.get_datetime_from_text(text_contents)
            if text_timestamps:
                self.add_datetime(text_timestamps)

    def extract_text_content(self):
        """
        Extract the plain text contents of a text file as strings.
        :return: False or text content as strings
        """

        content = self.get_file_lines()
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
            logging.debug('Extracted [%s] words (??) of content' % len(content))
            return decoded_content
        else:
            logging.warn('Unable to extract PDF contents.')
            return None

    def get_datetime_from_text(self, text):
        if text is None:
            logging.warning('Got NULL argument')
            return None

        if type(text) is not str:
            logging.warning('Got unexpected type {} (expected '
                            'string)'.format(type(text)))
            return None

        text = text.lower()

        # Create empty dictionary to hold all results.
        results = {}
        result_index = 0

        if text.find('gmail'):
            logging.debug('Text contains "gmail", might be a Gmail?')
            dt_gmail_list = dateandtime.search_gmail(text, 'text_contents_gmail_')

        regex_match = 0
        dt_regex_list = dateandtime.regex_search_str(text, 'text_contents_regex_{}'.format(regex_match))
        # dt_regex = None
        if dt_regex_list is not None:
            for new_key, new_value in dt_regex_list.iteritems():
                # TODO: Add to results even though it will result in duplicate
                #       entries? Should duplicate entry count indicate quality?
                # if new_value not in results.values():
                if True:
                    # print('{} is not in {}'.format(new_value, 'results.value()'))
                    k = '{0}_{1:03d}'.format('text_content', result_index)
                    results[k] = new_value
                    result_index += 1

        match = 0
        result_list = []
        for line in text:
            #text_split = line.split('\n')
            # for t in text_split:
            #     dt = dateandtime.bruteforce_str(t, 'pdf_contents_{}'.format(match))
            #     if dt is not None:
            #         logging.info('Added result from contents: {0}'.format(dt))
            #         result_list.append(dt)
            #         match += 1

            text_split = line.split()
            for t in text_split:
                dt = dateandtime.bruteforce_str(t, 'text_content_{}'.format(match))
                if dt is not None:
                    # logging.debug('Added result from contents: {0}'.format(dt))
                    result_list.append(dt)
                    match += 1

            for result in result_list:
                # print('result {} : {}'.format(type(result), result))
                for new_key, new_value in result.iteritems():
                    if new_value not in results.values():
                        # print('{} is not in {}'.format(new_value, 'results.value()'))
                        k = '{0}_{1:03d}'.format('text_content', result_index)
                        results[k] = new_value
                        result_index += 1

        return results

    def get_file_lines(self):
        fn = self.file_object.path
        with io.open(fn, 'r', encoding='utf8') as f:
            contents = f.read().split('\n')

            if contents:
                logging.info('Successfully read %d lines from \"%s\"'
                             % (len(contents), str(fn)))
                return contents
            else:
                logging.error("Got empty file \"%s\"" % fn)
                return None
