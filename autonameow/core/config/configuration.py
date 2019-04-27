# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2019 Jonas Sjöberg <autonameow@jonasjberg.com>
#   Source repository: https://github.com/jonasjberg/autonameow
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
from util import coercers
from util import disk
from util import text


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
                log.warning('Loaded configuration created by %s (currently running %s)',
                            self.version, C.STRING_PROGRAM_VERSION)
                log.info(
                    'The currently recommended way to migrate to a new version'
                    'is to move the current config to a temporary location, '
                    're-run the program so that a new template config file is '
                    'generated and then manually merge the old rules back into '
                    'the new file, while making any necessary adjustments to '
                    'accommodate any changes in syntax, naming, etc.'
                )
                # TODO: Handle migrating between configuration versions?

        if not self._rules:
            log.warning('Configuration does not contain any rules!')

    def get(self, key_list):
        assert isinstance(key_list, list)
        try:
            return _nested_dict_get(self._options, *key_list)
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

    def __str__(self):
        # TODO: [cleanup][hack] This is pretty bad ..
        out = ['autonameow version {}\n\n'.format(self.version)]

        for n, rule in enumerate(self.rules, start=1):
            out.append('Rule {}/{}:\n'.format(n, len(self.rules)))
            out.append(text.indent(rule.stringify(), columns=4) + '\n')

        out.append('\nReusable Name Templates:\n')
        out.append(
            text.indent(_yaml_format(self.reusable_nametemplates), columns=4)
        )

        out.append('\nMiscellaneous Options:\n')
        out.append(text.indent(_yaml_format(self.options), columns=4))

        return ''.join(out)


def _yaml_format(data):
    return coercers.force_string(disk.write_yaml(data))


def _nested_dict_get(dictionary, *keys):
    """
    Retrieves a value from a given nested dictionary structure.

    The structure is traversed by accessing each key in the given list
    of keys in order.

    Args:
        dictionary: The dictionary structure to traverse.
        keys: Iterable of keys to use during the traversal.

    Returns:
        The value in the nested structure, if successful.

    Raises:
        KeyError: Failed to retrieve any value with the given list of keys.
    """
    assert isinstance(dictionary, dict)

    for key in keys:
        try:
            dictionary = dictionary[key]
        except TypeError:
            raise KeyError('Thing is not subscriptable (traversed too deep?)')

    return dictionary
