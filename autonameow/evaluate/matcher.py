# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.
import logging
import re


class RuleMatcher(object):
    def __init__(self, file_object, rules):
        self.file_object = file_object
        self.rules = rules

    def _determine_ruleset_for_file(self):
        file_type = self.file_object.type
        file_name = self.file_object.basename

        for rule in self.rules:
            if rule['type'] is not file_type:
                continue

            elif 'name' in rule:
                try:
                    name_regex = re.compile(rule['name'])
                except re.error as e:
                    logging.error('Invalid regex pattern in configuration file:'
                                  ' "{}" (Error: {})'.format(rule['name'], e))
                else:
                    if not name_regex.match(file_name):
                        continue




    # for cpattern in Config['filename_patterns']:
    #     try:
    #         cregex = re.compile(cpattern, re.VERBOSE)
    #     except re.error as errormsg:
    #         warn(
    #             "WARNING: Invalid episode_pattern (error: %s)\nPattern:\n%s" % (
    #                 errormsg, cpattern))
    #     else:
    #         self.compiled_regexs.append(cregex)

