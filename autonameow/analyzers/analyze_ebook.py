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
from core import util


class EbookAnalyzer(BaseAnalyzer):
    run_queue_priority = 1
    handles_mime_types = ['application/pdf', 'application/epub+zip']
    meowuri_root = 'analysis.ebook'

    def __init__(self, file_object, add_results_callback,
                 request_data_callback):
        super(EbookAnalyzer, self).__init__(
            file_object, add_results_callback, request_data_callback
        )

    def run(self):
        self._text = self.request_data(self.file_object,
                                       'contents.textual.raw_text')

    def _add_results(self, meowuri_leaf, data):
        if data is None:
            return

        meowuri = '{}.{}'.format(self.meowuri_root, meowuri_leaf)
        log.debug(
            '{!s} passing "{}" to "add_results" callback'.format(self, meowuri)
        )
        self.add_results(meowuri, data)

    @classmethod
    def can_handle(cls, file_object):
        if util.eval_magic_glob(file_object.mime_type, cls.handles_mime_types):
            return True
        if (file_object.basename_suffix == b'mobi' and
                file_object.mime_type == 'application/octet-stream'):
            return True
        return False
