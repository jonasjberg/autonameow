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

    def print_datetime(self):
        datetime = self.get_datetime()

        FORMAT = '%-20.20s : %-s'
        print('')
        print(FORMAT % ("Datetime", "Value"))
        for entry in datetime:
            value = datetime[entry]
            # print('type(value): ' + str(type(value)))
            valuestr = value.isoformat()
            print(FORMAT % (entry, valuestr))

    def run(self):
        self.analyzer.run()

        self.print_datetime()

