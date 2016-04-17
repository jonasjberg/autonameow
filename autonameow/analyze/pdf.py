import pprint

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
        if self.pdf_metadata is None:
            self.pdf_metadata = self.extract_pdf_metadata()


        self.printMeta()
        print('--------------------------------------------------------------')

        datetime = self.get_datetime()
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(datetime)


    # TODO: FIX THIS. Returns nothing as-is.
    def get_datetime(self):
        parser = DateParse()

        DATE_TAG_FIELDS = ['ModDate', 'CreationDate']

        results = {}
        for field in DATE_TAG_FIELDS:
            date = time = None
            try:
                f = self.pdf_metadata[field]
                #date, time = self.pdf_metadata[field].split()
            except KeyError:
                print('KeyError for key [{}]'.format(field))
                pass

            f = f.lstrip('D:')
            clean_date = parser.date(f[:8])
            clean_time = parser.time(f[8:])

            if clean_date and clean_time:
                results[field] = (clean_date, clean_time)
            elif clean_date:
                results[field] = (clean_date, None)
            elif clean_time:
                results[field] = (None, clean_time)

        return results


    def extract_pdf_metadata(self):
        # Create empty dictionary to store PDF metadata "key:value"-pairs in.
        result = {}

        # Extract PDF metadata using PyPdf, nicked from Violent Python.
        try:
            filename = self.fileObject.get_path()
            pdfFile = PdfFileReader(file(filename, 'rb'))
            pdfMetadata = pdfFile.getDocumentInfo()

        except Exception:
            print("PDF metadata extraction error")

        if pdfMetadata:
            # Remove leading '/' from all entries and save to new dict 'result'.
            for entry in pdfMetadata:
                value = pdfMetadata[entry]
                key = entry.lstrip('\/')
                result[key] = value

        return result


    def printMeta(self):
        FORMAT='%-20.20s : %-s'
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