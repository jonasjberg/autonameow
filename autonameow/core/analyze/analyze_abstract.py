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

import logging


class AbstractAnalyzer(object):
    run_queue_priority = None

    def __init__(self, file_object):
        self.file_object = file_object
        self.applies_to_mime = None

    def run(self):
        raise NotImplementedError

    def get(self, field):
        func_name = 'get_{}'.format(field)

        get_func = getattr(self, func_name, None)
        if callable(get_func):
            try:
                return get_func()
            except NotImplementedError as e:
                logging.warning('Called unimplemented code: {}'.format(func_name))
                return None
        else:
            logging.error('Invalid get parameter: {!s}'.format(field))
            return None

    def get_datetime(self):
        raise NotImplementedError

    def get_title(self):
        raise NotImplementedError

    def get_author(self):
        raise NotImplementedError

    def get_tags(self):
        raise NotImplementedError

    def get_publisher(self):
        raise NotImplementedError
