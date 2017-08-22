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

import logging as log

from analyzers import BaseAnalyzer


class VideoAnalyzer(BaseAnalyzer):
    run_queue_priority = 0.1
    handles_mime_types = ['video/*']
    meowuri_root = 'analysis.video'

    def __init__(self, file_object, add_results_callback,
                 request_data_callback):
        super(VideoAnalyzer, self).__init__(
            file_object, add_results_callback, request_data_callback
        )
        self.add_results = add_results_callback

    def _add_results(self, label, data):
        meowuri = 'analysis.video.{}'.format(label)
        log.debug('{} passed "{}" to "add_results" callback'.format(
            self, meowuri)
        )
        if data is not None:
            self.add_results(meowuri, data)

    def run(self):
        # Pass results through callback function provided by the 'Analysis'.
        self._add_results('author', self.get_author())
        self._add_results('title', self.get_title())
        self._add_results('datetime', self.get_datetime())
        self._add_results('publisher', self.get_publisher())
        self._add_results('tags', self.get_tags())

    def get_author(self):
        # TODO: [TD0055] Implement the video analyzer.
        pass

    def get_title(self):
        # TODO: [TD0055] Implement the video analyzer.
        pass

    def get_datetime(self):
        # TODO: [TD0055] Implement the video analyzer.
        pass

    def get_publisher(self):
        # TODO: [TD0055] Implement the video analyzer.
        pass

    def get_tags(self):
        # TODO: [TD0055] Implement the video analyzer.
        pass

    # NOTE: Look into using "ffprobe" to get video data.
    #       Can it provide information not covered by "exiftool"?
    # NOTE: If using "ffprobe", add it as a new extractor class!
