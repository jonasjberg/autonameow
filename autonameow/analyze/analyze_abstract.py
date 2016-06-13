# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

import logging


class AbstractAnalyzer(object):
    def __init__(self, file_object, filters):
        self.file_object = file_object
        self.filters = filters

    def get_datetime(self):
        raise NotImplementedError

    def get_title(self):
        raise NotImplementedError

    def get_author(self):
        raise NotImplementedError

    # def run(self):
    #     """
    #     Run the analysis.
    #     """

