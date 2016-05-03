# -*- coding: utf-8 -*-

# autonameow
# ~~~~~~~~~~
# written by Jonas Sjöberg
# jomeganas@gmail.com
# ____________________________________________________________________________

from __future__ import print_function

import logging
import pprint
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from datetime import datetime

import re

from analyze.common import AnalyzerBase
from util.fuzzy_date_parser import DateParse


class ImageAnalyzer(AnalyzerBase):
    def __init__(self, file_path):
        self.file_path = file_path
        self.exif_data = None

    def run(self):
        """
        Run the analysis.
        """

        fs_timestamps = self.get_datetime_from_filesystem()
        if fs_timestamps:
            self.fileObject.add_datetime(fs_timestamps)

        if self.exif_data is None:
            logging.debug('Fetching EXIF data ..')
            self.exif_data = self.get_EXIF_data()

        exif_datetime = self.get_EXIF_datetime()
        if exif_datetime:
            self.fileObject.add_datetime(exif_datetime)
            # pp = pprint.PrettyPrinter(indent=4)
            # pp.pprint(exif_datetime)

    # def get_datetime(self):
    #     datetime = self.get_EXIF_datetime()
    #
    #     if datetime is None:
    #         logging.warning('Unable to extract datetime.')
    #     else:
    #         return datetime

    def get_EXIF_datetime(self):
        """
        Extracts date and time information from the EXIF data.
        The EXIF data could be corrupted or contain non-standard entries.
        Extraction should be fault-tolerant and able to handle non-standard
        entry formats.
        :return: Date/time as a dict of datetime-objects, keyed by EXIF-fields.
        """
        if self.exif_data is None:
            logging.warning('File has no EXIF data')
            return

        DATE_TAG_FIELDS = ['DateTimeOriginal', 'DateTimeDigitized',
                           'DateTimeModified', 'CreateDate', 'ModifyDate']
        results = {}
        logging.debug('Extracting date/time-information from EXIF-tags')
        for field in DATE_TAG_FIELDS:
            dt = dtstr = None
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
                logging.debug('datetime_str: %s' % datetime_str)

                try:
                    dt = datetime.strptime(datetime_str, "%Y:%m:%d %H:%M:%S")
                except ValueError:
                    logging.warning(
                        'Unable to parse datetime from [%s]' % field)

            if dt and dt not in results:
                logging.debug('ADDED: results[%s] = [%s]' % (field, dt))
                results[field] = dt

        logging.debug('Searching for GPS date/time-information in EXIF-tags')
        gps_date = gps_time = None
        try:
            gps_date = self.exif_data['GPSDateStamp']
            gps_time = self.exif_data['GPSTimeStamp']
        except KeyError:
            #logging.warn('KeyError for key GPS{Date,Time}Stamp]')
            pass
        else:
            gps_time_str = ''
            for toup in gps_time:
                gps_time_str += str(toup[0])

            logging.debug('gps_time_str: \"%s\"' % gps_time_str)
            logging.debug('gps_date: \"%s\"' % gps_date)
            gps_datetime_str = gps_date + gps_time_str

            try:
                dt = datetime.strptime(gps_datetime_str, "%Y:%m:%d%H%M%S")
            except ValueError:
                logging.warning('Unable to parse GPS datetime from [%s]' % gps_datetime_str)
            else:
                if dt not in results:
                    logging.debug('ADDED: results[%s] = [%s]' % ('GPSDateTime', dt))
                    results['GPSDateTime'] = dt

        # Remove erroneous date value produced by "OnePlus X" as of 2016-04-13.
        # https://forums.oneplus.net/threads/2002-12-08-exif-date-problem.104599/
        bad_exif_date = datetime.strptime('2002-12-08_12:00:00',
                                          '%Y-%m-%d_%H:%M:%S')
        try:
            if self.exif_data['Make'] == 'OnePlus' and \
               self.exif_data['Model'] == 'ONE E1003':
                if results['DateTimeDigitized'] == bad_exif_date:
                    logging.debug("Removing erroneous date \"%s\"" %
                                  str(bad_exif_date))
                    del results['DateTimeDigitized']
        except KeyError:
            #logging.warn('KeyError for key [DateTimeDigitized]')
            pass

        return results

    def get_EXIF_data(self):
        """
        Extracts EXIF information from a image using PIL.
        The EXIF data is stored in a dict using human-readable keys.
        :return: Dict of EXIF data.
        """
        # Create empty dictionary to store exif "key:value"-pairs in.
        result = {}

        # Extract EXIF data using PIL.ExifTags.
        exif_data = None
        try:
            filename = self.fileObject.path
            image = Image.open(filename)
            exif_data = image._getexif()
        except Exception:
            logging.warning(
                'Unable to extract EXIF data from \"{}\"' % str(filename))
            return None

        if exif_data:
            for tag, value in exif_data.items():
                # Obtain a human-readable version of the tag.
                tagString = TAGS.get(tag, tag)

                # Check if tag contains GPS data.
                if tagString == "GPSInfo":
                    logging.debug('Found GPS information')
                    resultGPS = {}

                    # Loop through the GPS information
                    for tagGPS, valueGPS in value.items():
                        # Obtain a human-readable version of the GPS tag.
                        tagStringGPS = GPSTAGS.get(tagGPS, tagGPS)

                        if valueGPS is not None:
                            # resultGPS[tagStringGPS] = valueGPS
                            result[tagStringGPS] = valueGPS

                            # # DEBUG: print extracted GPS information.
                            # pp = pprint.PrettyPrinter(indent=4)
                            # pp.pprint(resultGPS)

                else:
                    if value is not None:
                        result[tagString] = value

                        # pp = pprint.PrettyPrinter(indent=4)
                        # pp.pprint(result)

        # Return result, should be empty if errors occured.
        return result
