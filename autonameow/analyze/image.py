from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

from analyze.analyzer import AnalyzerBase
from analyze.fuzzy_date_parser import DateParse


class ImageAnalyzer(AnalyzerBase):
    def __init__(self, fileObject):
        self.fileObject = fileObject
        self.exif_data = self.get_EXIF_data()
        # print(exif_data)


    def run(self):
        self.get_EXIF_datetime()


    def get_EXIF_datetime(self):
        parser = DateParse()

        print(str(self.exif_data))

        # # Remove erroneous date value produced by "OnePlus X" as of 2016-04-13.
        # # https://forums.oneplus.net/threads/2002-12-08-exif-date-problem.104599/
        # if self.exif_data['Make'] == 'OnePlus' and self.exif_data['Model'] == 'ONE E1003':
        #     if self.exif_data['DateTimeDigitized'] == '2002:12:08 12:00:00':
        #         print "Removing erroneous EXIF date \"2002:12:08 12:00:00\""
        #         self.exif_data['DateTimeDigitized'] = None


        for d in self.exif_data.values():
            print(d)


        # dateTimeOriginal = "NA"
        # dateTimeDigitized = "NA"
        # createDate = "NA"
        # dateTime = "NA"
        # cameraModel = "NA"
        # cameraMake = "NA"
        #
        # # Collect basic image data if available
        # if tagValue == 'DateTimeOriginal':
        #     dateTimeOriginal = exifData.get(tag)
        #
        # if tagValue == 'DateTimeDigitized':
        #     dateTimeDigitized = exifData.get(tag)
        #
        # if tagValue == 'CreateDate':
        #     createDate = exifData.get(tag)
        #
        # if 'DateTime' in tagValue:
        #     dateTime = exifData.get(tag)
        #
        # if tagValue == 'Make':
        #     cameraMake = exifData.get(tag)
        #
        # if tagValue == 'Model':
        #     cameraModel = exifData.get(tag)
        #
        #     # # check the tag for GPS
        #     # if tagValue == "GPSInfo":
        #     #
        #     #     # Create dictionary to hold the GPS data
        #     #     gpsDictionary = {}
        #     #
        #     #     # Loop through the GPS information
        #     #     for curTag in theValue:
        #     #         gpsTag = GPSTAGS.get(curTag, curTag)
        #     #         gpsDictionary[gpsTag] = theValue[curTag]
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
        filename = self.fileObject.get_path()
        try:
            imgFile = Image.open(filename)
            exifData = imgFile._getexif()
        except Exception:
            print "EXIF data extraction error"
            return None, None

        if exifData:
            exif_data = dict()
            for tag, theValue in exifData.items():
                # obtain the tag
                tagValue = TAGS.get(tag, tag)

                # print("{} : {} : {}").format(tag, tagValue, theValue)

                data = exifData.get(tag)
                if data is not None:
                    exif_data[tagValue] = data

            return exif_data

        else:
            return None, None







