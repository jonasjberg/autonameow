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
import subprocess
from datetime import datetime

import PyPDF2
from PyPDF2.utils import PdfReadError

from core.analyze.analyze_abstract import AbstractAnalyzer
from core.util import dateandtime
from core.util import textutils
from core.util import wrap_exiftool


class PdfAnalyzer(AbstractAnalyzer):
    # @Overrides attribute in AbstractAnalyzer
    run_queue_priority = 1

    def __init__(self, file_object):
        super(PdfAnalyzer, self).__init__(file_object)
        self.applies_to_mime = 'pdf'

        self.metadata = None
        self.metadata_exiftool = None
        self.text = None

    # @Overrides method in AbstractAnalyzer
    def run(self):
        self.metadata = self._extract_pdf_metadata_with_pypdf()
        self.metadata_exiftool = self._extract_pdf_metadata_with_exiftool()

        self.text = self._extract_pdf_content()

    # @Overrides method in AbstractAnalyzer
    def get_author(self):
        results = []

        field = 'Author'
        if field in self.metadata:
            value = self.metadata[field]
            results.append({'value': value,
                            'source': field,
                            'weight': 1})
            logging.debug('Extracted author from pdf metadata field '
                          '"{}": "{}"'.format(field, value))

        field = 'PDF:Author'
        if field in self.metadata_exiftool:
            value = self.metadata_exiftool[field]
            results.append({'value': value,
                            'source': field,
                            'weight': 1})
            logging.debug('Extracted author from (exiftool) pdf metadata field '
                          '"{}": "{}"'.format(field, value))
        return results

    # @Overrides method in AbstractAnalyzer
    def get_title(self):
        results = []

        field = 'Title'
        if field in self.metadata:
            value = self.metadata[field]
            results.append({'value': value,
                            'source': field,
                            'weight': 1})
            logging.debug('Extracted title from pdf metadata field '
                          '"{}": "{}"'.format(field, value))

        field = 'PDF:Title'
        if field in self.metadata_exiftool:
            value = self.metadata_exiftool[field]
            results.append({'value': value,
                            'source': field,
                            'weight': 1})
            logging.debug('Extracted title from (exiftool) pdf metadata field '
                          '"{}": "{}"'.format(field, value))
        return results

    # @Overrides method in AbstractAnalyzer
    def get_datetime(self):
        results = []

        metadata_datetime = self._get_metadata_datetime()
        if metadata_datetime:
            results += metadata_datetime

        if self.text:
            text_timestamps = self._get_datetime_from_text()
            if text_timestamps:
                results += text_timestamps

        return results

    # @Overrides method in AbstractAnalyzer
    def get_tags(self):
        # TODO: Implement.
        pass

    # @Overrides method in AbstractAnalyzer
    def get_publisher(self):
        results = []

        field = 'PDF:EBX_PUBLISHER'
        if field in self.metadata:
            value = self.metadata[field]
            results.append({'value': value,
                            'source': field,
                            'weight': 1})
            logging.debug('Extracted publisher from pdf metadata field '
                          '"{}": "{}"'.format(field, value))

        field = 'PDF:EBX_PUBLISHER'
        if field in self.metadata_exiftool:
            value = self.metadata_exiftool[field]
            results.append({'value': value,
                            'source': field,
                            'weight': 1})
            logging.debug('Extracted publisher from (exiftool) pdf metadata field '
                          '"{}": "{}"'.format(field, value))
        return results

    def _get_metadata_datetime(self):
        """
        Extract date and time information from pdf metadata.
        :return: dict of datetime-objects
        """

        DATE_TAG_FIELDS = ['ModDate', 'CreationDate', 'ModDate']

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
                results.append({'value': dt,
                                'source': field,
                                'weight': 1})
                logging.debug('Extracted date/time from pdf metadata field '
                              '"{}": "{}"'.format(field, dt))

        return results

    def _extract_xmp_metadata(self):
        # TODO: This is currently completely unused! Remove or implement.
        #       https://pythonhosted.org/PyPDF2/XmpInformation.html
        pass

    def _extract_pdf_metadata_with_pypdf(self):
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
            pdff = PyPDF2.PdfFileReader(filename, 'rb')
            pdf_metadata = pdff.getDocumentInfo()
            # TODO: These below variables are unused! Remove or implement.
            # self.title = pdf_metadata.title
            # self.author = pdf_metadata.author
        except Exception as e:
            logging.error('PDF metadata extraction error: "{}"'.format(e))

        if pdf_metadata:
            # Remove leading '/' from all entries and save to new dict 'result'.
            for entry in pdf_metadata:
                value = pdf_metadata[entry]
                key = entry.lstrip('\/')
                result[key] = value

        return result

    def _extract_pdf_metadata_with_exiftool(self):
        with wrap_exiftool.ExifTool() as et:
            metadata = et.get_metadata(self.file_object.path)
        return metadata

    def _extract_pdf_content(self):
        """
        Extract the plain text contents of a PDF document.
        :return: False or PDF content as strings
        """
        pdf_text = None
        i = 1
        text_extractors = [extract_pdf_content_with_pypdf,
                           extract_pdf_content_with_pdftotext]
        for extractor in text_extractors:
            logging.debug('Running pdf text extractor [{:<2}/{:<2}] '
                          '..'.format(i, len(text_extractors)))
            pdf_text = extractor(self.file_object.path)
            if pdf_text and len(pdf_text) > 1:
                logging.debug('Extracted text with: {}'.format(extractor.__name__))
                # Post-process text extracted from a pdf document.
                pdf_text = textutils.sanitize_text(pdf_text)
                break

        if pdf_text:
            logging.debug('Extracted [{}] bytes of text'.format(len(pdf_text)))
            return pdf_text
        else:
            logging.info('Unable to extract textual content from pdf ..')
            return None

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


