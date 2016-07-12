# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

import logging
import os

from analyze.analyze_abstract import AbstractAnalyzer


class VideoAnalyzer(AbstractAnalyzer):
    def __init__(self, file_object, filters):
        super(VideoAnalyzer, self).__init__(file_object, filters)

        self.exif_data = None

    def get_author(self):
        # TODO: Implement.
        pass

    def get_title(self):
        # TODO: Implement.
        pass
    def get_datetime(self):
        # TODO: Implement.
        pass

    def get_tags(self):
        # TODO: Implement.
        pass

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
        # TODO: This needs a serious looking over and most probably reworking.
        return None

        filename = self.fileObject.get_path()
        for line in os.popen('ffprobe -loglevel quiet -show_entries stream_tags=creation_time -i ' + filename).readlines():
            if line[:18] == 'TAG:creation_time=':
                datetime = line[18:]
                print(datetime)
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
