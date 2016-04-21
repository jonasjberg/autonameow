from __future__ import print_function

import logging
import pprint
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

from analyze.common import AnalyzerBase
from util.fuzzy_date_parser import DateParse


class ImageAnalyzer(AnalyzerBase):
    def __init__(self, fileObject):
        self.fileObject = fileObject
        self.exif_data = None

    def run(self):
        """
        Run the analysis.
        """
        if self.exif_data is None:
            self.exif_data = self.get_EXIF_data()

        exif_datetime = self.get_EXIF_datetime()
        self.fileObject.timestamps.append(exif_datetime)
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(exif_datetime)

    def get_datetime(self):
        datetime = self.get_EXIF_datetime()

        if datetime is None:
            logging.warning('Unable to extract datetime.')
        else:
            return datetime

    def get_EXIF_datetime(self):
        """
        Extracts date and time information from the EXIF data.
        The EXIF data could be corrupted or contain non-standard entries.
        Extraction should be fault-tolerant and able to handle non-standard
        entry formats.
        :return: Touple of datetime objects representing date and time.
        """
        # Use "brute force"-type date parser everywhere?
        # Probably not necessary. Could possible handle some edges cases.
        # Performance could become a problem at scale ..
        # TODO: Investigate date parser types, etc..
        parser = DateParse()

        DATE_TAG_FIELDS = ['DateTimeOriginal', 'DateTimeDigitized',
                           'DateTimeModified', 'CreateDate']
        results = {}
        for field in DATE_TAG_FIELDS:
            date = time = None
            try:
                date, time = self.exif_data[field].split()
            except KeyError, TypeError:
                pass

            clean_date = parser.date(date)
            clean_time = parser.time(time)

            if clean_date and clean_time:
                results[field] = (clean_date, clean_time)

        GPS_date = GPS_time = None
        try:
            GPS_date = self.exif_data['GPSDateStamp']
            GPS_time = self.exif_data['GPSTimeStamp']
        except KeyError:
            pass

        if GPS_time:
            GPS_time_str = ''
            for toup in GPS_time:
                GPS_time_str += str(toup[0])
            #GPS_time_detoupled = str(GPS_time[0][0]) + str(GPS_time[1][0]) + str(GPS_time[2][0])
            #clean_GPS_date = parser.date(GPS_date)
            #clean_GPS_time = parser.time(GPS_time)

        if clean_date and clean_time:
            results['GPSDateTime'] = (clean_date, clean_time)

        # Remove erroneous date value produced by "OnePlus X" as of 2016-04-13.
        # https://forums.oneplus.net/threads/2002-12-08-exif-date-problem.104599/
        try:
            if self.exif_data['Make'] == 'OnePlus' and \
               self.exif_data['Model'] == 'ONE E1003':
                if results['DateTimeDigitized'] == '2002:12:08 12:00:00':
                    logging.debug("Removing erroneous EXIF date \"2002:12:08 12:00:00\"")
                    self.exif_data['DateTimeDigitized'] = None
        except KeyError:
            pass

        return results

        # FORMAT='%-20.20s | %-10.10s | %-8.8s'
        # print(FORMAT % ("EXIF FIELD", "Date", "Time"))
        # print(FORMAT % (field, clean_date, clean_time))


    def get_EXIF_data(self):
        """
        Extracts EXIF information from a image using PIL.
        The EXIF data is stored in a dict using human-readable keys.
        :return: Dict of EXIF data.
        """

        # Create empty dictionary to store exif "key:value"-pairs in.
        result = {}

        exif_data = None

        # Extract EXIF data using PIL.ExifTags.
        try:
            filename = self.fileObject.get_path()
            image = Image.open(filename)
            exif_data = image._getexif()
        except Exception:
            print("EXIF data extraction error")

        if exif_data:
            for tag, value in exif_data.items():
                # Obtain a human-readable version of the tag.
                tagString = TAGS.get(tag, tag)

                # Check if tag contains GPS data.
                if tagString == "GPSInfo":
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
