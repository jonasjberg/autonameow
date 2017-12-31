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

from core import constants as C
from util import (
    dump,
    nested_dict_get,
    text
)


log = logging.getLogger(__name__)


class Configuration(object):
    """
    Container for validated configuration data, typically loaded from a file.
    """
    def __init__(self, options, rules_, reusable_nametemplates, version):
        self._rules = list(rules_)
        self._reusable_nametemplates = dict(reusable_nametemplates)

        self._options = {'DATETIME_FORMAT': {},
                         'FILETAGS_OPTIONS': {}}
        self._options.update(options)

        self._version = version

        if self.version:
            if self.version != C.STRING_PROGRAM_VERSION:
                log.warning('Possible configuration compatibility mismatch!')
                log.warning('Loaded configuration created by {} (currently '
                            'running {})'.format(self.version,
                                                 C.STRING_PROGRAM_VERSION))
                log.info(
                    'The current recommended procedure is to move the '
                    'current config to a temporary location, re-run '
                    'the program so that a new template config file is '
                    'generated and then manually transfer rules to this file.'
                )

        self.referenced_meowuris = set()
        for rule in self._rules:
            # Keep track of all "meowURIs" referenced by rules.
            self.referenced_meowuris.update(rule.referenced_meowuris())

        # For Debugging/development only.
        _referenced_meowuris = sorted(self.referenced_meowuris)
        for _meowuri in _referenced_meowuris:
            log.debug('Configuration Rule referenced meowURI'
                      ' "{!s}"'.format(_meowuri))

    def get(self, key_list):
        try:
            return nested_dict_get(self._options, key_list)
        except KeyError:
            return None

    @property
    def version(self):
        """
        Returns:
            The version number of the program that wrote the configuration as
            a Unicode string, if it is available.  Otherwise None.
        """
        if self._version:
            return 'v' + '.'.join(map(str, self._version))
        return None

    @property
    def options(self):
        """
        Public interface for configuration options.
        Returns:
            Current and valid configuration options.
        """
        return self._options

    @property
    def rules(self):
        return list(self._rules)

    @property
    def reusable_nametemplates(self):
        return self._reusable_nametemplates

    @property
    def name_templates(self):
        _rule_templates = [r.name_template for r in self.rules]
        _reusable_templates = [t for t in self.reusable_nametemplates.values()]
        return _rule_templates + _reusable_templates

    def __str__(self):
        out = ['Written by autonameow version v{}\n\n'.format(self.version)]

        for number, rule in enumerate(self.rules):
            out.append('Rule {}:\n'.format(number + 1))
            out.append(text.indent(str(rule), amount=4) + '\n')

        out.append('\nReusable Name Templates:\n')
        out.append(
            text.indent(dump(self.reusable_nametemplates), amount=4)
        )

        out.append('\nMiscellaneous Options:\n')
        out.append(text.indent(dump(self.options), amount=4))

        return ''.join(out)
