# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg <autonameow@jonasjberg.com>
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
import os
import re
from collections import defaultdict

from util import coercers
from util import disk


log = logging.getLogger(__name__)


_PATH_THIS_DIR = coercers.AW_PATH(os.path.abspath(os.path.dirname(__file__)))


# TODO: [TD0189] Canonicalize metadata values with direct replacements


def _relative_absolute_path(basename):
    bytestring_basename = coercers.AW_PATHCOMPONENT(basename)
    return disk.joinpaths(_PATH_THIS_DIR, bytestring_basename)


class StringValueCanonicalizer(object):
    def __init__(self, literal_lookup_dict, regex_lookup_dict):
        assert isinstance(literal_lookup_dict, dict)
        assert isinstance(regex_lookup_dict, dict)
        self.canonical_value_literals = literal_lookup_dict
        self.canonical_value_regexes = regex_lookup_dict

        # Store tuple of (LOWERCASED CANONICAL, CANONICAL) so that values
        # can be compared to the lowercased canonical and still return the
        # canonical value with its original letter case as the result.
        all_canonical_values = set(self.canonical_value_regexes.keys())
        all_canonical_values.update(self.canonical_value_literals.keys())
        self.all_canonical_values = set(
            (s.lower(), s) for s in all_canonical_values
        )

    def __call__(self, s):
        """
        Returns a canonical representation if the given value if found.
        If no canonical value is found, the given value is returned as-is.
        """
        assert isinstance(s, str)

        canonical_value = self._find_canonical_value(s)
        if canonical_value is None:
            return s

        return canonical_value

    def _find_canonical_value(self, s):
        # Check if the given value is equal to any canonical value when
        # disregarding differences in letter case.
        matched_canonical_value = self._find_exact_canonical_match(s)
        if matched_canonical_value:
            return matched_canonical_value

        # Do literal string comparison.
        for canonical_value, literal_patterns in self.canonical_value_literals.items():
            if s in literal_patterns:
                return canonical_value

        # Do regex matching.
        # Use canonical form with longest total length of matched substrings.
        matches = defaultdict(int)
        for canonical_value, regex_patterns in self.canonical_value_regexes.items():
            for regex in regex_patterns:
                matchiter = re.finditer(regex, s)
                for match in matchiter:
                    matched_substring = match.group(0)
                    matches[canonical_value] += len(matched_substring)

        if matches:
            canonical_form_of_longest_match = max(matches, key=matches.get)
            return canonical_form_of_longest_match

        return None

    def _find_exact_canonical_match(self, s):
        lowercase_string = s.lower()

        for lowercase_canonical_value, canonical_value in self.all_canonical_values:
            if lowercase_string == lowercase_canonical_value:
                return canonical_value

        return None


class CanonicalizerConfigParser(object):
    CONFIG_SECTION_MATCH_ANY_LITERAL = 'match_any_literal'
    CONFIG_SECTION_MATCH_ANY_REGEX = 'match_any_regex_ignorecase'

    def __init__(self, config_datadict, lookup_dict_filepath=None):
        assert isinstance(config_datadict, dict)
        self._datadict = config_datadict

        # Store original path for additional information when logging errors.
        if lookup_dict_filepath:
            str_lookup_dict_filepath = coercers.force_string(lookup_dict_filepath)
        else:
            str_lookup_dict_filepath = '(unknown)'
        self.str_lookup_dict_filepath = str(str_lookup_dict_filepath)

        self._parsed_literal_lookup = None
        self._parsed_regex_lookup = None

    @property
    def parsed_literal_lookup(self):
        if self._parsed_literal_lookup is None:
            self._parsed_literal_lookup = self._parse_literal_lookup()
        return self._parsed_literal_lookup

    @property
    def parsed_regex_lookup(self):
        if self._parsed_regex_lookup is None:
            self._parsed_regex_lookup = self._parse_regex_lookup()
        return self._parsed_regex_lookup

    def _parse_literal_lookup(self):
        literal_lookup = dict()

        for canonical_form, sections in self._datadict.items():
            assert isinstance(canonical_form, str)
            if not canonical_form.strip():
                continue

            if not isinstance(sections, dict):
                log.error('Invalid entry "{!s}" in "{!s}"'.format(sections, self.str_lookup_dict_filepath))
                continue

            literals_to_match = sections.get(self.CONFIG_SECTION_MATCH_ANY_LITERAL)
            if not literals_to_match:
                continue

            valid_literals_to_match = [s for s in literals_to_match if s and s.strip()]
            if valid_literals_to_match:
                literal_lookup[canonical_form] = set(valid_literals_to_match)

        return literal_lookup

    def _parse_regex_lookup(self):
        regex_lookup = dict()

        for canonical_form, sections in self._datadict.items():
            assert isinstance(canonical_form, str)
            if not canonical_form.strip():
                continue

            regexes_to_match = sections.get(self.CONFIG_SECTION_MATCH_ANY_REGEX)
            if not regexes_to_match:
                continue

            if not all(isinstance(s, str) for s in regexes_to_match):
                log.error('Bad syntax in "{!s}"'.format(self.str_lookup_dict_filepath))
                continue

            non_empty_regex_patterns = [s for s in regexes_to_match if s and s.strip()]
            if non_empty_regex_patterns:
                compiled_regexes = set()
                for pattern in non_empty_regex_patterns:
                    try:
                        regex = re.compile(pattern, re.IGNORECASE)
                    except re.error as e:
                        log.error('Invalid regex pattern "{!s}" in "{!s}" :: '
                                  '{!s}'.format(pattern, self.str_lookup_dict_filepath, e))
                        continue
                    compiled_regexes.add(regex)

                if compiled_regexes:
                    regex_lookup[canonical_form] = compiled_regexes

        return regex_lookup


def build_string_value_canonicalizer(yaml_config_filename):
    yaml_config_filepath = _relative_absolute_path(yaml_config_filename)
    config_data = disk.load_yaml_file(yaml_config_filepath)

    parser = CanonicalizerConfigParser(config_data, yaml_config_filepath)
    literal_lookup_dict = parser.parsed_literal_lookup
    regex_lookup_dict = parser.parsed_regex_lookup

    canonicalizer = StringValueCanonicalizer(literal_lookup_dict, regex_lookup_dict)
    return canonicalizer


_CANONICALIZER_PUBLISHER = build_string_value_canonicalizer(b'canonical_publisher.yaml')
_CANONICALIZER_LANGUAGE = build_string_value_canonicalizer(b'canonical_language.yaml')
_CANONICALIZER_CREATORTOOL = build_string_value_canonicalizer(b'canonical_creatortool.yaml')


def canonicalize_publisher(string):
    return _CANONICALIZER_PUBLISHER(string)


def canonicalize_language(string):
    return _CANONICALIZER_LANGUAGE(string)


def canonicalize_creatortool(string):
    return _CANONICALIZER_CREATORTOOL(string)
