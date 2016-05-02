# -*- coding: utf-8 -*-
# coding=utf-8

# autonameow
# ~~~~~~~~~~
# written by Jonas Sjöberg
# jomeganas@gmail.com
# ____________________________________________________________________________

import logging
import pprint

from datetime import datetime
from unidecode import unidecode

import re

from analyze.common import AnalyzerBase

import pyPdf
import PyPDF2

from util.fuzzy_date_parser import DateParse


class PdfAnalyzer(AnalyzerBase):
    def __init__(self, fileObject):
        self.fileObject = fileObject
        self.pdf_metadata = None

        self.author = None
        self.title = None
        self.publisher = None

    def run(self):
        """
        Run this analyzer.
        This method is common to all analyzers.
        :return:
        """

        fs_timestamps = self.get_datetime_from_filesystem()
        if fs_timestamps:
            self.fileObject.add_datetime(fs_timestamps)

        if self.pdf_metadata is None:
            self.pdf_metadata = self.extract_pdf_metadata()

        metadata_datetime = self.get_metadata_datetime()
        if metadata_datetime:
            self.fileObject.add_datetime(metadata_datetime)

        print(self.get_title())
        print(self.get_author())

        pdf_text = self.extract_pdf_content()
        if pdf_text:
            logging.debug('PDF content:')
            # logging.debug(pdf_text)
            # print(pdf_text)
            # for line in pdf_text:
            #    print(line)

    def get_metadata_datetime(self):
        """
        Extract date and time information from pdf metadata.
        :return: dict of datetime-objects
        """
        parser = DateParse()

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

            if k is None:
                logging.warning( 'Got Null result from metadata field [%s]'
                                 % field)
                continue

            print(k)
            # Expected date format:     D:20121225235237+05'30'
            pdf_metadata_date_pattern = re.compile('.*D:(\d{14,14})\+(\d{2,2})\'(\d{2,2})\'.*')
            re_search = pdf_metadata_date_pattern.search(k.strip())
            if re_search is None:
                logging.warning(
                    'Found no date/time-pattern in metadata field [%s]' % field)
                continue

            try:
                dt = datetime.strptime(re_search.group(1), "%Y%m%d%H%M%S")
            except ValueError:
                logging.warning('Unable to parse datetime from '
                                'metadata field [%s]' % field)
                continue

            logging.debug('Added to results: results[%s] = [%s]' % (field, dt))
            results[field] = dt

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

        # Extract PDF metadata using PyPdf, nicked from Violent Python.
        try:
            filename = self.fileObject.get_path()
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
            filename = self.fileObject.get_path()
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
        logging.debug('Extracting page #0')
        content = pdff.pages[0].extractText()
        if len(content) == 0:
            logging.warning('Textual content of page #0 is empty.')
            return False

        else:
            # Collect more until a preset limit is reached.
            for i in range(1, number_of_pages):
                # Extract text from page and add to content.
                logging.debug('Extracting page #%s' % i)
                content += pdff.getPage(i).extractText() + '\n'

                # Cancel extraction at some arbitrary limit value.
                if len(content) > 8000:
                    logging.debug('Extraction hit content size limit.')
                    break

        # Fix encoding and replace Swedish characters.
        #content = content.encode('utf-8', 'ignore')
        #content = content.replace('\xc3\xb6', 'o').replace('\xc3\xa4', 'a').replace( '\xc3\xa5', 'a')

        # Collapse whitespace.
        # '\xa0' is non-breaking space in Latin1 (ISO 8859-1), also chr(160).
        #content = " ".join(content.replace("\xa0", " ").strip().split())

        content = unidecode(content)

        if content:
            # TODO: Determine what gets extracted **REALLY** ..
            logging.debug('Extracted [%s] words (??) of content' % len(content))
            return content
        else:
            logging.warn('Unable to extract PDF contents.')
            return False

    def get_author(self):
        """
        Return the author of the document.
        :return:
        """
        # TODO: Handle multiple authors.
        if self.author:
            return str(self.author)
        else:
            return None

    def get_title(self):
        """
        Return the title of the document.
        :return:
        """
        if self.title:
            return str(self.title)
        else:
            return None
