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
from analyze.text import TextAnalyzer
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

        if self.file_object is None:
            logging.critical('Got NULL file!')
            pass

    def print_all_datetime_info(self):
        dt_list = self.file_object.datetime_list

        print('All date/time information for file:')
        # print('\"%s\"' % str(self.file_object.path))

        datetime_report = {}
        flipped = {}
        for dt_dict in dt_list:
            # print('[dt_dict] %-15.15s   : %-80.80s' % (type(dt_dict), str(dt_dict)))
            if type(dt_dict) is not dict:
                logging.error('datetime list contains unexpected type %s' % type(dt_dict))
                continue

            for dt_key, dt_value in dt_dict.iteritems():
                # logging.info('Regex matcher found [{:^3}] matches.'.format(matches))
                # valuestr = v.isoformat()

                # # For now, lets get the first filename datetime only.
                # if dt_key.startswith('FilenameDateTime_'):
                #     if dt_key != 'FilenameDateTime_00':
                #         continue

                if dt_value not in flipped:
                    flipped[dt_value] = [dt_key]
                else:
                    flipped[dt_value].append(dt_key)

        # Sort by length of the lists stored as dict values.
        flipped_sorted = sorted(flipped.items(), key=lambda k: len(k[1]), reverse=True)

        def print_report_columns(c1, c2, c3):
            print('{0:30}  {1:>20}  {2:>8s}'.format(c1, c2, c3))

        print_report_columns('Date-/timestamp', 'Source', '#')

        for l in flipped_sorted:
            try:
                dt = l[0].isoformat()
            except TypeError:
                pass

            count = len(l[1])
            c1 = '{:30}'.format(dt)
            c2 = '{:>20}'.format(l[1][0])
            c3 = '{:03d}'.format(count)
            print_report_columns(c1, c2, c3)

            if count > 1:
                for v in l[1][1:]:
                    c2 = '{:>20}'.format(v)
                    print_report_columns(' ', c2, ' ')

        # for key, value in flipped.iteritems():
        #     # Dict keys are now datetime objects.
        #     try:
        #         keystr = key.strftime("%Y-%m-%d %H:%M:%S")
        #     except ValueError:
        #         continue
        #
        #     count = len(value)
        #
        #     c1 = '{:03d}'.format(count)
        #     c2 = '{:19}'.format(keystr)
        #     c3 = '{:80}'.format(value[0])
        #     print_report_columns(c1, c2, c3)
        #
        #     if count > 1:
        #         for v in value[1:]:
        #             c3 = '{:80}'.format(v)
        #             print_report_columns(' ', ' ', c3)



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
        self.analyzer = AnalyzerBase(self.file_object)
        self.analyzer.run()

        # Select analyzer based on detected file type.
        if self.file_object.type == "JPEG":
            logging.debug('File is of type [JPEG]')
            self.analyzer = ImageAnalyzer(self.file_object)

        elif self.file_object.type == "PDF":
            logging.debug('File is of type [PDF]')
            self.analyzer = PdfAnalyzer(self.file_object)

        elif self.file_object.type == "UTF-8" or self.file_object.type == "ASCII":
            logging.debug('File is a of type [TEXT]')
            self.analyzer = TextAnalyzer(self.file_object)

        else:
            logging.debug('File is of type [unknown]')
            return

        # Run analyzer.
        self.analyzer.run()

        #str_year = self.fileObject.get_oldest_datetime().strftime('%Y')
        #str_title = self.analyzer.title
        #str_author = 'author'  # self.analyzer.author
        #str_publisher = 'publisher'
        #new_filename = str_title + ' ' + str_author + ' ' + str_publisher + ' ' + str_year
        #print('New Filename: \"%s\"' % new_filename)

        # self.print_all_datetime_info()


