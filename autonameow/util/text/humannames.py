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

import re

from thirdparty import nameparser
from util import sanity


RE_AUTHOR_ET_AL = re.compile(
    r'[\[\(\{]?et.al\.?[\]\)\}]?', re.IGNORECASE
)
RE_AUTHOR_PREFIX = re.compile(
    r'author:? ', re.IGNORECASE
)
RE_EDITED_BY = re.compile(
    r'ed(\.|ited) by', re.IGNORECASE
)
RE_REPEATING_PERIODS = re.compile(
    r'\.\.+', re.IGNORECASE
)


BLACKLISTED_HUMAN_NAMES = frozenset([
    'author',
    'dvd presenter',
    'editor',
    'inc',
    'presenter',
    'reviewer',
    'technical editor',
    'technical review',
])


def strip_author_et_al(string):
    """
    Attempts to remove variations of "et al." from a Unicode string.
    """
    subbed = RE_AUTHOR_ET_AL.sub('', string).replace('...', '')
    return subbed.strip().rstrip(',').lstrip('.')


def strip_edited_by(string):
    return RE_EDITED_BY.sub('', string).strip()


def strip_author_prefix(string):
    return RE_AUTHOR_PREFIX.sub('', string).strip()


def strip_repeating_periods(string):
    return RE_REPEATING_PERIODS.sub('', string).strip()


def strip_bad_author_substrings(string):
    assert isinstance(string, str)
    s = string
    s = strip_repeating_periods(s)
    s = strip_edited_by(s)
    s = strip_author_prefix(s)
    s = strip_author_et_al(s)

    if s.lower().startswith('by '):
        s = s[3:]

    return s


def _parse_name(human_name):
    """
    Thin wrapper around 'nameparser'.

    Translates the instance of 'HumanName' returned by 'nameparser' to a dict.

    Args:
        human_name: The name to parse as a Unicode string.

    Returns:
        A dict of data returned by the 'HumanName' class or an empty dict if
        "nameparser" is unavailable or the parsing returns non-True.
    """
    if nameparser:
        parsed = nameparser.HumanName(human_name)
        if parsed:
            # Some first names are misinterpreted as titles.
            if not parsed.first:
                _first_list = parsed.title_list
            else:
                _first_list = parsed.first_list

            return {
                'first': parsed.first or '',
                'first_list': _first_list or [],
                'last': parsed.last.replace(' ', '') or '',
                'last_list': parsed.last_list or [],
                'middle': parsed.middle or '',
                'middle_list': parsed.middle_list or [],
                'original': parsed.original or '',
                'suffix': parsed.suffix or '',
                'title': parsed.title or '',
                'title_list': parsed.title_list or [],
            }
    return {}


class HumanNameParser(object):
    # List of words to exclude from the output.
    IGNORED_AUTHOR_WORDS = frozenset([
        '',
    ])

    def __call__(self, name):
        if name is None:
            return {}
        sanity.check_internal_string(name)

        preprocessed_name = self._preprocess(name)
        parsed_name = _parse_name(preprocessed_name)
        if not parsed_name:
            return {}

        checked_parsed_name = self._check_bad_nameparser_result(parsed_name)
        return checked_parsed_name

    @classmethod
    def _check_bad_nameparser_result(cls, parsed_name):
        # Check for bad handling of names like 'Regina O. Obe'
        original_parts = parsed_name.get('original', '').split(' ')
        if len(original_parts) == 3 and re.match(r'[A-Z]\.', original_parts[1]):
            if parsed_name.get('suffix', '') == original_parts[2]:
                # Last name mistaken for suffix
                # Middle name mistaken for last name
                if not parsed_name.get('middle'):
                    parsed_name['suffix'] = ''
                    parsed_name['suffix_list'] = ['']
                    parsed_name['middle'] = original_parts[1]
                    parsed_name['middle_list'] = [original_parts[1]]
                    parsed_name['last'] = original_parts[2]
                    parsed_name['last_list'] = [original_parts[2]]
        return parsed_name

    @classmethod
    def _preprocess(cls, name):
        return filter_name(name)


class HumanNameFormatter(object):
    """
    Base class for all human name formatters with shared utility functionality.

    Instances of this class and its inheriting classes should *NOT* retain any
    kind of state. Inheriting classes should implement the 'format()' method
    and regular expression 'RE_FORMATTED_NAME' that matches the output format.

    Example usage:  formatted = HumanNameFormatterSubclass()('Lord Gibson III')
    """
    # Regex matching names in the class-specific format.
    # NOTE: This __MUST__ be defined by inheriting classes!
    RE_FORMATTED_NAME = None

    def __call__(self, parsed_name):
        sanity.check_isinstance(parsed_name, dict)
        if not self.RE_FORMATTED_NAME:
            raise NotImplementedError(
                'Inheriting classes must define "RE_FORMATTED_NAME"'
            )

        _original_string = parsed_name.get('original', '')
        if self._is_formatted(_original_string):
            return _original_string

        return self.format(parsed_name)

    @classmethod
    def _is_formatted(cls, name):
        """
        Return names that are already in the output format as-is.
        """
        if cls.RE_FORMATTED_NAME.match(name):
            return True
        return False

    def format(self, name):
        """
        Formats a human name to a class-specific format.

          NOTE: This method __MUST__ be implemented by inheriting classes!

        Args:
            name: The human name to format as a Unicode string.

        Returns:
            A formatted version of the given name as a Unicode string.
        """
        raise NotImplementedError('Must be implemented by inheriting classes.')


