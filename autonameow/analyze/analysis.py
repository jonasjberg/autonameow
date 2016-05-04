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
        dt_list = self.file_object.get_datetime_list()

        print('All date/time information for file:')
        print('\"%s\"' % str(self.file_object.path))
        FORMAT = '%-20.20s : %-s'
        print(FORMAT % ("Datetime", "Value"))
        # print('dt_list type : %s' % type(dt_list))

        for dt_dict in dt_list:
            # print('[dt_dict] %-15.15s   : %-80.80s' % (type(dt_dict), str(dt_dict)))
            if type(dt_dict) is not dict:
                logging.error('datetime list contains unexpected type %s' % type(dt_dict))
                continue

            for dt_key, dt_value in dt_dict.iteritems():
                # print('[dt_key] %-15.15s   : %-80.80s' % (type(dt_key), str(dt_key)))
                # print('[dt_value] %-15.15s : %-80.80s' % (type(dt_value), str(dt_value)))
                # valuestr = v.isoformat()
                valuestr = dt_value.strftime("%Y-%m-%d %H:%M:%S")
                print(FORMAT % (dt_key, valuestr))

    def print_oldest_datetime(self):
        oldest_dt = self.file_object.get_oldest_datetime()
        # print('type(oldest_dt): %s' % type(oldest_dt))
        print('Oldest date/time information for file:')
        print('\"%s\"' % str(self.file_object.path))
        FORMAT = '%-20.20s : %-s'
        print(FORMAT % ("Datetime", "Value"))
        # valuestr = oldest_dt.strftime("%Y-%m-%d %H:%M:%S")
        # print(FORMAT % ('oldest', valuestr))
        print(FORMAT % ('oldest', str(oldest_dt)))

    def prefix_date_to_filename(self):
        fo = self.file_object

        datetime = fo.get_oldest_datetime()

        ext = fo.extension
        fn_noext = fo.basename_no_ext
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


