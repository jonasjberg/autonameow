# -*- coding: utf-8 -*-

# autonameow
# ~~~~~~~~~~
# written by Jonas Sjöberg
# jomeganas@gmail.com
# ____________________________________________________________________________

import logging
from colorama import Fore
from colorama import Back
from colorama import Style

from analyze.common import AnalyzerBase
from analyze.image import ImageAnalyzer
from analyze.pdf import PdfAnalyzer
from analyze.text import TextAnalyzer
from util import disk


class Analysis(object):
    """
    Main interface to all file analyzers.
    """

    analyzer = None
    best_datetime = None
    best_name = None

    def __init__(self, file_object, filters):
        self.file_object = file_object

        if self.file_object is None:
            logging.critical('Got NULL file!')
            pass

        self.filters = filters

    def print_all_datetime_info(self):
        """
        Prints all date/time-information for the current file.
        :return:
        """
        dt_list = self.file_object.datetime_list

        print('All date/time information for file:')
        flipped = {}
        for dt_dict in dt_list:
            # print('[dt_dict] %-15.15s   : %-80.80s' % (type(dt_dict), str(dt_dict)))
            if type(dt_dict) is not dict:
                logging.error('datetime list contains unexpected type %s' % type(dt_dict))
                continue

            # Create a new dict with values being lists of the "sources"
            # for each datetime-object keyed by datetime-objects.
            for dt_key, dt_value in dt_dict.iteritems():
                if dt_value not in flipped:
                    flipped[dt_value] = [dt_key]
                else:
                    flipped[dt_value].append(dt_key)

        # Sort by length of the lists of datetime-object stored as values
        # in the dict.
        flipped_sorted = sorted(flipped.items(),
                                key=lambda k: len(k[1]),
                                reverse=True)

        def print_report_columns(c1, c2, c3):
            """
            Prints a line with three columns.
            """
            print('{0:20}  {1:>8s}  {2:>30}'.format(c1, c2, c3))

        # Print the header information.
        print(Back.WHITE + Fore.BLACK +
              '{0:20}  {1:>8s}  {2:>30}'.format('Date-/timestamp', '#', 'Source(s)')
              + Fore.RESET + Back.RESET)

        for line in flipped_sorted:
            try:
                dt = line[0].isoformat()
            except TypeError:
                pass

            print_report_columns('{:20}'.format(dt),
                                 '{:03d}'.format(len(line[1])),
                                 '{:>30}'.format(line[1][0]))
            if len(line[1]) > 1:
                for v in line[1][1:]:
                    print_report_columns(' ', ' ', '{:>30}'.format(v))
                print('')

    def print_oldest_datetime(self):
        oldest_dt = self.file_object.get_oldest_datetime()
        print('Oldest date/time information for file:')
        print('\"%s\"' % str(self.file_object.path))
        print('{:<20} : {:<}'.format('Datetime', 'Value'))
        print('{:<20} : {:<}'.format('oldest', oldest_dt))

    def prefix_date_to_filename(self):
        fo = self.file_object

        datetime = fo.get_oldest_datetime()

        ext = fo.extension
        fn_noext = fo.basename_no_ext
        fn_noext = fn_noext.replace(ext, '')

        print('%s %s.%s' % (datetime.strftime('%Y-%m-%d_%H%M%S'), fn_noext, ext))

    def run(self):
        # Create a basic analyzer, common to all file types.
        self.analyzer = AnalyzerBase(self.file_object, self.filters)
        self.analyzer.run()

        # Select analyzer based on detected file type.
        if self.file_object.type == "JPEG":
            logging.debug('File is of type [JPEG]')
            self.analyzer = ImageAnalyzer(self.file_object, self.filters)

        elif self.file_object.type == "PDF":
            logging.debug('File is of type [PDF]')
            self.analyzer = PdfAnalyzer(self.file_object, self.filters)

        elif self.file_object.type == "UTF-8" or self.file_object.type == "ASCII":
            logging.debug('File is a of type [TEXT]')
            self.analyzer = TextAnalyzer(self.file_object, self.filters)

        else:
            logging.debug('File is of type [unknown]')
            return

        # Run analyzer.
        self.analyzer.run()


