# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.
import logging
import re

from util import misc


class RuleMatcher(object):
    def __init__(self, file_object, rules):
        self.file_object = file_object
        self.rules = rules
        logging.debug('Initialized RuleMatcher [{}] with rules "{}"'.format(self.__str__(), self.rules))

        print('self.rules (type: {}):'.format(type(self.rules)))
        print(misc.dump(self.rules))
        self.file_matches_rule = self._determine_rule_matching_file()

    def _determine_rule_matching_file(self):
        # rules = self.rules.
        for rule_name, rule_contents in self.rules.iteritems():
            does_match = False
            # print('rule: {} (type: {})'.format(self.rules[rule_name], type(self.rules[rule_name])))

            if 'type' in self.rules[rule_name]:
                if self.rules[rule_name]['type'] == self.file_object.type:
                    logging.debug('Rule [{}] matches [{}]'.format('type', self.file_object.type))
                    does_match = True
                else:
                    # Rule does not apply -- file type differs.
                    logging.debug('Rule [{}] does not match [{}]'.format('type', self.file_object.type))
                    does_match = True
                    continue
            else:
                print('no type in rule')

            if 'name' in self.rules[rule_name]:
                if self.rules[rule_name]['name'] is not None:
                    try:
                        name_regex = re.compile(self.rules[rule_name]['name'])
                    except re.error as e:
                        logging.critical('Invalid regex pattern in '
                                         'configuration file: "{}" '
                                         '(Error: {})'.format(self.rules[rule_name]['name'], e))
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

            if 'path' in self.rules[rule_name]:
                # TODO: Path matching. Use regex here as well?
                if self.rules[rule_name]['path'] is not None:
                    try:
                        pass
                    except Exception:
                        pass
                    else:
                        pass
                else:
                    does_match = True

            if does_match:
                return self.rules[rule_name]
            else:
                return None


