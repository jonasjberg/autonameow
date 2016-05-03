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
from util import disk


class Analysis(object):
    """
    Main interface to all file analyzers.
    """

    analyzer = None
    best_datetime = None
    best_name = None

    def __init__(self, file_object):
        self.file_object = file_object
        self.datetime_list = []

        if self.file_object is None:
            logging.critical('Got NULL file!')
            pass

    def print_all_datetime_info(self):
        datetime = self.file_object.get_datetime_list()

        print('All date/time information for file:')
        print('\"%s\"' % str(self.file_object.path))
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
        datetime = self.file_object.get_oldest_datetime()
        # print('type(datetime): %s' % type(datetime))
        print('Oldest date/time information for file:')
        print('\"%s\"' % str(self.file_object.path))
        FORMAT = '%-20.20s : %-s'
        print(FORMAT % ("Datetime", "Value"))
        # valuestr = datetime.strftime("%Y-%m-%d %H:%M:%S")
        # print(FORMAT % ('oldest', valuestr))
        print(FORMAT % ('oldest', str(datetime)))

    def prefix_date_to_filename(self):
        fo = self.file_object

        datetime = fo.get_oldest_datetime()

        ext = fo.get_file_extension(fo.path)
        fn_noext = fo.get_file_name_noext()
        fn_noext = fn_noext.replace(ext, '')

        print('%s %s.%s' % (datetime.strftime('%Y-%m-%d_%H%M%S'), fn_noext, ext))

    def run(self):
        # Create a basic analyzer, common to all file types.
        self.analyzer = AnalyzerBase(self.file_object)
        self.analyzer.run()

        # Select analyzer based on detected file type.
        if self.file_object.type == "JPEG":
            logging.debug('File is of type [JPEG]')
            self.analyzer = ImageAnalyzer(self.file_object)

        elif self.file_object.type == "PDF":
            logging.debug('File is of type [PDF]')
            self.analyzer = PdfAnalyzer(self.file_object)

        else:
            logging.debug('File is of type [unknown]')

        # Run analyzer.
        self.analyzer.run()

        #str_year = self.fileObject.get_oldest_datetime().strftime('%Y')
        #str_title = self.analyzer.title
        #str_author = 'author'  # self.analyzer.author
        #str_publisher = 'publisher'
        #new_filename = str_title + ' ' + str_author + ' ' + str_publisher + ' ' + str_year
        #print('New Filename: \"%s\"' % new_filename)

        # self.print_all_datetime_info()


