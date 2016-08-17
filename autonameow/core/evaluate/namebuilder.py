# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

from core.fileobject import FileObject


class NameBuilder(object):
    """
    Builds a new filename for a given FileObject and a rule (set of rules).
    The 'rule' contains a 'new_name_template', which is filled out with data
    from 'analysis_results'.
    The rule also specifies which data from 'analysis_results' is to be used.
    """
    def __init__(self, file_object, analysis_results, rule):
        assert isinstance(file_object, FileObject)
        # assert isinstance(analysis_results, dict)
        # assert isinstance(rule, dict)

        self.file_object = file_object
        self.analysis_results = analysis_results
        self.rule = rule

        self.new_name = None

    def build(self):
        if self.rule is None:
            return False
        elif self.analysis_results is None:
            return False

        print(self.rule)
        print(self.analysis_results)


        self.new_name = self.rule['new_name_template']
        # TODO: Finish this method. Very much a work in progress.
