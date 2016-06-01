# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

import logging
from colorama import Back
from colorama import Fore

from analyze.analyze_filesystem import FilesystemAnalyzer
from analyze.analyze_image import ImageAnalyzer
from analyze.analyze_pdf import PdfAnalyzer
from analyze.analyze_text import TextAnalyzer


class ExtractedData(object):
    # TODO: Not used and incomplete -- implement properly or remove entirely.
    def __init__(self, data, weight):
        self.data = data
        self.weight = weight


class Analysis(object):
    """
    Main interface to all file analyzers.
    """
    analyzer = None

    def __init__(self, file_object, filters):
        self.file_object = file_object
        if self.file_object is None:
            logging.critical('Got NULL file!')
            pass

        self.filters = filters

        # List of analyzers to run.
        analysis_run_queue = [FilesystemAnalyzer]

        # Create a basic analyzer, common to all file types.
        self.analyzer = FilesystemAnalyzer(self.file_object, self.filters)

        # Select analyzer based on detected file type.
        t = self.file_object.type
        if t == 'JPG':
            logging.debug('File is of type [JPG]')
            # self.analyzer = ImageAnalyzer(self.file_object, self.filters)
            analysis_run_queue.append(ImageAnalyzer)
        elif t == 'PNG':
            logging.debug('File is of type [PNG]')
            # self.analyzer = ImageAnalyzer(self.file_object, self.filters)
            analysis_run_queue.append(ImageAnalyzer)
        elif t == 'PDF':
            logging.debug('File is of type [PDF]')
            # self.analyzer = PdfAnalyzer()
            analysis_run_queue.append(PdfAnalyzer)
        elif t == 'TXT':
            logging.debug('File is a of type [TEXT]')
            # self.analyzer = TextAnalyzer()
            analysis_run_queue.append(PdfAnalyzer)
        else:
            logging.debug('File type ({}) is not yet mapped to a type-specific '
                          'Analyzer.'.format(self.file_object.type))
            pass

        collected_datetime = []
        # collected_title = []
        # collected_author = []
        # etc ..
        for analysis in analysis_run_queue:
            if not analysis:
                logging.error('Got Null analysis.')
                continue

            a = analysis(self.file_object, self.filters)
            if not a:
                logging.error('Got Null analysis.')
                continue
            logging.debug('Running Analyzer: {}'.format(a.__class__))
            collected_datetime.append(a.get_datetime())
            # collected_title.append(analysis.get_title())
            # collected_author.append(analysis.get_author())
            # etc ..




    def filter_datetime(self, dt):
        """
        Adds a datetime-entry by first checking any filters for matches.
        Matches are ignored, "passed out" ..
        :param dt: datetime to add
        """
        if type(dt) is not dict:
            logging.warning('Got unexpected type \"{}\" '
                            '(expected dict)'.format(type(dt)))

        if type(dt) is list:
            if not dt:
                logging.warning('Got empty list')
                return

            # TODO: Handle whether dicts or lists should be passed, and passed
            #       only that type, OR make sure both types can be handled.
            # for item in dt:
            #     if not item:
            #         continue
            #     if type(item) is dict:
            #         for k, v in item.iteritems():
            #             if v in
            #             dt_dict[k] = v
            return

        passed = {}
        removed = {}
        ignore_years = [yr.year for yr in self.filters['ignore_years']]
        ignore_before = self.filters['ignore_before_year']
        ignore_after = self.filters['ignore_after_year']
        ok = True
        for key, value in dt.iteritems():
            if ignore_years is not None and len(ignore_years) > 0:
                if value.year in ignore_years:
                    ok = False

            # if type(value) is not datetime:
            #     logging.error('type(value) is not datetime: {} {}'.format(str(value), type(value)))
            # if ignore_before.year > value.year > ignore_after.year:
            if value.year < ignore_before.year:
                ok = False
            if value.year > ignore_after.year:
                ok = False

            if ok:
                # logging.debug('Filter passed date/time {} .. '.format(dt))
                passed[key] = value
            else:
                # logging.debug('Filter removed date/time {} .. '.format(dt))
                removed[key] = value

        logging.debug('Datetime filter removed {} entries, passed {} '
                      'entries.'.format(len(removed), len(passed)))

        self.file_object.add_datetime(passed)


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
            temp_dict = None
            for dt_key, dt_value in dt_dict.iteritems():
                if type(dt_value) is list:
                    i = 0
                    temp_dict = {}
                    for entry in dt_value:
                        if entry is not None:
                            temp_dict['{}_{:03d}'.format(dt_key, i)] = entry
                            i += 1
                else:
                    if dt_value not in flipped:
                        flipped[dt_value] = [dt_key]
                    else:
                        flipped[dt_value].append(dt_key)

            if temp_dict:
                for dt_key, dt_value in temp_dict.iteritems():
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

    def find_most_probable_datetime(self):
        # TODO: Implement ..
        print('FINDING MOST PROBABLE DATETIME NOWWW')
        dt_list = self.file_object.datetime_list
        # dt_list = unpack_dict(dt_list)

        for entry in dt_list:
            # for key, value in entry.iteritems():
            #     if key == 'Exif_DateTimeOriginal':
            #         print('Most probable :: Exif_DateTimeOriginal: {}'.format(value))
            pass

        if 'Filename_brute_00' in dt_list:
            print('Most probable :: Filename_brute_00 {}'.format('value'))
        if 'Exif_DateTimeOriginal' in dt_list:
            print('Most probable :: Exif_DateTimeOriginal: {}'.format('value'))

    def prefix_date_to_filename(self):
        # TODO: Implement this properly ..
        fo = self.file_object

        datetime = fo.get_oldest_datetime()

        ext = fo.extension
        fn_noext = fo.basename_no_ext
        fn_noext = fn_noext.replace(ext, '')

        print('%s %s.%s' % (datetime.strftime('%Y-%m-%d_%H%M%S'), fn_noext, ext))


