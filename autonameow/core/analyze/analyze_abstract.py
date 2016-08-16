# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.


class AbstractAnalyzer(object):
    def __init__(self, file_object):
        self.file_object = file_object

    def get_datetime(self):
        raise NotImplementedError

    def get_title(self):
        raise NotImplementedError

    def get_author(self):
        raise NotImplementedError

    def get_tags(self):
        raise NotImplementedError

    # def run(self):
    #     """
    #     Run the analysis.
    #     """