def extract_pdf_content_with_pdftotext(pdf_file):
    """
    Extract the plain text contents of a PDF document using pdftotext.

    Returns:
        False or PDF content as string
    """
    try:
        pipe = subprocess.Popen(['pdftotext', '-nopgbrk', '-layout',
                                 '-enc', 'UTF-8', pdf_file, '-'],
                                shell=False,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
    except ValueError:
        logging.warning(
            '"subprocess.Popen" was called with invalid arguments.')
        return False

    stdout, stderr = pipe.communicate()
    if pipe.returncode != 0:
        logging.warning('subprocess returned [{}] - STDERROR: '
                        '{}'.format(pipe.returncode, stderr))
        return False
    else:
        return stdout.decode('utf-8', errors='replace')


def extract_pdf_content_with_pypdf(pdf_file):
    """
    Extract the plain text contents of a PDF document using PyPDF2.

    Returns:
        False or PDF content as strings.
    """
    try:
        pdff = PyPDF2.PdfFileReader(open(pdf_file, 'rb'))
    except Exception:
        logging.error('Unable to read PDF file content.')
        # TODO:
        return False

    try:
        num_pages = pdff.getNumPages()
    except PdfReadError:
        # NOTE: This now wholly determines whether a pdf is readable.
        #       Possible to not getNumPages but still be able to read the text?
        logging.error('PDF document might be encrypted with restrictions '
                      'preventing reading.')
        return False
    else:
        logging.debug('PDF document has # pages: {}'.format(num_pages))

    # Start by extracting a limited range of pages.
    # TODO: Relevant info is more likely to be within some range of pages?
    logging.debug('Extracting page #1')
    content = pdff.pages[0].extractText()
    if len(content) == 0:
        logging.debug('Textual content of page #1 is empty.')
        pass

    # Collect more until a preset arbitrary limit is reached.
    for i in range(1, num_pages):
        if len(content) > 50000:
            logging.debug('Extraction hit content size limit.')
            break
        logging.debug('Extracting page {:<4} of {:<4} ..'.format(i + 1,
                                                                 num_pages))
        content += pdff.getPage(i).extractText() + '\n'

    if content:
        return content
    else:
        logging.debug('Unable to extract text with PyPDF2 ..')
        return False
