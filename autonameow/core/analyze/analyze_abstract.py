# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

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
                logging.warning('Called unimplemented code')
                return None
        else:
            logging.error('Invalid get parameter: {}'.format(str(field)))
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
