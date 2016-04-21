import logging

from analyze.common import AnalyzerBase
from analyze.image import ImageAnalyzer
from analyze.pdf import PdfAnalyzer


class Analysis(object):
    """
    Main interface to all file analyzers.
    """

    analyzer = None
    best_datetime = None
    best_name = None

    def __init__(self, fileObject):
        self.fileObject = fileObject

        # Select analyzer based on detected file type.
        if self.fileObject.get_type() == "JPEG":
            logging.debug('File is of type [JPEG]')
            self.analyzer = ImageAnalyzer(self.fileObject)

        elif self.fileObject.get_type() == "PDF":
            logging.debug('File is of type [PDF]')
            self.analyzer = PdfAnalyzer(self.fileObject)

        else:
            # Create a basic analyzer, common to all file types.
            logging.debug('File is of type [unknown]')
            self.analyzer = AnalyzerBase(self.fileObject)

    def get_datetime(self):
        return self.analyzer.get_datetime()

    def run(self):
        self.analyzer.run()

