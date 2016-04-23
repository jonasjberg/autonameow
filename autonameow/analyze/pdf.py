import logging
import pprint

from datetime import datetime

import re

from analyze.common import AnalyzerBase

import pyPdf
from pyPdf import PdfFileReader

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
                logging.warning(
                    'Got Null result from metadata field [%s]' % field)
                continue

            # Expected date format:     D:20121225235237+05'30'
            pdf_metadata_date_pattern = re.compile('.*D:(\d{14,14}).*')
            re_search = pdf_metadata_date_pattern.search(k)
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

            results[field] = dt

        return results

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
            pdfFile = PdfFileReader(file(filename, 'rb'))
            pdfMetadata = pdfFile.getDocumentInfo()
            print('METADATA TYPE: %s' % str(type(pdfMetadata)))
            self.title = pdfMetadata.title
            self.author = pdfMetadata.author

        except Exception:
            logging.error("PDF metadata extraction error")

        if pdfMetadata:
            # Remove leading '/' from all entries and save to new dict 'result'.
            for entry in pdfMetadata:
                value = pdfMetadata[entry]
                key = entry.lstrip('\/')
                result[key] = value

        return result

    # import warnings,sys,os,string
    # from pyPdf import PdfFileWriter, PdfFileReader
    # # warnings.filterwarnings("ignore")
    #
    #
    #
    # for root, dir, files in os.walk(str(sys.argv[1])):
    #     for fp in files:
    #         if ".pdf" in fp:
    #             fn = root+"/"+fp
    #             try:
    #                 pdfFile = PdfFileReader(file(fn,"rb"))
    #                 title = pdfFile.getDocumentInfo().title.upper()
    #                 author = pdfFile.getDocumentInfo().author.upper()
    #                 pages = pdfFile.getNumPages()
    #
    #                 if (pages > 5) and ("DR EVIL" in author):
    #                     resultStr = "Matched:"+str(fp)+"-"+str(pages)

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

        # Use only the first and second page of content.
        if pdff.getNumPages() > 1:
            pdf_text = pdff.pages[0].extractText() + pdff.pages[1].extractText()
        elif pdff.getNumPages() == 1:
            pdf_text = pdff.pages[0].extractText()
        else:
            logging.error('Unable to determine number of pages of PDF.')
            return False

        if len(pdf_text) == 0:
            logging.warning('Textual content of PDF is empty.')
            return False

        if pdf_text:
            logging.debug('Extracted [%s] lines of textual content' % len(pdf_text))

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
