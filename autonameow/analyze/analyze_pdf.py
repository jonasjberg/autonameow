# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

import logging
import re
from datetime import datetime

import PyPDF2
from unidecode import unidecode

from analyze.analyze_abstract import AbstractAnalyzer
from util import dateandtime


class PdfAnalyzer(AbstractAnalyzer):
    def __init__(self, file_object, filters):
        super(PdfAnalyzer, self).__init__(file_object, filters)
        self.pdf_metadata = self.extract_pdf_metadata()

    def get_author(self):
        # TODO: Implement.
        pass

    def get_title(self):
        # TODO: Implement.
        pass

    def get_datetime(self):
        result = []

        metadata_datetime = self.get_metadata_datetime()
        if metadata_datetime:
            # self.filter_datetime(metadata_datetime)
            result.append(metadata_datetime)

        pdf_text = self.extract_pdf_content()
        if pdf_text:
            text_timestamps = self.get_datetime_from_text(pdf_text)
            if text_timestamps:
                # self.filter_datetime(text_timestamps)
                result.append(text_timestamps)

        return result

    def get_metadata_datetime(self):
        """
        Extract date and time information from pdf metadata.
        :return: dict of datetime-objects
        """

        DATE_TAG_FIELDS = ['ModDate', 'CreationDate']

        results = {}
        for field in DATE_TAG_FIELDS:
            date = time = k = None
            if field in self.pdf_metadata:
                try:
                    k = self.pdf_metadata[field]
                    # date, time = self.pdf_metadata[field].split()
                except KeyError:
                    logging.error('KeyError for key [{}]'.format(field))
                    pass

            k = k.strip()
            if k is None:
                logging.warning('Null value in metadata field [%s]' % field)
                continue

            found_match = False
            dt = None
            # Expected date format:             D:20121225235237+05'30'
            #
            # Regex search matches two groups:  D: 20121225235237 +05'30'
            #                                      ^            ^ ^     ^
            #                                      '------------' '-----'
            #                                            #1         #2
            # Which are extracted separately.
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
            date_pattern_no_tz = re.compile('.*D:(\d{14,14})Z.*')
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
                key = '{0}_{1}'.format('pdf_metadata', field)
                logging.debug('Extracted date/time from pdf metadata: '
                              'results[%s] = [%s]' % (key, dt))
                results[key] = dt

        return results

    def extract_xmp_metadata(self):
        # TODO: ..
        pass

    def extract_pdf_metadata(self):
        """
        Extract metadata from a PDF document using "pyPdf".
        :return: dict of PDF metadata
        """
        # Create empty dictionary to store PDF metadata "key:value"-pairs in.
        result = {}
        pdf_metadata = None

        # Extract PDF metadata using PyPdf, nicked from Violent Python.
        try:
            filename = self.file_object.path
            pdff = PyPDF2.PdfFileReader(file(filename, 'rb'))
            pdf_metadata = pdff.getDocumentInfo()
            self.title = pdf_metadata.title
            self.author = pdf_metadata.author
        except Exception:
            logging.error("PDF metadata extraction error")

        if pdf_metadata:
            # Remove leading '/' from all entries and save to new dict 'result'.
            for entry in pdf_metadata:
                value = pdf_metadata[entry]
                key = entry.lstrip('\/')
                result[key] = value

        return result

    def extract_pdf_content(self):
        """
        Extract the plain text contents of a PDF document as strings.
        :return: False or PDF content as strings
        """

        # Extract PDF content using PyPDF2.
        try:
            filename = self.file_object.path
            pdff = PyPDF2.PdfFileReader(open(filename, 'rb'))
        except Exception:
            logging.error('Unable to read PDF file content.')
            return False

        number_of_pages = pdff.getNumPages()
        logging.debug('Number of pages: %d', number_of_pages)

        # # Use only the first and second page of content.
        # if pdff.getNumPages() == 1:
        #     pdf_text = pdff.pages[0].extractText()
        # elif pdff.getNumPages() > 1:
        #     pdf_text = pdff.pages[0].extractText() + pdff.pages[1].extractText()
        # else:
        #     logging.error('Unable to determine number of pages of PDF.')
        #     return False

        # Start by extracting a limited range of pages.
        # Maybe relevant info is more likely to be on the front page, or at
        # least in the first few pages?
        logging.debug('Extracting page #0')
        content = pdff.pages[0].extractText()
        if len(content) == 0:
            logging.debug('Textual content of page #0 is empty.')
            pass

        # Collect more until a preset limit is reached.
        logging.debug('Keep extracting pages from pdf document ..')
        for i in range(1, number_of_pages):
            # Extract text from page and add to content.
            # logging.debug('Extracting page #%s' % i)
            content += pdff.getPage(i).extractText() + '\n'

            # Cancel extraction at some arbitrary limit value.
            if len(content) > 50000:
                logging.debug('Extraction hit content size limit.')
                break

        # Fix encoding and replace Swedish characters.
        # content = content.encode('utf-8', 'ignore')
        # content = content.replace('\xc3\xb6', 'o').replace('\xc3\xa4', 'a').replace('\xc3\xa5', 'a')

        content = unidecode(content)
        # Collapse whitespace.
        # '\xa0' is non-breaking space in Latin1 (ISO 8859-1), also chr(160).
        content = " ".join(content.replace("\xa0", " ").strip().split())

        if content:
            # TODO: Determine what gets extracted **REALLY** ..
            logging.debug('Extracted [%s] words (??) of content' % len(content))
            return content
        else:
            logging.warn('Unable to extract PDF contents.')
            return None

    def get_datetime_from_text(self, text):
        # TODO: This redirection is very ugly.
        dt = dateandtime.get_datetime_from_text(text, 'text')

        if not dt:
            return None

        results = {}

        i = 0
        if 'text_contents_regex' in dt:
            print('dt has key text_contents_regex')
            for entry in dt['text_contents_regex']:
                if not entry:
                    continue
                if type(entry) is list:
                    for e in entry:
                        new_key = '{0}_{1:06d}'.format('text_contents', i)
                        results[new_key] = e
                        i += 1
                elif type(entry) is dict:
                    for k, v in entry.iteritems():
                        new_key = '{0}_{1:06d}'.format('text_contents', i)
                        results[new_key] = v
                        i += 1
        else:
            print('dt DOES NOT have key test_contents_regex')

        if 'text_contents_brute' in dt:
            print('dt has key text_contents_brute')
            for entry in dt['text_contents_brute']:
                if not entry:
                    continue
                if type(entry) is list:
                    for e in entry:
                        new_key = '{0}_{1:06d}'.format('text_contents', i)
                        results[new_key] = e
                        i += 1
                elif type(entry) is dict:
                    for k, v in entry.iteritems():
                        new_key = '{0}_{1:06d}'.format('text_contents', i)
                        results[new_key] = v
                        i += 1

        else:
            print('dt DOES NOT have key test_contents_brute')

        return results