class LastNameInitialsFormatter(HumanNameFormatter):
    """
    Formats a full name to LAST_NAME, INITIALS..
    Example:  "Gibson Cat Sjöberg" is returned as "Sjöberg G.C."
    """
    RE_FORMATTED_NAME = re.compile(r'[\w-]+ (\w\.)+$')

    def format(self, parsed_name):
        first_list = parsed_name.get('first_list', '')
        middle_list = parsed_name.get('middle_list', '')
        last = parsed_name.get('last', '')

        def _to_initial(string):
            string = string.strip('.')
            try:
                return string[0]
            except IndexError:
                return ''

        _initials = [_to_initial(f) for f in first_list]
        _initials += [_to_initial(m) for m in middle_list]
        initials = '{0}{1}'.format('.'.join(_initials), '.')

        return '{} {}'.format(last, initials).strip()


DEFAULT_NAME_FORMATTER = LastNameInitialsFormatter


def format_name_list(list_of_human_names, formatter=None):
    """
    Formats a list of human names using a specific formatter.

    This is intended to be the primary public interface for formatting names.
    The name is first "parsed" into a dict that is then passed to the formatter.

    Args:
        list_of_human_names: List of human names as Unicode strings.
        formatter: Callable that accepts an returns a Unicode string.
                   Argument is optional and uses a default in unspecified.

    Returns:
        A lexicographically sorted list of the given names as Unicode strings,
        after having been processed by "formatter".
    """
    if not formatter:
        formatter = DEFAULT_NAME_FORMATTER

    assert callable(formatter), 'Argument "formatter" must be callable'
    if issubclass(formatter, HumanNameFormatter):
        # Cannot call the class directly, requires instantiating first.
        formatter = formatter()

    parser = HumanNameParser()
    _parsed_names = [parser(n) for n in list_of_human_names]
    if not _parsed_names:
        return []

    _formatted_names = [formatter(n) for n in _parsed_names]
    return sorted(_formatted_names, key=str.lower)


def format_name(human_name, formatter=None):
    """
    Formats a human name using a specific formatter.

    This is intended to be the primary public interface for formatting a name.
    The name is first "parsed" into a dict that is then passed to the formatter.

    Args:
        human_name: Human name as a Unicode string.
        formatter: Callable that accepts an returns a Unicode string.
                   Argument is optional and uses a default in unspecified.

    Returns:
        The given name as a Unicode string, after processing by "formatter".
    """
    if not formatter:
        formatter = DEFAULT_NAME_FORMATTER

    assert callable(formatter), 'Argument "formatter" must be callable'
    if issubclass(formatter, HumanNameFormatter):
        # Cannot call the class directly, requires instantiating first.
        formatter = formatter()

    _parsed_name = HumanNameParser()(human_name)
    if not _parsed_name:
        return ''

    return formatter(_parsed_name)


def remove_blacklisted_names(human_name):
    if human_name.lower().strip() in BLACKLISTED_HUMAN_NAMES:
        return ''
    return human_name


def split_multiple_names(list_of_names):
    # Local import to avoid circular imports within the 'util' module.
    from util import flatten_sequence_type

    RE_NAME_SEPARATORS = r',| ?\band| ?\+'

    result = list()
    flat_list_of_names = flatten_sequence_type(list_of_names)
    if len(flat_list_of_names) == 1 and flat_list_of_names[0].startswith('edited by'):
        # TODO: [hack] FIX THIS!
        # TODO: Some cases require filtering out substrings, which is
        #       currently typically done in a separate step after this
        #       function..
        return flat_list_of_names

    for name_or_names in flat_list_of_names:
        split_parts = re.split(RE_NAME_SEPARATORS, name_or_names)
        non_whitespace_parts = [p.strip() for p in split_parts if p]
        result.extend(non_whitespace_parts)
    return result


def filter_multiple_names(list_of_names):
    filter_output = list()
    for name in list_of_names:
        filtered_name = filter_name(name)
        if filtered_name and len(filtered_name) > 1:
            filter_output.append(filtered_name)

    return filter_output


def filter_name(human_name):
    name = remove_blacklisted_names(human_name)
    name = strip_bad_author_substrings(name)
    return name
