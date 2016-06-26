# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.
import logging
import re


class RuleMatcher(object):
    def __init__(self, file_object, rules):
        self.file_object = file_object
        self.rules = rules

        self.file_matches_rule = self._determine_rule_matching_file()

    def _determine_rule_matching_file(self):
        for rule in self.rules:
            does_match = False
            if rule['type'] == self.file_object.type:
                does_match = True
            else:
                # Rule does not apply -- file type differs.
                continue

            if 'name' in rule:
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
                        if name_regex.match(self.file_object.basename):
                            does_match = True
                        else:
                            # Rule does not apply -- regex does not match.
                            continue
                else:
                    does_match = True

            if 'path' in rule:
                # TODO: Path matching. Use regex here as well?
                if rule['path'] is not None:
                    try:
                        pass
                    except Exception:
                        pass
                    else:
                        pass
                else:
                    does_match = True

            if does_match:
                return rule
            else:
                return None


