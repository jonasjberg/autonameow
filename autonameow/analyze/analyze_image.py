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
from analyze.analyze_filesystem import FilesystemAnalyzer
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
            # self.filter_datetime(exif_datetime)
            result += exif_timestamps

        # TODO: Fix this here below.
        ocr_timestamps = self._get_ocr_datetime()
        ocr_ts = dateandtime.get_datetime_from_text(self.ocr_text, 'ocr')
        if ocr_ts:
            result.append(ocr_ts)

        return result

    def get_author(self):
        # TODO: Implement.
        pass

    def get_title(self):
        # TODO: Implement.
        pass

    def _get_exif_datetime(self):
        """
        Extracts date and time information from the EXIF data.
        The EXIF data could be corrupted or contain non-standard entries.
        Extraction should be fault-tolerant and able to handle non-standard
        entry formats.
        :return: Date/time as a dict of datetime-objects, keyed by EXIF-fields.
        """
        if self.exif_data is None:
            logging.warning('Found no EXIF data in file '
                            '"{}"'.format(self.file_object.path))
            return

        DATE_TAG_FIELDS = ['DateTimeOriginal', 'DateTimeDigitized',
                           'DateTimeModified', 'CreateDate', 'ModifyDate',
                           'DateTime']
        results = {}
        logging.debug('Extracting date/time-information from EXIF-tags')
        for field in DATE_TAG_FIELDS:
            dt = None
            try:
                dtstr = self.exif_data[field]
            except KeyError:
                #logging.warn('KeyError for key [{}]'.format(field))
                continue

            if not dtstr:
                continue

            # Expected date format:         2016:04:07 18:47:30
            date_pattern = re.compile(
                '.*(\d{4}:[01]\d:[0123]\d\ [012]\d:[012345]\d:[012345]\d).*')
            try:
                re_match = date_pattern.search(dtstr)
            except TypeError:
                logging.warn('TypeError for [%s]' % dtstr)
            else:
                datetime_str = re_match.group(1)
                # logging.debug('datetime_str: %s' % datetime_str)

                try:
                    dt = datetime.strptime(datetime_str, '%Y:%m:%d %H:%M:%S')
                except ValueError:
                    logging.warning('Unable to parse datetime from [%s]'
                                    % field)

            if dt:
                key = 'Exif_{}'.format(field)
                logging.debug('ADDED: results[%s] = [%s]' % (key, dt))
                results[key] = dt

        logging.debug('Searching for GPS date/time-information in EXIF-tags')
        try:
            gps_date = self.exif_data['GPSDateStamp']
            gps_time = self.exif_data['GPSTimeStamp']
        except KeyError:
            #logging.warn('KeyError for key GPS{Date,Time}Stamp]')
            pass
        else:
            dt = None
            gps_time_str = ''
            for toup in gps_time:
                gps_time_str += str(toup[0])

            logging.debug('gps_time_str: \"%s\"' % gps_time_str)
            logging.debug('gps_date: \"%s\"' % gps_date)
            gps_datetime_str = gps_date + gps_time_str

            try:
                dt = datetime.strptime(gps_datetime_str, '%Y:%m:%d%H%M%S')
            except ValueError:
                logging.warning('Unable to parse GPS datetime from [%s]'
                                % gps_datetime_str)
            if dt:
                key = 'Exif_GPSDateTime'
                logging.debug('ADDED: results[%s] = [%s]' % (key, dt))
                results[key] = dt

        # Remove erroneous date value produced by "OnePlus X" as of 2016-04-13.
        # https://forums.oneplus.net/threads/2002-12-08-exif-date-problem.104599/
        bad_exif_date = datetime.strptime('2002-12-08_12:00:00',
                                          '%Y-%m-%d_%H:%M:%S')
        try:
            if self.exif_data['Make'] == 'OnePlus' and \
               self.exif_data['Model'] == 'ONE E1003':
                if results['Exif_DateTimeDigitized'] == bad_exif_date:
                    logging.debug('Removing erroneous date \"%s\"' %
                                  str(bad_exif_date))
                    del results['Exif_DateTimeDigitized']
        except KeyError:
            #logging.warn('KeyError for key [DateTimeDigitized]')
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
            return image_text

    def _get_ocr_datetime(self):
        """
        Extracts EXIF information from a image using PIL.
        The EXIF data is stored in a dict using human-readable keys.
        :return: Dict of EXIF data.
        """
        if self.ocr_text is None:
            logging.warning('Found no text from OCR of '
                            '\"{}\"'.format(self.file_object.path))
            return
        pass

