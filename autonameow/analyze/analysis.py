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

    def __init__(self, file_path):
        self.file_path = file_path
        self.datetime_list = []

        if file_path is None:
            logging.critical('Got NULL file path')
            return

        # Remains untouched, for use when renaming file
        self.original_file_path = os.path.basename(file_path)
        logging.debug('Original file path: \"%s\"' % self.original_file_path)

        # Get full absolute path
        self.file_path = os.path.abspath(self.file_path)
        logging.debug('Absolute path: \"%s\"' % self.file_path)

        # Figure out basic file type
        self.file_type = disk.read_magic_header(file_path)


    def print_all_datetime_info(self):
        datetime = self.get_datetime_list()

        print('All date/time information for file:')
        print('\"%s\"' % str(self.file_path))
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
        print('\"%s\"' % str(self.file_path))
        FORMAT = '%-20.20s : %-s'
        print(FORMAT % ("Datetime", "Value"))
        # valuestr = datetime.strftime("%Y-%m-%d %H:%M:%S")
        # print(FORMAT % ('oldest', valuestr))
        print(FORMAT % ('oldest', str(datetime)))

    def prefix_date_to_filename(self):
        datetime = self.get_oldest_datetime()
        ext = disk.get_file_extension(self.file_path)
        fn_noext = self.file_path.replace(ext, '')

        print('%s %s%s' % (datetime.strftime('%Y-%m-%d_%H%M%S'), fn_noext, ext))

    def run(self):
        # Select analyzer based on detected file type.
        if self.file_type == "JPEG":
            logging.debug('File is of type [JPEG]')
            self.analyzer = ImageAnalyzer(self.file_path)

        elif self.file_type == "PDF":
            logging.debug('File is of type [PDF]')
            self.analyzer = PdfAnalyzer(self.file_path)

        else:
            # Create a basic analyzer, common to all file types.
            logging.debug('File is of type [unknown]')
            self.analyzer = AnalyzerBase(self.file_path)

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
