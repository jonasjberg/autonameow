# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg
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
import os
import re

from util import coercers
from util import disk


log = logging.getLogger(__name__)


_PATH_THIS_DIR = coercers.AW_PATH(os.path.abspath(os.path.dirname(__file__)))


# TODO: [TD0189] Canonicalize metadata values with direct replacements


def _relative_absolute_path(basename):
    bytestring_basename = coercers.AW_PATHCOMPONENT(basename)
    return disk.joinpaths(_PATH_THIS_DIR, bytestring_basename)


class StringValueCanonicalizer(object):
    def __init__(self, value_lookup_dict, lookup_dict_filepath=None):
        if lookup_dict_filepath:
            str_lookup_dict_filepath = coercers.force_string(lookup_dict_filepath)
        else:
            str_lookup_dict_filepath = '(unknown filepath)'

        # Store original path for additional information when logging errors.
        self.str_lookup_dict_filepath = str(str_lookup_dict_filepath)
        self.canonical_value_regexes = self._parse_canonical_value_regexes(value_lookup_dict)

    def __call__(self, string):
        canonical_value = self._find_first_match(string)
        if canonical_value is None:
            return string
        return canonical_value

    def _find_first_match(self, string):
        lowercase_string = string.lower()

        for canonical_value, regexes in self.canonical_value_regexes.items():
            if lowercase_string == canonical_value.lower():
                return canonical_value

            if any(regex.match(string) for regex in regexes):
                return canonical_value

        return None

    def _parse_canonical_value_regexes(self, datadict):
        assert isinstance(datadict, dict)

        parsed_value_regexes = dict()
        for canonical, pattern_list in datadict.items():
            compiled_regexes = list()

            for pattern in pattern_list:
                try:
                    regex = re.compile(pattern, re.DOTALL | re.IGNORECASE)
                except re.error as e:
                    log.error('Invalid regex in "{!s}" :: '
                              '{!s}'.format(self.str_lookup_dict_filepath, e))
                    continue
                compiled_regexes.append(regex)

            if compiled_regexes:
                parsed_value_regexes[canonical] = compiled_regexes

        return parsed_value_regexes


def build_string_value_canonicalizer(yaml_config_filename):
    yaml_config_filepath = _relative_absolute_path(yaml_config_filename)
    config_data = disk.load_yaml_file(yaml_config_filepath)
    canonicalizer = StringValueCanonicalizer(config_data, yaml_config_filepath)
    return canonicalizer


_CANONICALIZER_PUBLISHER = build_string_value_canonicalizer(b'canonical_publisher.yaml')


def canonicalize_publisher(string):
    return _CANONICALIZER_PUBLISHER(string)
