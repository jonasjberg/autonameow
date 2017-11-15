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

import re

from core.util import sanity
from thirdparty import nameparser


RE_AUTHOR_ET_AL = re.compile(
    r'[\[\(\{]?et.al\.?[\]\)\}]?', re.IGNORECASE
)


def strip_author_et_al(string):
    """
    Attempts to remove variations of "et al." from a Unicode string.
    """
    _subbed = RE_AUTHOR_ET_AL.sub('', string).replace('...', '')
    return _subbed.strip().rstrip(',').lstrip('.')


def parse_name(human_name):
    """
    Thin wrapper around 'nameparser'.

    Args:
        human_name: The name to parse as a Unicode string.

    Returns:
        The parsed name as an instance of the 'HumanName' class or None if
        "nameparser" is unavailable.
    """
    if nameparser:
        return nameparser.HumanName(human_name)
    return None


class HumanNameFormatter(object):
    """
    Base class for all human name formatters with shared utility functionality.

    Instances of this class and its inheriting classes should *NOT* retain any
    kind of state. Inheriting classes should implement the 'format()' method.

    Example usage:  formatted = HumanNameFormatterSubclass()('Lord Gibson')
    """
    # List of words to exclude from the output.
    IGNORED_AUTHOR_WORDS = frozenset([
        '',
    ])

    def __call__(self, name):
        sanity.check_internal_string(name)
        preprocessed_name = self._preprocess(name)
        return self.format(preprocessed_name)

    def _preprocess(self, name):
        if not name or not name.strip():
            return ''

        for ignored_word in cls.IGNORED_AUTHOR_WORDS:
            name = name.replace(ignored_word, '')

        name = strip_author_et_al(name)
        name = name.strip().rstrip(',').lstrip('.')
        return name

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
    def format(self, name):
        """
        Formats a full name to LAST_NAME, INITIALS..

        Example:  "Gibson Cat Sjöberg" is returned as "Sjöberg G.C."

        Args:
            name: The full name to format as a Unicode string.

        Returns:
            The specified name written as LAST_NAME, INITIAL, INITIAL..
        """
        # Return names already in the output format as-is.
        if re.match(r'[\w-]+ (\w\.)+$', name):
            return name

        # Using the third-party 'nameparser' module.
        _human_name = parse_name(name)
        if not _human_name:
            return ''

        # Some first names are misinterpreted as titles.
        if _human_name.first == '':
            first_list = _human_name.title_list
        else:
            first_list = _human_name.first_list

        def _to_initial(string):
            string = string.strip('.')
            try:
                return string[0]
            except IndexError:
                return ''

        initials = [_to_initial(f) for f in first_list]
        initials += [_to_initial(m) for m in _human_name.middle_list]
        _initials = '{0}{1}'.format('.'.join(initials), '.')

        last_name = _human_name.last.replace(' ', '')
        return '{} {}'.format(last_name, _initials).strip()


DEFAULT_NAME_FORMATTER = LastNameInitialsFormatter


def format_name_list(list_of_human_names, formatter=None):
    """
    Formats a list of human names using a specific formatter.

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

    _formatted_names = [formatter(n) for n in list_of_human_names]
    return sorted(_formatted_names, key=str.lower)


def format_name(human_name, formatter=None):
    """
    Formats a human name using a specific formatter.

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

    return formatter(human_name)
