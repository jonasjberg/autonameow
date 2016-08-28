# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

import logging
import re


class RuleMatcher(object):
    def __init__(self, file_object, rules):
        self.file_object = file_object
        self.rules = rules
        logging.debug('Initialized RuleMatcher [{}] with rules '
                      '"{}"'.format(self.__str__(), self.rules))

        self._active_rule_key = self._determine_active_rule_key()
        logging.debug('File matches rule: '
                      '{}'.format(self._active_rule_key))
        if self._active_rule_key:
            self.active_rule = self.rules[self._active_rule_key]

    def _determine_active_rule_key(self):
        # rules = self.rules.
        for rule in self.rules.keys():
            does_match = False
            # print('rule: {} (type: {})'.format(self.rules[rule], type(self.rules[rule])))

            if 'type' in self.rules[rule]:
                ok = False
                this_type = self.rules[rule]['type']
                if isinstance(this_type, list):
                    for t in this_type:
                        if t == self.file_object.type:
                            ok = True
                            break
                else:
                    if this_type == self.file_object.type:
                        ok = True
                if ok:
                    does_match = True
                else:
                    # Rule does not apply -- file type differs.
                    # logging.debug('Rule [{:<20}] type "{}" does not match file '
                    #               'type "{}"'.format(rule,
                    #                             self.file_object.type,
                    #                             self.rules[rule]['type']))
                    continue
            else:
                logging.debug('Rule [{:<20}] does not specify "type"'.format(rule))

            if 'name' in self.rules[rule]:
                if self.rules[rule]['name'] is not None:
                    try:
                        name_regex = re.compile(self.rules[rule]['name'])
                    except re.error as e:
                        logging.critical('Invalid regex pattern in '
                                         'rule [{:<20}]: "{}" '
                                         '(Error: {})'.format(self.rules[rule], self.rules[rule]['name'], e))
                        # Rule does not apply -- regex not valid.
                        #                        (would be unsafe to continue)
                        continue
                    else:
                        if name_regex.match(self.file_object.filename):
                            does_match = True
                        else:
                            # Rule does not apply -- regex does not match.
                            logging.debug('Name regex in rule does not match')
                            continue
                else:
                    does_match = True

            if 'path' in self.rules[rule]:
                # TODO: Path matching. Use regex here as well?
                if self.rules[rule]['path'] is not None:
                    try:
                        pass
                    except Exception:
                        pass
                    else:
                        pass
                else:
                    does_match = True

            if does_match:
                logging.debug('Rule [{:<20}] matches file '
                              '"{}"'.format(rule,
                                            self.file_object.path))
                return rule
            else:
                return None


