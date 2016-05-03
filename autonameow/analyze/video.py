import logging
import os

from analyze.common import AnalyzerBase
from util.fuzzy_date_parser import DateParse


class VideoAnalyzer(AnalyzerBase):
    def __init__(self, file_object):
        self.fileObject = file_object
        self.exif_data = None

    def run(self):
        """
        Run the analysis.
        """
        # if self.exif_data is None:
        #     self.exif_data = self.get_EXIF_data()
        # exif_datetime = self.get_exif_datetime()

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
        # TODO: Extract EXIF data from video using exiftool?
        pass

    def get_EXIF_data(self):
        # TODO: Extract EXIF data from video using exiftool?
        pass

    def get_movie_creation_date(self):
        """
        Extract create date using "ffprobe".
        :return: Creation date/time as a datetime-object.
        """
        parser = DateParse()

        filename = self.fileObject.get_path()
        for line in os.popen('ffprobe -loglevel quiet -show_entries stream_tags=creation_time -i ' + filename).readlines():
            if line[:18] == 'TAG:creation_time=':
                datetime = line[18:]
                date, time = datetime.split()
                clean_date = parser.date(date)
                clean_time = parser.time(time)

                if clean_date and clean_time:
                    dt = None
                    try:
                        dt = datetime.combine(clean_date, clean_time)
                    except ValueError:
                        logging.warning('Unable to extract date/time from ffprobe output.')
                    return dt
