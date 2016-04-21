import logging

from analyze.common import AnalyzerBase
from analyze.image import ImageAnalyzer
from analyze.pdf import PdfAnalyzer


class Analysis(object):
    """
    Main interface to all file analyzers.
    """

    analyzer = None

    def __init__(self, fileObject):
        self.fileObject = fileObject

        # Select analyzer based on detected file type.
        if file.get_type() == "JPEG":
            logging.debug('File is of type [JPEG]')
            self.analyzer = ImageAnalyzer(file)
        elif file.get_type() == "PDF":
            logging.debug('File is of type [PDF]')
            self.analyzer = PdfAnalyzer(file)
        else:
            # Create a basic analyzer, common to all file types.
            logging.debug('File is of type [unknown]')
            self.analyzer = AnalyzerBase(file)

    def get_datetime(self):
        return self.analyzer.get_datetime()

    def run(self):
        self.analyzer.run()

