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
import os
import re
from collections import defaultdict
from functools import lru_cache

from core import exceptions
from util import coercers
from util import disk
from util import encoding as enc


log = logging.getLogger(__name__)


_SELF_DIRPATH = coercers.AW_PATH(os.path.abspath(os.path.dirname(__file__)))


class KnownDataFileParser(object):
    SECTION_MATCH_ANY_LITERAL_CASESENSITIVE = 'match_any_literal'
    SECTION_MATCH_ANY_LITERAL_IGNORECASE = 'match_any_literal_ignorecase'
    # TODO: Implement 'match_any_literal_ignorecase'!
    SECTION_MATCH_ANY_REGEX_CASESENSITIVE = 'match_any_regex'
    SECTION_MATCH_ANY_REGEX_IGNORECASE = 'match_any_regex_ignorecase'

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

            literals_to_match = sections.get(self.SECTION_MATCH_ANY_LITERAL_CASESENSITIVE)
            if not literals_to_match:
                continue

            if not isinstance(literals_to_match, list):
                log.error('Invalid entry "%s" in "%s"', sections,
                          self.str_lookup_dict_filepath)
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

            maybe_ignorecase_patterns = sections.get(self.SECTION_MATCH_ANY_REGEX_IGNORECASE)
            _process_patterns(maybe_ignorecase_patterns, ignore_case=True)

            maybe_casesensitive_patterns = sections.get(self.SECTION_MATCH_ANY_REGEX_CASESENSITIVE)
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


def _get_lookup_cache():
    return defaultdict(dict)


def clear_lookup_cache():
    global _LOOKUP_CACHE
    _LOOKUP_CACHE = _get_lookup_cache()


_LOOKUP_CACHE = _get_lookup_cache()


@lru_cache()
def _resolve_abspath_from_datafile_basename(filename):
    bytestring_basename = coercers.AW_PATHCOMPONENT(filename)
    if not bytestring_basename.endswith(b'.yaml'):
        bytestring_basename += b'.yaml'

    return disk.joinpaths(_SELF_DIRPATH, b'data', bytestring_basename)


def _get_known_data_file_parser(yaml_filepath):
    try:
        config_data = disk.load_yaml_file(yaml_filepath)
    except (exceptions.FilesystemError, disk.YamlLoadError) as e:
        # TODO: [TD0164] Fix mismatched throwing/catching of exceptions ..
        log.critical(
            'Error while loading string canonicalizer YAML file "%s" :: %s',
            enc.displayable_path(yaml_filepath), str(e)
        )
        return None

    parser = KnownDataFileParser(config_data, yaml_filepath)
    return parser


def _try_parse_data_and_populate_lookup_cache(fieldname):
    yaml_filepath = _resolve_abspath_from_datafile_basename(fieldname)
    if not disk.isfile(yaml_filepath):
        return False

    parser = _get_known_data_file_parser(yaml_filepath)
    if not parser:
        return False

    _LOOKUP_CACHE[fieldname]['regex'] = parser.parsed_regex_lookup
    _LOOKUP_CACHE[fieldname]['literal'] = parser.parsed_literal_lookup
    return True


def literal_lookup_dict(fieldname):
    """
    Returns a dictionary with canonical values of the given field name storing
    sets of "equivalent" literal string values.

    Args:
        fieldname: Field value corresponding to the basenames of files stored
                   in the 'data' directory.

    Returns:
        A dict keyed by canonical Unicode string values, storing sets of
        "equivalent" literal string values that could be replaced with the
        canonical value.
    """
    if fieldname in _LOOKUP_CACHE:
        return _LOOKUP_CACHE[fieldname]['literal']

    if _try_parse_data_and_populate_lookup_cache(fieldname):
        return _LOOKUP_CACHE[fieldname]['literal']

    return dict()


def regex_lookup_dict(fieldname):
    """
    Returns a dictionary with canonical values of the given field name storing
    sets of "equivalent" compiled regular expressions.

    Args:
        fieldname: Field value corresponding to the basenames of files stored
                   in the 'data' directory.

    Returns:
        A dict keyed by canonical Unicode string values, storing sets of
        "equivalent" compiled regular expressions that could be used to search
        for text to be replaced with the canonical value.
    """
    if fieldname in _LOOKUP_CACHE:
        return _LOOKUP_CACHE[fieldname]['regex']

    if _try_parse_data_and_populate_lookup_cache(fieldname):
        return _LOOKUP_CACHE[fieldname]['regex']

    return dict()


def lookup_values(fieldname):
    """
    Returns a set of all known canonical values for the given field name.

    The returned set is the union of the sets of all keys in the regex and
    literal lookup dicts.

    Args:
        fieldname: Field value corresponding to the basenames of files stored
                   in the 'data' directory.

    Returns:
        A set of all known canonical values for the given field name.
    """
    def _merge_all_cached_lookup_keys(_fieldname):
        cached_lookups = _LOOKUP_CACHE[_fieldname]
        regex_lookup_keys = set(cached_lookups['regex'].keys())
        literal_lookup_keys = set(cached_lookups['literal'].keys())
        return set(regex_lookup_keys | literal_lookup_keys)

    if fieldname in _LOOKUP_CACHE:
        return _merge_all_cached_lookup_keys(fieldname)

    if _try_parse_data_and_populate_lookup_cache(fieldname):
        return _merge_all_cached_lookup_keys(fieldname)

    return set()
