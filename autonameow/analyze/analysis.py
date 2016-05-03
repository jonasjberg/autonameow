# -*- coding: utf-8 -*-

# autonameow
# ~~~~~~~~~~
# written by Jonas Sjöberg
# jomeganas@gmail.com
# ____________________________________________________________________________

import logging
import os

import datetime

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
        datetime = self.get_datetime_list()

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
        datetime = self.get_oldest_datetime()
        # print('type(datetime): %s' % type(datetime))
        print('Oldest date/time information for file:')
        print('\"%s\"' % str(self.file_object.path))
        FORMAT = '%-20.20s : %-s'
        print(FORMAT % ("Datetime", "Value"))
        # valuestr = datetime.strftime("%Y-%m-%d %H:%M:%S")
        # print(FORMAT % ('oldest', valuestr))
        print(FORMAT % ('oldest', str(datetime)))

    def prefix_date_to_filename(self):
        datetime = self.get_oldest_datetime()
        ext = disk.get_file_extension(self.file_object.path)
        fn_noext = self.file_object.path.replace(ext, '')

        print('%s %s%s' % (datetime.strftime('%Y-%m-%d_%H%M%S'), fn_noext, ext))

    def run(self):
        # Select analyzer based on detected file type.
        if self.file_object.type == "JPEG":
            logging.debug('File is of type [JPEG]')
            self.analyzer = ImageAnalyzer(self.file_object)

        elif self.file_object.type == "PDF":
            logging.debug('File is of type [PDF]')
            self.analyzer = PdfAnalyzer(self.file_object)

        else:
            # Create a basic analyzer, common to all file types.
            logging.debug('File is of type [unknown]')
            self.analyzer = AnalyzerBase(self.file_object)

        # Run analyzer.
        self.analyzer.run()

        #str_year = self.fileObject.get_oldest_datetime().strftime('%Y')
        #str_title = self.analyzer.title
        #str_author = 'author'  # self.analyzer.author
        #str_publisher = 'publisher'
        #new_filename = str_title + ' ' + str_author + ' ' + str_publisher + ' ' + str_year
        #print('New Filename: \"%s\"' % new_filename)

        # self.print_all_datetime_info()


    def add_datetime(self, dt):
        """
        Add date/time-information dict to the list of all date/time-objects
        found for this FileObject.
        :param dt: date/time-information dict ('KEY' 'datetime') to add
        :return:
        """
        if dt is None:
            logging.warning('Got null argument')
            return

        if not dt in self.datetime_list:
            # logging.debug('Adding datetime-object [%s] to list' % str(type(dt)))
            self.datetime_list.append(dt)

    def get_datetime_list(self):
        """
        Get the list of datetime-objects found for this FileObject.
        :return: date/time-information as a list of dicts
        """
        return self.datetime_list

    def get_oldest_datetime(self):
        """
        Get the oldest datetime-object in datetime_list.
        :return:
        """
        oldest_yet = datetime.datetime.max
        for l in self.datetime_list:
            for entry in l:
                value = l[entry]
                if value < oldest_yet:
                    oldest_yet = value

        return oldest_yet
