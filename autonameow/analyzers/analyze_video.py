# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg
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


from analyzers import BaseAnalyzer


class VideoAnalyzer(BaseAnalyzer):
    RUN_QUEUE_PRIORITY = 0.1
    HANDLES_MIME_TYPES = ['video/*']

    # TODO: [TD0157] Look into analyzers 'FIELD_LOOKUP' attributes.

    def __init__(self, fileobject, config, request_data_callback):
        super().__init__(fileobject, config, request_data_callback)

    def analyze(self):
        # TODO: [TD0055] Implement the video analyzer.
        pass

    # NOTE: Look into using "ffprobe" to get video data.
    #       Can it provide information not covered by "exiftool"?
    # NOTE: If using "ffprobe", add it as a new extractor class!

    @classmethod
    def check_dependencies(cls):
        return True
