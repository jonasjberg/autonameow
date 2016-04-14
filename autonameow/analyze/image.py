from __future__ import print_function
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

from analyze.analyzer import AnalyzerBase
from analyze.fuzzy_date_parser import DateParse

import pprint


class ImageAnalyzer(AnalyzerBase):
    def __init__(self, fileObject):
        self.fileObject = fileObject
        self.exif_data = self.get_EXIF_data()

    def run(self):
        self.get_EXIF_datetime()
        # print(self.exif_data)

    def get_EXIF_datetime(self):
        # Use "brute force"-type date parser everywhere?
        # Probably not necessary. Could possible handle some edges cases.
        # Performance could become a problem at scale ..
        # TODO: Investigate date parser types, etc..
        parser = DateParse()

        DATE_TAG_FIELDS = ['DateTimeOriginal', 'DateTimeDigitized',
                           'DateTimeModified', 'CreateDate']
        results = {}
        for field in DATE_TAG_FIELDS:
            try:
                date, time = self.exif_data[field].split()
                clean_date = parser.date(date)
                clean_time = parser.time(time)
            except KeyError:
                pass

            if clean_date and clean_time:
                results[field] = (clean_date, clean_time)

        try:
            GPS_date = self.exif_data["GPSDateStamp"]
            GPS_time = self.exif_data["GPSTimeStamp"]

            GPS_time_str = ''
            for toup in GPS_time:
                GPS_time_str += str(toup[0]))
            #GPS_time_detoupled = str(GPS_time[0][0]) + str(GPS_time[1][0]) + str(GPS_time[2][0])
            #print(GPS_time_detoupled)
            #clean_GPS_date = parser.date(GPS_date)
            #clean_GPS_time = parser.time(GPS_time)
        except KeyError:
            pass

        if clean_date and clean_time:
            results[field] = (clean_date, clean_time)


        #pp = pprint.PrettyPrinter(indent=4)
        #pp.pprint(results)
        #    FORMAT='%-20.20s | %-10.10s | %-8.8s'
        #    print(FORMAT % ("EXIF FIELD", "Date", "Time"))
        #    print(FORMAT % (field, clean_date, clean_time))

                # dateTimeOriginal = parser.date(origdate)

                # TODO: implement function parser.time()
                # dateTimeOriginal = parser.time(origtime)

                # print('dateTimeOriginal: {}'.format(dateTimeOriginal))

                # print(str(self.exif_data))

                # # Remove erroneous date value produced by "OnePlus X" as of 2016-04-13.
                # # https://forums.oneplus.net/threads/2002-12-08-exif-date-problem.104599/
                # if self.exif_data['Make'] == 'OnePlus' and self.exif_data['Model'] == 'ONE E1003':
                #     if self.exif_data['DateTimeDigitized'] == '2002:12:08 12:00:00':
                #         print "Removing erroneous EXIF date \"2002:12:08 12:00:00\""
                #         self.exif_data['DateTimeDigitized'] = None

                # for d in self.exif_data.values():
                #    print(d)

                # dateTimeOriginal = "NA"
                # dateTimeDigitized = "NA"
                # createDate = "NA"
                # dateTime = "NA"
                # cameraModel = "NA"
                # cameraMake = "NA"
                #
                # # Collect basic image data if available
                # if tagString == 'DateTimeOriginal':
                #     dateTimeOriginal = exifData.get(tag)
                #
                #     # # check the tag for GPS
                #     # if tagString == "GPSInfo":
                #     #
                #     #     # Create dictionary to hold the GPS data
                #     #     gpsDictionary = {}
                #     #
                #     #     # Loop through the GPS information
                #     #     for curTag in value:
                #     #         gpsTag = GPSTAGS.get(curTag, curTag)
                #     #         gpsDictionary[gpsTag] = value[curTag]
                #
                #     # return gpsDictionary, basicEXIFData
                #
                # # Remove erroneous date value produced by "OnePlus X" as of 2016-04-13.
                # # https://forums.oneplus.net/threads/2002-12-08-exif-date-problem.104599/
                # if cameraMake == 'OnePlus' and cameraModel == 'ONE E1003':
                #     if dateTimeDigitized == '2002:12:08 12:00:00':
                #         dateTimeDigitized = None
                #
                # dateEXIFdata = [dateTimeOriginal, dateTimeDigitized, createDate, dateTime]
                # deviceEXIFdata = [cameraMake, cameraModel]

    def get_EXIF_data(self):
        # Create empty dictionary to store exif "key:value"-pairs in.
        result = {}

        # Extract EXIF data using PIL.ExifTags.
        try:
            filename = self.fileObject.get_path()
            image = Image.open(filename)
            exifData = image._getexif()
        except Exception:
            print("EXIF data extraction error")

        if exifData:
            for tag, value in exifData.items():
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

            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(result)


        return result
