# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2017 Jonas Sjöberg
#   Personal site:   http://www.jonasjberg.com
#   GitHub:          https://github.com/jonasjberg
#   University mail: js224eh[a]student.lnu.se
#
#   This file is part of autonameow.
#
#   autonameow is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   autonameow is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with autonameow.  If not, see <http://www.gnu.org/licenses/>.

import logging
import os

from core.analyze.analyze_abstract import AbstractAnalyzer


class VideoAnalyzer(AbstractAnalyzer):
    # @Overrides attribute in AbstractAnalyzer
    run_queue_priority = 0.1

    def __init__(self, file_object):
        super(VideoAnalyzer, self).__init__(file_object)
        self.applies_to_mime = 'mp4'

        self.exif_data = None

    # @Overrides method in AbstractAnalyzer
    def run(self):
        # TODO: Implement.
        pass

    # @Overrides method in AbstractAnalyzer
    def get_author(self):
        # TODO: Implement.
        pass

    # @Overrides method in AbstractAnalyzer
    def get_title(self):
        # TODO: Implement.
        pass

    # @Overrides method in AbstractAnalyzer
    def get_datetime(self):
        # TODO: Implement.
        pass

    # @Overrides method in AbstractAnalyzer
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
                        logging.debug('Unable to extract date/time from ffprobe output.')
                    return dt
