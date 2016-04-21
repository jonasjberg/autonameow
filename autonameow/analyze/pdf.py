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

    def run(self):
        """
        Run this analyzer.
        This method is common to all analyzers.
        :return:
        """
        if self.pdf_metadata is None:
            self.pdf_metadata = self.extract_pdf_metadata()

        metadata_datetime = self.get_metadata_datetime()
        if metadata_datetime:
            self.fileObject.add_datetime(metadata_datetime)
            # print('--------------------------------------------------------------')
            # self.printMeta()
            # print('--------------------------------------------------------------')

            # datetime = self.get_datetime()
            # pp = pprint.PrettyPrinter(indent=4)
            # pp.pprint(datetime)

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

        except Exception:
            logging.error("PDF metadata extraction error")

        if pdfMetadata:
            # Remove leading '/' from all entries and save to new dict 'result'.
            for entry in pdfMetadata:
                value = pdfMetadata[entry]
                key = entry.lstrip('\/')
                result[key] = value

        return result

    def printMeta(self):
        FORMAT = '%-20.20s : %-s'
        print('')
        print(FORMAT % ("Metadata field", "Value"))
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(pdfMetadata)
        for entry in self.pdf_metadata:
            # print([{}]  []) + entry + ':' + pdfMetadata[entry]
            value = self.pdf_metadata[entry]
            print(FORMAT % (entry, value))


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
