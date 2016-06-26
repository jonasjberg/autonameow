# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.
import logging
import re


class RuleMatcher(object):
    def __init__(self, file_object, rules):
        self.file_object = file_object
        self.rules = rules

        self.use_rule = self._determine_ruleset_for_file()

    def _determine_ruleset_for_file(self):
        file_type = self.file_object.type
        file_name = self.file_object.basename

        for rule in self.rules:
            if rule['type'] is not file_type:
                # Rule does not apply -- file type differs.
                continue

            elif 'name' in rule:
                if rule['name'] is not None:
                    try:
                        name_regex = re.compile(rule['name'])
                    except re.error as e:
                        logging.critical('Invalid regex pattern in '
                                         'configuration file: "{}" '
                                         '(Error: {})'.format(rule['name'], e))
                        # Rule does not apply -- regex not valid.
                        #                        (would be unsafe to continue)
                        continue
                    else:
                        if not name_regex.match(file_name):
                            # Rule does not apply -- regex does not match.
                            continue

