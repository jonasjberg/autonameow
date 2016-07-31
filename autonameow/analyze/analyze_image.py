# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

from __future__ import print_function

import logging
import re
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from datetime import datetime

from pytesseract import image_to_string

from analyze.analyze_abstract import AbstractAnalyzer
from util import dateandtime


class ImageAnalyzer(AbstractAnalyzer):
    def __init__(self, file_object, filters):
        super(ImageAnalyzer, self).__init__(file_object, filters)

        # Start by trying to extract EXIF information from the image.
        logging.debug('Extracting EXIF data ..')
        self.exif_data = self._get_exif_data()
        self.ocr_text = self._get_text_from_ocr()

        # TODO: Run OCR on the image and store any textual output.
        # TODO: Run (text) analysis on any text produced by OCR.
        #       (I.E. extract date/time, titles, authors, etc.)

    def get_datetime(self):
        result = []
        exif_timestamps = self._get_exif_datetime()
        if exif_timestamps:
            result += exif_timestamps

        # TODO: Fix this here below.
        ocr_timestamps = self._get_ocr_datetime()
        if ocr_timestamps:
            result += ocr_timestamps

        return result

    def get_author(self):
        # TODO: Implement.
        pass

    def get_title(self):
        # TODO: Implement.
        pass

    def get_tags(self):
        # TODO: Implement.
        pass

    def _get_exif_datetime(self):
        """
        Extracts date and time information from the EXIF data.
        The EXIF data could be corrupted or contain non-standard entries.
        Extraction should be fault-tolerant and able to handle non-standard
        entry formats.
        :return: a list of dictionaries on the form:
                 [ { 'value': datetime.datetime(2016, 6, 5, 16, ..),
                     'source' : 'datetimeoriginal',
                     'weight'  : 1
                   }, .. ]
        """
        if self.exif_data is None:
            logging.warning('Found no EXIF data in file '
                            '"{}"'.format(self.file_object.path))
            return

        # Exif field, weight
        # TODO: Recheck the weights. Should they even be defined here?
        DATE_TAG_FIELDS = [['DateTimeOriginal', 1],
                           ['DateTimeDigitized', 1],
                           ['DateTimeModified', 0.5],
                           ['CreateDate', 1],
                           ['ModifyDate', 0.5],
                           ['DateTime', 0.75]]
        results = []
        logging.debug('Extracting date/time-information from EXIF-tags')
        for field, weight in DATE_TAG_FIELDS:
            try:
                dtstr = self.exif_data[field]
            except KeyError:
                # logging.warn('KeyError for key [{}]'.format(field))
                continue
            if not dtstr:
                continue

            dt = None
            # Expected date format:         2016:04:07 18:47:30
            date_pattern = re.compile(
                '.*(\d{4}:[01]\d:[0123]\d\ [012]\d:[012345]\d:[012345]\d).*')
            try:
                re_match = date_pattern.search(dtstr)
            except TypeError:
                logging.warn('TypeError for [%s]'.format(dtstr))
            else:
                datetime_str = re_match.group(1)
                # logging.debug('datetime_str: %s' % datetime_str)
                try:
                    dt = datetime.strptime(datetime_str, '%Y:%m:%d %H:%M:%S')
                except ValueError:
                    logging.warning('Unable to parse datetime from '
                                    '[%s]'.format(field))
            if dt:
                # logging.debug('ADDED: results[%s] = [%s]' % (key, dt))
                results.append({'value': dt,
                                'source': field.lower(),
                                'weight': weight})

        logging.debug('Searching for GPS date/time-information in EXIF-tags')
        try:
            gps_date = self.exif_data['GPSDateStamp']
            gps_time = self.exif_data['GPSTimeStamp']
        except KeyError:
            # logging.warn('KeyError for key GPS{Date,Time}Stamp]')
            pass
        else:
            dt = None
            gps_time_str = ''
            for toup in gps_time:
                gps_time_str += str(toup[0])

            # logging.debug('gps_time_str: \"%s\"' % gps_time_str)
            # logging.debug('gps_date: \"%s\"' % gps_date)
            gps_datetime_str = gps_date + gps_time_str
            try:
                dt = datetime.strptime(gps_datetime_str, '%Y:%m:%d%H%M%S')
            except ValueError:
                logging.warning('Unable to parse GPS datetime from '
                                '[%s]'.format(gps_datetime_str))
            if dt:
                # logging.debug('ADDED: results[%s] = [%s]' % (key, dt))
                results.append({'value': dt,
                                'source': 'gpsdatetime',
                                'weight': 1})

        # Remove erroneous date value produced by "OnePlus X" as of 2016-04-13.
        # https://forums.oneplus.net/threads/2002-12-08-exif-date-problem.104599/
        if self.exif_data['Make'] == 'OnePlus' and \
           self.exif_data['Model'] == 'ONE E1003':
            bad_exif_date = datetime.strptime('20021208_120000',
                                              '%Y%m%d_%H%M%S')
            try:
                # if results['Exif_DateTimeDigitized'] == bad_exif_date:
                #     logging.debug('Removing erroneous date \"%s\"' %
                #                   str(bad_exif_date))
                #     del results['Exif_DateTimeDigitized']
                # http://stackoverflow.com/a/1235631
                # TODO: FIX THIS! Currently does not pass anything if the bad
                #                 exif date is in the dict.
                pass
                results[:] = [d for d in results if \
                              (d.get('source') == 'DateTimeDigitized' and \
                               d.get('value') != bad_exif_date)]
            except KeyError:
                # logging.warn('KeyError for key [DateTimeDigitized]')
                pass

        return results

    def _get_exif_data(self):
        """
        Extracts EXIF information from a image using PIL.
        The EXIF data is stored in a dict using human-readable keys.
        :return: Dict of EXIF data.
        """
        # Create empty dictionary to store exif "key:value"-pairs in.
        result = {}

        # Extract EXIF data using PIL.ExifTags.
        exif_data = None
        filename = self.file_object.path
        try:
            image = Image.open(filename)
        except IOError as e:
            logging.warning('PIL image I/O error({0}): {1}'.format(e.errno,
                                                                   e.strerror))
        else:
            try:
                exif_data = image._getexif()
            except Exception as e:
                logging.warning('PIL image EXIF extraction error({0}): '
                                '{1}'.format(e.args, e.message))
        if not exif_data:
            logging.warning('Unable to extract EXIF data.')
            return None

        for tag, value in exif_data.items():
            # Obtain a human-readable version of the tag.
            tag_string = TAGS.get(tag, tag)

            # Check if tag contains GPS data.
            if tag_string == 'GPSInfo':
                logging.debug('Found GPS information')
                result_gps = {}

                # Loop through the GPS information
                for tag_gps, value_gps in value.items():
                    # Obtain a human-readable version of the GPS tag.
                    tag_string_gps = GPSTAGS.get(tag_gps, tag_gps)

                    if value_gps is not None:
                        # print('[tag_string_gps] %-15.15s : '
                        #       '%-80.80s'.format(type(tag_string_gps),
                        #                         str(tag_string_gps)))
                        # print('[value_gps]      %-15.15s : '
                        #       '%-80.80s'.format(type(value_gps),
                        #                         str(value_gps)))
                        result_gps[tag_string_gps] = value_gps

            else:
                if value is not None:
                    # print('[tag_string] %-15.15s : '
                    #       '%-80.80s'.format(type(tag_string),
                    #                         str(tag_string)))
                    # print('[value]      %-15.15s : '
                    #       '%-80.80s'.format(type(value),
                    #                         str(value)))
                    result[tag_string] = value

        # Return result, should be empty if errors occured.
        return result

    def _get_text_from_ocr(self):
        """
        Get any textual content from the image by running OCR with tesseract
        through the pytesseract wrapper.
        :return: image text if found, else None (?)
        """
        # TODO: Test this!
        image_text = None
        filename = self.file_object.path
        try:
            image = Image.open(filename)
        except IOError as e:
            logging.warning('PIL image I/O error({}): {}'.format(e.errno,
                                                                 e.strerror))
        else:
            try:
                image_text = image_to_string(image)
            except Exception as e:
                logging.warning('PyTesseract image OCR error({}): '
                                '{}'.format(e.args, e.message))
        if not image_text:
            return None
        else:
            image_text = image_text.strip()
            logging.debug('Extracted [{}] bytes of '
                          'text'.format(len(image_text)))
            # print('Got image text: ')
            # print(image_text)
            return image_text

    def _get_ocr_datetime(self):
        """
        Extracts date and time information from the text produced by OCR.
        :return: a list of dictionaries on the form:
                 [ { 'value': datetime.datetime(2016, 6, 5, 16, ..),
                     'source' : 'ocr',
                     'weight'  : 0.1
                   }, .. ]
        """
        if self.ocr_text is None:
            logging.warning('Found no text from OCR of '
                            '\"{}\"'.format(self.file_object.path))
            return None

        results = []
        text = self.ocr_text
        if type(text) == list:
            text = ' '.join(text)

        dt_regex = dateandtime.regex_search_str(text)
        if dt_regex:
            for e in dt_regex:
                results.append({'value': e,
                                'source': 'image_ocr_regex',
                                'weight': 0.25})

        text_split = text.split('\n')
        logging.debug('Try getting datetime from text split by newlines')
        for t in text_split:
            dt_brute = dateandtime.bruteforce_str(t)
            if dt_brute:
                for e in dt_brute:
                    results.append({'value': e,
                                    'source': 'image_ocr_brute',
                                    'weight': 0.1})

            dt_ocr_special = dateandtime.special_datetime_ocr_search(t)
            if dt_ocr_special:
                results.append({'value': dt_ocr_special,
                                'source': 'image_ocr_special',
                                'weight': 0.25})

        if len(results) == 0:
            logging.warning('Found no date/time-information in OCR text.')
            return None
        else:
            return results
