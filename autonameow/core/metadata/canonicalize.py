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

from core.truths import known_data_loader
from util.text import regexbatch


class StringValueCanonicalizer(object):
    """
    Uses any or more fixed patterns do string value canonicalization.
    Search patterns used by this class is typically loaded from YAML files.

    The matching works as follows:

    1) All canonical values are matched against the incoming value,
       ignoring any differences in letter case. This means that all letter
       case variations of an incoming value 'english' will be replaced with
       the canonical form 'ENGLISH', even if these variations are not listed
       explicitly in any of the passed in search patterns.
    2) Then the 'match_any_literal' entries are matched against the value.
       This matching is case-sensitive and includes whitespace, etc.
    3) And finally, any regex entries are matched against the value.
       In case of conflicting matches, the canonical form with the longest
       total match length is used.

    The canonical form of the first successful match is used, which probably
    means that listing common patterns as literal values *might* possibly be
    more efficient than only using the regular expressions.
    """
    def __init__(self, literal_lookup_dict, regex_lookup_dict):
        assert isinstance(literal_lookup_dict, dict)
        assert isinstance(regex_lookup_dict, dict)
        self.canonical_value_literals = literal_lookup_dict
        self.canonical_value_regexes = regex_lookup_dict

        # Store all canonical values in a dict keyed by lower-case canonical
        # values, each storing the original letter case version of itself.
        #
        #     all_canonical_values_lowercase_keys = {
        #         'foo bar': 'Foo Bar',
        #         'baz': 'BAZ',
        #     }
        #
        # This is to be able to compare incoming lower-cased values to the
        # lower-cased canonical form but still return the canonical value with
        # its original letter case as the result.
        all_canonical_values = set(self.canonical_value_regexes.keys())
        all_canonical_values.update(self.canonical_value_literals.keys())
        self.all_canonical_values_lowercase_keys = {
            v.lower(): v for v in all_canonical_values
        }

    def __call__(self, s):
        """
        Returns a canonical representation if the given value if found.
        If no canonical value is found, the given value is returned as-is.
        """
        canonical_value = self._find_canonical_value(s)
        if canonical_value is None:
            return s

        return canonical_value

    def _find_canonical_value(self, s):
        assert isinstance(s, str)

        # Check if the given value is equal to any canonical value when
        # disregarding differences in letter case.
        matched_canonical_value = self._find_literal_ignorecase_match(s)
        if matched_canonical_value:
            return matched_canonical_value

        # Do literal string comparison.
        for canonical_value, literal_patterns in self.canonical_value_literals.items():
            if s in literal_patterns:
                return canonical_value

        # Do regex matching.
        canonical_form = regexbatch.find_replacement_value(
            value_regexes=self.canonical_value_regexes,
            strng=s,
        )
        if canonical_form:
            return canonical_form

        return None

    def _find_literal_ignorecase_match(self, s):
        lowercase_string = s.lower()
        if lowercase_string not in self.all_canonical_values_lowercase_keys:
            return None

        return self.all_canonical_values_lowercase_keys[lowercase_string]


def build_string_value_canonicalizer(yaml_config_filename):
    literal_lookup_dict = known_data_loader.literal_lookup_dict(yaml_config_filename)
    regex_lookup_dict = known_data_loader.regex_lookup_dict(yaml_config_filename)

    canonicalizer = StringValueCanonicalizer(literal_lookup_dict, regex_lookup_dict)
    return canonicalizer


_CANONICALIZER_PUBLISHER = build_string_value_canonicalizer('publisher')
_CANONICALIZER_LANGUAGE = build_string_value_canonicalizer('language')
_CANONICALIZER_CREATORTOOL = build_string_value_canonicalizer('creatortool')


def canonicalize_publisher(string):
    return _CANONICALIZER_PUBLISHER(string)


def canonicalize_language(string):
    return _CANONICALIZER_LANGUAGE(string)


def canonicalize_creatortool(string):
    return _CANONICALIZER_CREATORTOOL(string)
