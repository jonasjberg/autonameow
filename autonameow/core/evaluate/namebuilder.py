# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

import os

from core.fileobject import FileObject


class NameBuilder(object):
    """
    Builds a new filename for a FileObject from a set of rules.
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

    def _populate_fields(self, analysis_results, rule):
        """
        Assembles a dict with keys matching the fields in the new name template
        defined in the rule. The dict values come from the analysis results,
        which ones is also defined in the rule.
        :param analysis_results:
        :return:
        """
        print(analysis_results)
        ardate = None #rule['prefer_datetime']
        artime = None
        artitle = None
        artags = None

        populated_fields = {
            'date': ardate or None,
            'time': artime or None,
            'description': artitle or None,
            'tags': artags or None,
            'ext': os.path.extsep + self.file_object.filenamepart_ext
        }
        return populated_fields

    def _fill_template(self, populated_fields, rule):
        # TODO: Finish this method. Very much a work in progress.
        return rule['new_name_template'] % populated_fields

    def build(self):
        fields = self._populate_fields(self.analysis_results, self.rule)
        self.new_name = self._fill_template(fields, self.rule)
        print((self.new_name))
