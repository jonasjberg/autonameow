# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.


class AbstractAction(object):
    def __init__(self, file_object, results):
        self.file_object = file_object
        self.results = results

    def perform_action(self):
        raise NotImplementedError

