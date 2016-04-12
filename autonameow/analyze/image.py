from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

from analyze.analyzer import AnalyzerBase


class ImageAnalyzer(AnalyzerBase):
    def __init__(self, fileObject):
        self.fileObject = fileObject


    def run(self):
        self.get_timestamp()


    def get_timestamp(self):
        exif_data = self.get_EXIF_data()
        print(exif_data)

    def get_EXIF_data(self):
        filename = self.fileObject.get_path()
        try:
            imgFile = Image.open(filename)
            exifData = imgFile._getexif()
        except Exception:
            print "exif data extraction error"
            return None, None

        dateTimeOriginal = "NA"
        dateTimeDigitized = "NA"
        createDate = "NA"
        dateTime = "NA"
        cameraModel = "NA"
        cameraMake = "NA"

        if exifData:
            for tag, theValue in exifData.items():
                # obtain the tag
                tagValue = TAGS.get(tag, tag)

                # print("{} : {} : {}").format(tag, tagValue, theValue)

                # Collect basic image data if available
                if tagValue == 'DateTimeOriginal':
                    dateTimeOriginal = exifData.get(tag)

                if tagValue == 'DateTimeDigitized':
                    dateTimeDigitized = exifData.get(tag)

                if tagValue == 'CreateDate':
                    createDate = exifData.get(tag)

                if 'DateTime' in tagValue:
                    dateTime = exifData.get(tag)

                if tagValue == 'Make':
                    cameraMake = exifData.get(tag)

                if tagValue == 'Model':
                    cameraModel = exifData.get(tag)

                    # # check the tag for GPS
                    # if tagValue == "GPSInfo":
                    #
                    #     # Create dictionary to hold the GPS data
                    #     gpsDictionary = {}
                    #
                    #     # Loop through the GPS information
                    #     for curTag in theValue:
                    #         gpsTag = GPSTAGS.get(curTag, curTag)
                    #         gpsDictionary[gpsTag] = theValue[curTag]

                    # return gpsDictionary, basicEXIFData

            # Remove erroneous date value produced by "OnePlus X" as of 2016-04-13.
            # https://forums.oneplus.net/threads/2002-12-08-exif-date-problem.104599/
            if cameraMake == 'OnePlus' and cameraModel == 'ONE E1003':
                if dateTimeDigitized == '2002:12:08 12:00:00':
                    dateTimeDigitized = None

            basicEXIFData = [cameraMake, cameraModel, dateTimeOriginal, dateTimeDigitized, createDate, dateTime]
            return basicEXIFData

        else:
            return None, None







