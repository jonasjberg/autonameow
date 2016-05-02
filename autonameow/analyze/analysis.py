# -*- coding: utf-8 -*-

# autonameow
# ~~~~~~~~~~
# written by Jonas Sjöberg
# jomeganas@gmail.com
# ____________________________________________________________________________

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

    def print_all_datetime_info(self):
        datetime = self.fileObject.get_datetime_list()

        fn = self.fileObject.path
        print('All date/time information for file:')
        print('\"%s\"' % str(fn))
        FORMAT = '%-20.20s : %-s'
        print(FORMAT % ("Datetime", "Value"))
        for l in datetime:
            for entry in l:
                value = l[entry]
                # print('type(value): ' + str(type(value)))
                # valuestr = value.isoformat()
                valuestr = value.strftime("%Y-%m-%d %H:%M:%S")
                print(FORMAT % (entry, valuestr))

    def print_oldest_datetime(self):
        datetime = self.fileObject.get_oldest_datetime()
        # print('type(datetime): %s' % type(datetime))
        fn = self.fileObject.path
        print('Oldest date/time information for file:')
        print('\"%s\"' % str(fn))
        FORMAT = '%-20.20s : %-s'
        print(FORMAT % ("Datetime", "Value"))
        # valuestr = datetime.strftime("%Y-%m-%d %H:%M:%S")
        # print(FORMAT % ('oldest', valuestr))
        print(FORMAT % ('oldest', str(datetime)))

    def run(self):
        # Select analyzer based on detected file type.
        if self.fileObject.type == "JPEG":
            logging.debug('File is of type [JPEG]')
            self.analyzer = ImageAnalyzer(self.fileObject)

        elif self.fileObject.type == "PDF":
            logging.debug('File is of type [PDF]')
            self.analyzer = PdfAnalyzer(self.fileObject)

        else:
            # Create a basic analyzer, common to all file types.
            logging.debug('File is of type [unknown]')
            self.analyzer = AnalyzerBase(self.fileObject)

        # Run analyzer.
        self.analyzer.run()

        str_year = self.fileObject.get_oldest_datetime().strftime('%Y')
        str_title = self.analyzer.title
        str_author = 'author'  # self.analyzer.author
        str_publisher = 'publisher'
        new_filename = str_title + ' ' + str_author + ' ' + str_publisher + ' ' + str_year

        print('New Filename: \"%s\"' % new_filename)

        # self.print_all_datetime_info()
