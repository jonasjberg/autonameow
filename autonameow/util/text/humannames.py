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

import re

import nameparser
from util.text.regexcache import RegexCache
from util.text import substring


# TODO: [TD0195] Handle malformed metadata with duplicated authors
#       Detect and filter duplicated authors like ['Gibson Sjöberg', 'Gibson']


BLACKLISTED_HUMAN_NAMES = frozenset([
    'author',
    'contributing writers',
    'dvd presenter',
    'editor',
    'foreword',
    'inc',
    'jr.',
    'presenter',
    'reviewer',
    'technical editor',
    'technical review',
])


def strip_contributions(string):
    RE_CONTRIBUTIONS = r'(with )?contributions( by)? '
    regex = RegexCache(RE_CONTRIBUTIONS, flags=re.IGNORECASE)
    subbed_string = regex.sub('', string)
    return subbed_string.strip()


def strip_author_et_al(string):
    """
    Attempts to remove variations of "et al." from a Unicode string.
    """
    RE_AUTHOR_ET_AL = r'[\[\(\{]?et.al\.?[\]\)\}]?'
    regex = RegexCache(RE_AUTHOR_ET_AL, flags=re.IGNORECASE)

    subbed_string = regex.sub('', string).replace('...', '')
    return subbed_string.strip().rstrip(',').lstrip('.')


def strip_edited_by(string):
    RE_EDITED_BY = r'\(?,? ?(technical.)?ed(\.|ited|itor)( by)?\)?|\(ed\)'
    regex = RegexCache(RE_EDITED_BY, flags=re.IGNORECASE)
    subbed_string = regex.sub('', string)
    return subbed_string.strip()


def strip_foreword_by(string):
    RE_FOREWORD_BY = r'foreword( by)?:?'
    regex = RegexCache(RE_FOREWORD_BY, flags=re.IGNORECASE)
    subbed_string = regex.sub('', string)
    return subbed_string.strip()


def strip_author_prefix(string):
    RE_AUTHOR_PREFIX = r'author:? '
    regex = RegexCache(RE_AUTHOR_PREFIX, flags=re.IGNORECASE)
    subbed_string = regex.sub('', string)
    return subbed_string.strip()


def strip_repeating_periods(string):
    RE_REPEATING_PERIODS = r'\.\.+'
    regex = RegexCache(RE_REPEATING_PERIODS, flags=re.IGNORECASE)
    subbed_string = regex.sub('', string)
    return subbed_string.strip()


def strip_bad_author_substrings(string):
    assert isinstance(string, str)

    s = string
    s = strip_repeating_periods(s)
    s = strip_edited_by(s)
    s = strip_foreword_by(s)
    s = strip_author_prefix(s)
    s = strip_author_et_al(s)
    s = strip_contributions(s)

    leading_trailing_substring_regexes = [
        # Leading substrings to remove
        r'^[\[({;]',
        r'^(written )?(by )?',

        # Trailing substrings to remove
        r'[\])};]$',
    ]
    for pattern in leading_trailing_substring_regexes:
        s = re.sub(pattern, '', s, flags=re.IGNORECASE)

    return s


def _handle_letter_case_of_nobiliary_particle(s, particle):
    """
    Undoes a title-case transformation of certain parts of a full name.

    Returns the given string "s" with the first letter of "particle"
    lower-cased.
    Example usage:

    >>> _handle_letter_case_of_nobiliary_particle('Gibson Von Cheese', 'Von')
    'Gibson von Cheese'
    """
    assert isinstance(s, str)
    assert isinstance(particle, str)

    def __lower_first_upper_second(_match):
        _lowered_first = _match.group(1).lower()
        _lowered_second = _match.group(2).upper()
        return _lowered_first + _lowered_second

    pattern_with_spaces_match = ' {} '.format(particle)
    pattern_with_spaces_replace = pattern_with_spaces_match.lower()
    subbed = re.sub(pattern_with_spaces_match, pattern_with_spaces_replace, s)

    pattern_match = '({})([\w])'.format(particle)
    subbed = re.sub(pattern_match, __lower_first_upper_second, subbed)
    return subbed


