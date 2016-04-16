from analyze.analyzer import AnalyzerBase


class PdfAnalyzer(AnalyzerBase):

    def __init__(self, fileObject):
        self.fileObject = fileObject


    def run(self):
        # TODO: Run analysis specific to PDF documents.
        pass

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