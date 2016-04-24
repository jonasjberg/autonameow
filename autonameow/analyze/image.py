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

from analyze.common import AnalyzerBase
from util.fuzzy_date_parser2 import Parser


class ImageAnalyzer(AnalyzerBase):
    def __init__(self, fileObject):
        self.fileObject = fileObject
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
        # Use "brute force"-type date parser everywhere?
        # Probably not necessary. Could possible handle some edges cases.
        # Performance could become a problem at scale ..
        # TODO: Investigate date parser types, etc..
        parse = Parser()

        DATE_TAG_FIELDS = ['DateTimeOriginal', 'DateTimeDigitized',
                           'DateTimeModified', 'CreateDate']
        results = {}
        logging.debug('Extracting date/time-information from EXIF-tags')
        for field in DATE_TAG_FIELDS:
            # date = time = None
            try:
                # date, time = self.exif_data[field].split()
                dtstr = self.exif_data[field]
            except KeyError, TypeError:
                logging.warn('KeyError for key [{}]'.format(field))
                pass

            # dt = parse.datetime(date, time)
            print('dtstr TYPE: %s' % type(dtstr))
            dt = parse.datetime(' '.join(dtstr))
            if dt:
                logging.debug('Adding field [%s] with value [%s] to results' % (str(field), str(dt.isoformat())))
                results[field] = dt

        logging.debug('Searching for GPS date/time-information in EXIF-tags')
        GPS_date = GPS_time = None
        try:
            GPS_date = self.exif_data['GPSDateStamp']
            GPS_time = self.exif_data['GPSTimeStamp']
        except KeyError:
            logging.warn('KeyError for key GPS{Date,Time}Stamp]')
            pass

        if GPS_time:
            GPS_time_str = ''
            for toup in GPS_time:
                GPS_time_str += str(toup[0])
            #GPS_time_detoupled = str(GPS_time[0][0]) + str(GPS_time[1][0]) + str(GPS_time[2][0])
            #clean_GPS_time = parser.time(GPS_time_detoupled)

        GPS_dt = parse.datetime(GPS_date, GPS_time_str)
        if GPS_dt:
            logging.debug('Adding field [%s] with value [%s] to results' % ('GPSDateTime', str(GPS_dt.isoformat())))
            results['GPSDateTime'] = GPS_dt

        # Remove erroneous date value produced by "OnePlus X" as of 2016-04-13.
        # https://forums.oneplus.net/threads/2002-12-08-exif-date-problem.104599/
        bad_exif_date = datetime.strptime("2002-12-08_12:00:00", "%Y-%m-%d_%H:%M:%S")
        try:
            if self.exif_data['Make'] == 'OnePlus' and self.exif_data['Model'] == 'ONE E1003':
                if results['DateTimeDigitized'] == bad_exif_date:
                    logging.debug("Removing erroneous date \"%s\"" % str(bad_exif_date))
                    del results['DateTimeDigitized']
        except KeyError:
            logging.warn('KeyError for key [DateTimeDigitized]')
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
            filename = self.fileObject.get_path()
            image = Image.open(filename)
            exif_data = image._getexif()
        except Exception:
            logging.warning('Unable to extract EXIF data from \"{}\"' % str(filename))
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