def _handle_special_cases_of_name_letter_case(s):
    for particle in ('Van', 'Von'):
        s = _handle_letter_case_of_nobiliary_particle(s, particle)

    s = s.replace(' De ', ' de ')
    return s


def normalize_letter_case(string):
    assert isinstance(string, str)

    title_case_string = string.title()
    title_case_name = _handle_special_cases_of_name_letter_case(title_case_string)
    return title_case_name


def _parse_name(human_name):
    """
    Thin wrapper around 'nameparser'.

    Translates the instance of 'HumanName' returned by 'nameparser' to a dict.

    Args:
        human_name: The name to parse as a Unicode string.

    Returns:
        A dict of data returned by the 'HumanName' class or an empty dict if
        the parsing returns non-True.
    """
    parsed = nameparser.HumanName(human_name)
    if not parsed:
        return dict()

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


class HumanNameParser(object):
    def __call__(self, name):
        if name is None:
            return {}
        assert isinstance(name, str)

        preprocessed_name = self._preprocess(name)
        parsed_name = _parse_name(preprocessed_name)
        if not parsed_name:
            return {}

        checked_parsed_name = self._check_bad_nameparser_result(parsed_name)
        return checked_parsed_name

    @classmethod
    def _check_bad_nameparser_result(cls, parsed_name):
        original_parts = parsed_name.get('original', '').split(' ')
        if len(original_parts) == 3:
            # Correct for bad handling of names like 'Regina O. Obe'
            if re.match(r'[A-Z]\.', original_parts[1]):
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

            # Correct for bad handling of names like 'Le Minh Nguyen'.
            elif (parsed_name['original'] == parsed_name['first']
                  and parsed_name['last'] == ''
                  and parsed_name['middle'] == ''
                  and parsed_name['suffix'] == ''
                  and parsed_name['title'] == ''):
                parsed_name['first'] = original_parts[0]
                parsed_name['first_list'] = [original_parts[0]]
                parsed_name['middle'] = original_parts[1]
                parsed_name['middle_list'] = [original_parts[1]]
                parsed_name['last'] = original_parts[2]

            # Correct for bad handling of names like 'Shiva Prasad K.M.'
            elif re.match(r'([A-Z]\.)+', parsed_name['last']) and len(parsed_name['last_list']) == 1:
                # Swap 'last' with 'middle' and 'last_list' with 'middle_list'.
                misplaced_last = parsed_name['middle']
                misplaced_last_list = parsed_name['middle_list']
                misplaced_middle = parsed_name['last']
                misplaced_middle_list = [
                    s for s
                    in parsed_name['last_list'][0].split('.')
                    if s.strip()
                ]
                parsed_name['last'] = misplaced_last
                parsed_name['last_list'] = misplaced_last_list
                parsed_name['middle'] = misplaced_middle
                parsed_name['middle_list'] = misplaced_middle_list

        elif len(original_parts) == 2:
            # Correct for bad handling of names like 'I.N. Bronsh'
            if re.match(r'([A-Z]\.){2,}', original_parts[0]):
                if (parsed_name['first'] == parsed_name['first_list'][0]
                        and parsed_name['last'] == parsed_name['last_list'][0]
                        and not parsed_name['middle']
                        and not parsed_name['middle_list']
                        and not parsed_name['suffix']
                        and not parsed_name['title']
                        and not parsed_name['title_list']):

                    initials = [
                        s for s in parsed_name['first'].split('.') if s.strip()
                    ]
                    first_initial = initials[0]
                    remaining_initials = initials[1:]
                    parsed_name['first'] = first_initial
                    parsed_name['first_list'] = [first_initial]
                    parsed_name['middle'] = remaining_initials[0]
                    parsed_name['middle_list'] = remaining_initials

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
        assert isinstance(parsed_name, dict)
        if not self.RE_FORMATTED_NAME:
            raise NotImplementedError(
                'Inheriting classes must define "RE_FORMATTED_NAME"'
            )

        _original_string = parsed_name.get('original', '')
        if self._original_name_is_already_formatted(_original_string):
            return _original_string

        return self.format(parsed_name)

    @classmethod
    def _original_name_is_already_formatted(cls, name):
        """
        Return names that are already in the output format as-is.
        """
        return bool(cls.RE_FORMATTED_NAME.match(name))

    def format(self, name):
        """
        Formats a human name to a class-specific format.

          NOTE: This method __MUST__ be implemented by inheriting classes!

        Args:
            name (str): The human name to format as a Unicode string.

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

    RE_NAME_SEPARATORS = r';|,| ?\b[aA]nd | ?\+| ?& ?|[\[\]]'

    flat_list_of_names = flatten_sequence_type(list_of_names)
    if len(flat_list_of_names) == 1 and flat_list_of_names[0].startswith('edited by'):
        # TODO: [hack] FIX THIS!
        # TODO: Some cases require filtering out substrings, which is
        #       currently typically done in a separate step after this
        #       function..
        return flat_list_of_names

    if len(flat_list_of_names) == 1:
        name_or_names = flat_list_of_names[0]
        separator_chars = substring.find_separators(name_or_names)

        # Make a string from the unique non-whitespace separator-chars.
        stripped_separator_chars = ''.join(set(c.strip() for c in separator_chars))
        if ';' in stripped_separator_chars and ',' in stripped_separator_chars:
            # TODO: [hack] Clean up adding/removing from 'RE_NAME_SEPARATORS'!

            # The point of this is to remove ',' from 'RE_NAME_SEPARATORS'
            # when both ',' and ';' are potential separator characters.
            RE_NAME_SEPARATORS = r';| ?\band| ?\+| ?& ?'

        elif re.match(r'\w+, \w', name_or_names):
            # Detect cases like ['Paul, Baz'] and return as-is.
            return [name_or_names]

    elif len(flat_list_of_names) > 1:
        if all(re.match(r'\w+, \w', p) for p in flat_list_of_names):
            # Detect cases like ['Foobar, S.', 'Paul, Baz', 'Gibson, N.']
            # where ',' should NOT be used as a separator.
            return flat_list_of_names

    result = list()
    for name_or_names in flat_list_of_names:
        split_parts = re.split(RE_NAME_SEPARATORS, name_or_names)
        non_whitespace_parts = [p.strip() for p in split_parts if p.strip()]
        result.extend(non_whitespace_parts)

    if len(flat_list_of_names) == len(result):
        # Splitting by various separators had no effect.
        if len(flat_list_of_names) > 2:
            if any(re.match(r'^\w\.$', p) for p in flat_list_of_names):
                # At least of the names is something like 'X.'
                # Assume the list of names should actually be put back together
                # rather than split.. Join parts in groups of two.
                groups_of_two = (
                    flat_list_of_names[i:i+2]
                    for i in range(0, len(flat_list_of_names), 2)
                )
                joined_names = [' '.join(part) for part in groups_of_two]
                return joined_names

    return result


def filter_multiple_names(list_of_names):
    filter_output = list()
    for name in list_of_names:
        filtered_name = filter_name(name)
        if filtered_name and len(filtered_name) > 1:
            # TODO: [cleanup][hack]: Deals with a single very special case ..
            # Given a filtered name like this:
            # 'Gibson Ford ... Technical reviewers: Smulan Ferrari ...',
            # only the first name, 'Gibson Ford' is returned.
            m = re.match(r'^([\w ]+)( Technical Reviewers: .*)', filtered_name)
            if m:
                filtered_name = m.group(1).strip()

            filter_output.append(filtered_name)

    return filter_output


def filter_name(human_name):
    assert isinstance(human_name, str)

    name = human_name.strip()
    if name:
        name = remove_blacklisted_names(name)
        name = strip_bad_author_substrings(name)
        name = normalize_letter_case(name)

    return name


def preprocess_names(list_of_names):
    """
    Primary "public" filtering/cleanup function for incoming raw names.

    Intended to process lists of strings of names from any kind of source.
    Wraps all other filtering functionality provided by this module.
    """
    assert isinstance(list_of_names, list)
    assert all(isinstance(s, str) for s in list_of_names)

    return split_multiple_names(filter_multiple_names(list_of_names))
