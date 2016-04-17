import pprint

from analyze.common import AnalyzerBase

import pyPdf
from pyPdf import PdfFileReader

import PyPDF2



class PdfAnalyzer(AnalyzerBase):

    def __init__(self, fileObject):
        self.fileObject = fileObject


    def run(self):
        if self.pdf_metadata is None:
            self.pdf_metadata = self.extract_pdf_metadata()


        self.printMeta()


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
            # TODO: Clean results possibly?
            return pdfMetadata
        else:
            return None


    def printMeta(self):
        FORMAT='%-20.20s : %-s'
        print('')
        print(FORMAT % ("Metadata field", "Value"))
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(pdfMetadata)
        for entry in pdfMetadata:

            # print([{}]  []) + entry + ':' + pdfMetadata[entry]
            value = pdfMetadata[entry]
            key = entry.lstrip('\/')
            print(FORMAT % (key, value))


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