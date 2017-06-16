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
#   the Free Software Foundation.
#
#   autonameow is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with autonameow.  If not, see <http://www.gnu.org/licenses/>.

from analyzers.analyzer import Analyzer


class VideoAnalyzer(Analyzer):
    run_queue_priority = 0.1

    def __init__(self, file_object, add_results_callback, extracted_data):
        super(VideoAnalyzer, self).__init__(
            file_object, add_results_callback, extracted_data
        )
        self.applies_to_mime = 'mp4'

    def run(self):
        # TODO: Remove, use callbacks instead.
        pass

    def get_author(self):
        # TODO: Remove, use callbacks instead.
        pass

    def get_title(self):
        # TODO: Remove, use callbacks instead.
        pass

    def get_datetime(self):
        # TODO: Remove, use callbacks instead.
        pass

    def get_publisher(self):
        # TODO: Remove, use callbacks instead.
        pass

    def get_tags(self):
        # TODO: Remove, use callbacks instead.
        pass

    # NOTE: Look into using "ffprobe" to get video data.
    #       Can it provide information not covered by "exiftool"?
    # NOTE: If using "ffprobe", add it as a new extractor class!
