# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2017 Jonas Sjöberg
#   Personal site:   http://www.jonasjberg.com
#   GitHub:          https://github.com/jonasjberg
#   University mail: js224eh[a]student.lnu.se
#
#   This file is part of autonameow.
#
#   autonameow is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation.
#
#   autonameow is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with autonameow.  If not, see <http://www.gnu.org/licenses/>.

import logging
import re


class RuleMatcher(object):
    """
    Handles matching of FileObjects to rules.

    Determines which rule, if any; applies to the given FileObject.

    Note:
        This class is in very bad shape and a work in progress.
        TODO: Fix everything! It's just all so very hacky! *SO SO VERY HACKY*
    """
    # TODO: [BL004] Implement reading user configuration from config files.
    def __init__(self, file_object, rules):
        """
        RuleMatcher initialization.

        Note:
            Matching starts straight away at instantiation.

        Args:
            file_object (FileObject): FileObject to match against rules
            rules (dict): set of all available rules
        """
        self.file_object = file_object
        self.rules = rules
        logging.debug('Initialized RuleMatcher [{}] with rules '
                      '"{}"'.format(self.__str__(), self.rules))

        self._active_rule_key = self._determine_active_rule_key()
        if self._active_rule_key:
            logging.debug('File matches rule: '
                          '{}'.format(self._active_rule_key))
            self.active_rule = self.rules[self._active_rule_key]
        else:
            # TODO: Handle this case properly.
            #       NameBuilder (and others?) depend on this *NOT* being None.
            logging.debug('File does not match any rules.')
            self.active_rule = None

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


