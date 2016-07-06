# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

import logging
import re
import subprocess
from datetime import datetime

import PyPDF2
from PyPDF2.utils import PdfReadError
from unidecode import unidecode

from analyze.analyze_abstract import AbstractAnalyzer
from util import dateandtime


class PdfAnalyzer(AbstractAnalyzer):
    def __init__(self, file_object, filters):
        super(PdfAnalyzer, self).__init__(file_object, filters)
        self.metadata = self._extract_pdf_metadata()
        self.text = self._extract_pdf_content()

    def get_author(self):
        # TODO: Implement.
        pass

    def get_title(self):
        # TODO: Implement.
        pass

    def get_datetime(self):
        results = []

        metadata_datetime = self._get_metadata_datetime()
        if metadata_datetime:
            # self.filter_datetime(metadata_datetime)
            results += metadata_datetime

        if self.text:
            text_timestamps = self._get_datetime_from_text()
            if text_timestamps:
                # self.filter_datetime(text_timestamps)
                results += text_timestamps

        return results

    def _get_metadata_datetime(self):
        """
        Extract date and time information from pdf metadata.
        :return: dict of datetime-objects
        """

        DATE_TAG_FIELDS = ['ModDate', 'CreationDate']

        results = []
        for field in DATE_TAG_FIELDS:
            date = time = k = None
            if field in self.metadata:
                try:
                    k = self.metadata[field]
                    k = k.strip()
                    # date, time = self.pdf_metadata[field].split()
                except KeyError:
                    logging.error('KeyError for key [{}]'.format(field))
                    pass

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
                results.append({'datetime': dt,
                                'source': field,
                                'weight': 1})
                logging.debug('Extracted date/time from pdf metadata field '
                              '"{}": "{}"'.format(field, dt))

        return results

    def _extract_xmp_metadata(self):
        # TODO: This is currently completely unused! Remove or implement.
        #       https://pythonhosted.org/PyPDF2/XmpInformation.html
        pass

    def _extract_pdf_metadata(self):
        """
        Extract metadata from a PDF document using "pyPdf".
        :return: dict of PDF metadata
        """
        # Create empty dictionary to store PDF metadata "key:value"-pairs in.
        result = {}
        pdf_metadata = None
        filename = self.file_object.path

        # Extract PDF metadata using PyPdf, nicked from Violent Python.
        try:
            pdff = PyPDF2.PdfFileReader(file(filename, 'rb'))
            pdf_metadata = pdff.getDocumentInfo()
            # TODO: These below variables are unused! Remove or implement.
            # self.title = pdf_metadata.title
            # self.author = pdf_metadata.author
        except Exception:
            logging.error("PDF metadata extraction error")

        if pdf_metadata:
            # Remove leading '/' from all entries and save to new dict 'result'.
            for entry in pdf_metadata:
                value = pdf_metadata[entry]
                key = entry.lstrip('\/')
                result[key] = value

        return result

    def _extract_pdf_content(self):
        """
        Extract the plain text contents of a PDF document.
        :return: False or PDF content as strings
        """
        # TODO: Check this
        pdf_text = self._extract_pdf_content_with_pypdf()
        if pdf_text:
            logging.debug('Extracted ')
            return pdf_text
        else:
            pdf_text = self._extract_pdf_content_with_pdftotext()
            if pdf_text:
                return pdf_text
            else:
                return False

    def _extract_pdf_content_with_pypdf(self):
        """
        Extract the plain text contents of a PDF document using PyPDF2.
        :return: False or PDF content as strings
        """
        try:
            filename = self.file_object.path
            pdff = PyPDF2.PdfFileReader(open(filename, 'rb'))
        except Exception:
            logging.error('Unable to read PDF file content.')
            return False

        try:
            number_of_pages = pdff.getNumPages()
        except PdfReadError:
            # NOTE: This now wholly determines whether a pdf doucment is
            #       readable or not. Possible to not getNumPages but still be
            #       able to read the text?
            logging.error('PDF document might be encrypted with restrictions '
                          'preventing reading.')
            return False
        else:
            logging.debug('PDF document has # pages: {}'.format(number_of_pages))

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

    def _extract_pdf_content_with_pdftotext(self):
        """
        Extract the plain text contents of a PDF document using pdftotext.
        :return: False or PDF content as strings
        """
        path = self.file_object.path
        try:
            pipe = subprocess.Popen(["pdftotext", path, "-"], shell=False,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT)
        except ValueError:
            logging.warning('"subprocess.Popen" was called with invalid '
                            'arguments.')
            return False

        stdout, stderr = pipe.communicate()
        if pipe.returncode != 0:
            return False
        elif pipe.returncode == 0:
            return stdout

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
                 [ { 'datetime': datetime.datetime(2016, 6, 5, 16, ..),
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
                    results.append({'datetime': e,
                                    'source': 'text_content_regex',
                                    'weight': 0.25})
            else:
                results.append({'datetime': dt_regex,
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
                    for e in dt_regex:
                        results.append({'datetime': e,
                                        'source': 'text_content_brute',
                                        'weight': 0.1})
                else:
                    results.append({'datetime': dt_brute,
                                    'source': 'text_content_brute',
                                    'weight': 0.1})

        # if matches == 0:
        if True:
            logging.debug('No matches. Trying with text split by whitespace')
            text_split = text.split()
            for t in text_split:
                dt_brute = dateandtime.bruteforce_str(t)
                if dt_brute:
                    matches += 1
                    if isinstance(dt_brute, list):
                        for e in dt_regex:
                            results.append({'datetime': e,
                                            'source': 'text_content_brute',
                                            'weight': 0.1})
                    else:
                        results.append({'datetime': dt_brute,
                                        'source': 'text_content_brute',
                                        'weight': 0.1})

        return results
