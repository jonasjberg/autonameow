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

from core import exceptions
from util import coercers
from util import disk
from util import encoding as enc


log = logging.getLogger(__name__)


_PATH_THIS_DIR = coercers.AW_PATH(os.path.abspath(os.path.dirname(__file__)))


# TODO: [TD0189] Canonicalize metadata values with direct replacements


def _relative_absolute_path(basename):
    bytestring_basename = coercers.AW_PATHCOMPONENT(basename)
    return disk.joinpaths(_PATH_THIS_DIR, bytestring_basename)


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
        # lowercased canonical form but still return the canonical value with
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
        assert isinstance(s, str)

        canonical_value = self._find_canonical_value(s)
        if canonical_value is None:
            return s

        return canonical_value

    def _find_canonical_value(self, s):
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

    def _find_literal_ignorecase_match(self, s):
        lowercase_string = s.lower()
        if lowercase_string not in self.all_canonical_values_lowercase_keys:
            return None

        return self.all_canonical_values_lowercase_keys[lowercase_string]


class CanonicalizerConfigParser(object):
    CONFIG_SECTION_MATCH_ANY_LITERAL_CASESENSITIVE = 'match_any_literal'
    CONFIG_SECTION_MATCH_ANY_LITERAL_IGNORECASE = 'match_any_literal_ignorecase'
    # TODO: Implement 'match_any_literal_ignorecase'!
    CONFIG_SECTION_MATCH_ANY_REGEX_CASESENSITIVE = 'match_any_regex'
    CONFIG_SECTION_MATCH_ANY_REGEX_IGNORECASE = 'match_any_regex_ignorecase'

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

        # All patterns are stored with the 'canonical_form' as keys.
        for canonical_form, sections in self._datadict.items():
            assert isinstance(canonical_form, str)
            if not canonical_form.strip():
                continue

            if not isinstance(sections, dict):
                log.error('Invalid entry "%s" in "%s"', sections, self.str_lookup_dict_filepath)
                continue

            literals_to_match = sections.get(self.CONFIG_SECTION_MATCH_ANY_LITERAL_CASESENSITIVE)
            if not literals_to_match:
                continue

            valid_literals_to_match = [
                s for s in literals_to_match
                if s and isinstance(s, str) and s.strip()
            ]
            if valid_literals_to_match:
                literal_lookup[canonical_form] = set(valid_literals_to_match)

        return literal_lookup

    def _parse_regex_lookup(self):
        regex_lookup = dict()

        # All patterns are stored with the 'canonical_form' as keys.
        for canonical_form, sections in self._datadict.items():
            assert isinstance(canonical_form, str)
            if not canonical_form.strip():
                continue

            if not isinstance(sections, dict):
                log.error('Invalid entry "%s" in "%s"', sections, self.str_lookup_dict_filepath)
                continue

            all_compiled_regexes = set()

            def _process_patterns(_patterns_list, ignore_case):
                if not _patterns_list:
                    return

                assert isinstance(_patterns_list, list)
                _filtered_patterns = self._filter_non_empty_str(_patterns_list)
                if not _filtered_patterns:
                    return

                _regexes = self._compile_regexes(_filtered_patterns, ignore_case)
                all_compiled_regexes.update(_regexes)

            maybe_ignorecase_patterns = sections.get(self.CONFIG_SECTION_MATCH_ANY_REGEX_IGNORECASE)
            _process_patterns(maybe_ignorecase_patterns, ignore_case=True)

            maybe_casesensitive_patterns = sections.get(self.CONFIG_SECTION_MATCH_ANY_REGEX_CASESENSITIVE)
            _process_patterns(maybe_casesensitive_patterns, ignore_case=False)

            if all_compiled_regexes:
                regex_lookup[canonical_form] = all_compiled_regexes

        return regex_lookup

    @staticmethod
    def _filter_non_empty_str(maybe_strings):
        return [
            s for s in maybe_strings
            if s and isinstance(s, str) and s.strip()
        ]

    def _compile_regexes(self, pattern_strings, ignore_case=False):
        re_flags = 0
        if ignore_case:
            re_flags |= re.IGNORECASE

        compiled_regexes = set()
        for pattern in pattern_strings:
            try:
                regex = re.compile(pattern, re_flags)
            except re.error as e:
                log.error('Invalid regex pattern "%s" in "%s" --- %s',
                          pattern, self.str_lookup_dict_filepath, e)
                continue
            compiled_regexes.add(regex)

        return compiled_regexes


def build_string_value_canonicalizer(yaml_config_filename):
    yaml_config_filepath = _relative_absolute_path(yaml_config_filename)
    try:
        config_data = disk.load_yaml_file(yaml_config_filepath)
    except (exceptions.FilesystemError, disk.YamlLoadError) as e:
        # TODO: [TD0164] Fix mismatched throwing/catching of exceptions ..
        log.critical(
            'Error while loading string canonicalizer YAML file "%s" :: %s',
            enc.displayable_path(yaml_config_filepath), str(e)
        )
        return None

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
