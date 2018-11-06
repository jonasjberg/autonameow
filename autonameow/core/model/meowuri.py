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
import re
from collections import namedtuple
from functools import lru_cache

from core import constants as C
from core.exceptions import InvalidMeowURIError
from util import coercers
from util import sanity
from util.misc import flatten_sequence_type


log = logging.getLogger(__name__)


MeowURIParts = namedtuple('MeowURIParts', 'root children leaf')


class MeowURIParser(object):
    @staticmethod
    def parse(*args):
        # Handle all kinds of combinations of arguments, lists and tuples.
        flattened = flatten_sequence_type(args)
        args_list = list(flattened)

        # Normalize into a list of period-separated Unicode words ..
        raw_parts = list()
        for arg in args_list:
            if isinstance(arg, (MeowURI, MeowURIChild, MeowURIRoot, MeowURILeaf)):
                # TODO: [performance] This is probably extremely inefficient ..
                arg = str(arg)

            if not isinstance(arg, str):
                raise InvalidMeowURIError(
                    'Invalid MeowURI part: {} "{!s}"'.format(type(arg), arg)
                )

            if is_meowuri_parts(arg):
                # Split the "MeowURI" by periods to a list of strings.
                parts_list = meowuri_list(arg)
                raw_parts.extend(parts_list)
            elif is_one_meowuri_part(arg):
                raw_parts.append(arg)
            else:
                raise InvalidMeowURIError(
                    'Invalid MeowURI part: "{!s}" ({})'.format(arg, type(arg))
                )

        if not raw_parts:
            raise InvalidMeowURIError('Insufficient and/or invalid arguments')

        # Get and remove the first element ("root")
        _first_part = raw_parts.pop(0)
        try:
            _root = MeowURIRoot(_first_part)
        except InvalidMeowURIError:
            raise

        # Get and remove the last element ("leaf")
        _last_part = None
        try:
            _last_part = raw_parts.pop()
        except IndexError:
            raise InvalidMeowURIError('MeowURI is incomplete')
        try:
            _leaf = MeowURILeaf(_last_part)
        except InvalidMeowURIError:
            _leaf = None

        # Remaining elements are children
        _children = list()
        if raw_parts:
            _children = [MeowURIChild(n) for n in raw_parts]

        return MeowURIParts(root=_root, children=_children, leaf=_leaf)


class MeowURI(object):
    """
    (Meow) _U_niform _R_esource _I_dentifier

    Instances of this class act as references to "some data".
    This convention is used throughout the application.

    The "MeowURI" consists of (lower-case?) words, separated by periods.

    Examples:   "generic.metadata.author"
                "extractor.filesystem.xplat.basename_prefix"
                "analyzer.filename.datetime"

    NOTE: Assume that instances of this class are immutable once instantiated.
    """
    def __init__(self, *args):
        meowuri_parts = MeowURIParser.parse(*args)
        self._root = meowuri_parts.root
        self._children = meowuri_parts.children
        self._leaf = meowuri_parts.leaf
        self._parts = (
            [meowuri_parts.root] + meowuri_parts.children + [meowuri_parts.leaf]
        )

        # Lazily computed.
        self.__cached_str = None

    @property
    def root(self):
        if self._root:
            return str(self._root)
        return C.MEOWURI_UNDEFINED_PART

    @property
    def children(self):
        if self._children:
            return [str(n) for n in self._children]
        return C.MEOWURI_UNDEFINED_PART

    @property
    def leaf(self):
        if self._leaf:
            return str(self._leaf)
        return C.MEOWURI_UNDEFINED_PART

    @property
    def parts(self):
        return self._parts

    def matchglobs(self, glob_list):
        """
        Evaluates this "MeowURI" against a list of "globs".
        """
        if not glob_list:
            return False

        if not isinstance(glob_list, list):
            glob_list = [glob_list]
        _meowuri_string = str(self)
        return evaluate_meowuri_globs(_meowuri_string, glob_list)

    @property
    def is_generic(self):
        return self.root == C.MEOWURI_ROOT_GENERIC

    def matches_start(self, item):
        return self._check_partial_match(item, 'startswith')

    def matches_end(self, item):
        return self._check_partial_match(item, 'endswith')

    def _check_partial_match(self, item, str_comparison_func):
        self_str = str(self)
        self_str_match_func = getattr(self_str, str_comparison_func)
        assert callable(self_str_match_func)

        if isinstance(item, str):
            if not item.strip():
                return False
            return self_str_match_func(item)
        elif isinstance(item, (self.__class__, MeowURIRoot, MeowURILeaf)):
            item_string = str(item)
            return self_str_match_func(item_string)
        return False

    def __contains__(self, item):
        if not isinstance(item, (str, self.__class__, MeowURIRoot, MeowURILeaf)):
            return False

        self_str = str(self)
        self_str_parts = meowuri_list(self_str)
        item_string = str(item)
        try:
            item_string_parts = meowuri_list(item_string)
        except InvalidMeowURIError:
            return False
        return any(p in self_str_parts for p in item_string_parts)

    def stripleaf(self):
        return MeowURI(self._parts[:-1])

    def __eq__(self, other):
        if isinstance(other, str):
            return str(self) == other
        elif isinstance(other, self.__class__):
            return str(self) == str(other)
        return False

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            sp = len(self.parts)
            op = len(other.parts)
            if sp != op:
                return sp < op
            if self.root != other.root:
                return self.root < other.root
            if self.children != other.children:
                return self.children < other.children
            if self.leaf != other.leaf:
                return self.leaf < other.leaf

        raise TypeError('unorderable types: {!s} < {!s}'.format(
            self.__class__, other.__class__
        ))

    def __gt__(self, other):
        return not self < other

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        if not self.__cached_str:
            self.__cached_str = C.MEOWURI_SEPARATOR.join(str(p)
                                                         for p in self._parts)
        return self.__cached_str

    def __repr__(self):
        return '<{}({!s})>'.format(self.__class__.__name__, self)


class MeowURINode(object):
    # TODO: [cleanup] Currently unused!
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.children = list()

    def _get_self_and_all_parents(self):
        traversed_nodes = [self]
        node = self
        while node.parent is not None:
            node = node.parent
            traversed_nodes.append(node)

        traversed_nodes.reverse()
        return traversed_nodes

    def make_absolute(self):
        resolved_nodes = self._get_self_and_all_parents()
        return C.MEOWURI_SEPARATOR.join([n.name for n in resolved_nodes])


class MeowURIChild(object):
    def __init__(self, raw_value):
        str_value = coercers.force_string(raw_value)
        normalized_str_value = _normalize_string(str_value)
        self._validate(normalized_str_value)
        self._value = normalized_str_value

    def _validate(self, string):
        if not string:
            raise InvalidMeowURIError('Got empty string')
        if string in C.MEOWURI_ROOTS:
            raise InvalidMeowURIError(
                'Child must not contain root node: "{!s}"'.format(string)
            )

    def __str__(self):
        return self._value


class MeowURILeaf(object):
    def __init__(self, raw_value):
        str_value = coercers.force_string(raw_value)
        self._validate(str_value)
        self._value = str_value

    def _validate(self, string):
        if not string:
            raise InvalidMeowURIError('Got empty string')
        if string in C.MEOWURI_ROOTS:
            raise InvalidMeowURIError(
                'Leaf must not contain root node: "{!s}"'.format(string)
            )

    def __str__(self):
        return self._value


class MeowURIRoot(object):
    def __init__(self, raw_value):
        str_value = coercers.force_string(raw_value)
        normalized_str_value = _normalize_string(str_value)
        self._validate(normalized_str_value)
        self._value = normalized_str_value

    def _validate(self, string):
        if not string:
            raise InvalidMeowURIError('Got empty string')
        if string not in C.MEOWURI_ROOTS:
            raise InvalidMeowURIError(
                'Not a valid MeowURI root: "{!s}"'.format(string)
            )

    def __str__(self):
        return self._value


def _normalize_string(string):
    return string.lower().strip()


RE_MEOWURI_PART = re.compile(
    r'^{chars}+$'.format(chars=C.RE_ALLOWED_MEOWURI_PART_CHARS)
)
RE_MEOWURI_PARTS = re.compile(
    r'^{chars}+({sep}{chars}+)+$'.format(chars=C.RE_ALLOWED_MEOWURI_PART_CHARS,
                                         sep=re.escape(C.MEOWURI_SEPARATOR))
)


@lru_cache()
def is_one_meowuri_part(raw_string):
    """
    Safely check if an unknown (string) argument is a valid MeowURI part.

    Args:
        raw_string: The string to test. Types other than Unicode strings fail.

    Returns:
        True if "raw_string" is a Unicode string and a valid MeowURI part.
        False for any other case, including errors. Exceptions are suppressed.
    """
    try:
        return bool(RE_MEOWURI_PART.match(raw_string))
    except (TypeError, ValueError):
        return False


@lru_cache()
def is_meowuri_parts(string):
    try:
        return bool(RE_MEOWURI_PARTS.match(string))
    except (TypeError, ValueError):
        return False


@lru_cache(maxsize=512)
def meowuri_list(meowuri_string, sep=str(C.MEOWURI_SEPARATOR)):
    """
    Splits a "MeowURI" string with parts separated by 'sep' into a list.

    Example MeowURI:    'extractor.metadata.exiftool.createdate'
    Resulting output:   ['extractor', 'metadata', 'exiftool', 'createdate']

    Args:
        meowuri_string (str): The "MeowURI" string to split.
        sep (str): Separator between parts.

    Returns: The components of the given "MeowURI" string as a list.
    """
    if not isinstance(meowuri_string, str):
        raise InvalidMeowURIError('MeowURI string must be of type "str"')

    meowuri_string = meowuri_string.strip()
    if not meowuri_string:
        raise InvalidMeowURIError('Got empty MeowURI string')

    if sep in meowuri_string:
        # Remove any leading/trailing separators.
        if meowuri_string.startswith(sep):
            meowuri_string = meowuri_string.lstrip(sep)
        if meowuri_string.endswith(sep):
            meowuri_string = meowuri_string.rstrip(sep)

        # Collapse any repeating separators.
        repeated_separators = 2 * sep
        while repeated_separators in meowuri_string:
            meowuri_string = meowuri_string.replace(repeated_separators, sep)

        # Check if input is all separators.
        if not meowuri_string.replace(sep, '').strip():
            raise InvalidMeowURIError('Invalid MeowURI string')

    parts = meowuri_string.split(sep)
    return [p for p in parts if p]


@lru_cache(maxsize=512)
def _evaluate_glob(glob, meowuri_string, sep):
    glob_parts = glob.split(sep)

    # All wildcards match anything.
    if len([gp for gp in glob_parts if gp == '*']) == len(glob_parts):
        return True

    # No wildcards, do direct comparison.
    if '*' not in glob_parts:
        if glob == meowuri_string:
            return True
        return None

    if glob.startswith('*'+sep) and glob.endswith(sep+'*'):
        # Check if the center piece is a match.
        literal_glob_parts = [g for g in glob_parts if g != '*']
        for literal_glob_part in literal_glob_parts:
            # Put back periods to match whole parts and not substrings.
            glob_center_part = '{sep}{lit}{sep}'.format(sep=sep, lit=literal_glob_part)
            if glob_center_part in meowuri_string:
                return True

    # First part doesn't matter, check if trailing pieces match.
    if glob.startswith('*'+sep):
        stripped_glob = re.sub(r'^\*', '', glob)
        if meowuri_string.endswith(stripped_glob):
            return True

    # Last part doesn't matter, check if leading pieces match.
    if glob.endswith(sep+'*'):
        stripped_glob = re.sub(r'\*$', '', glob)
        if meowuri_string.startswith(stripped_glob):
            return True

    return None


def evaluate_meowuri_globs(meowuri_string, glob_list,
                           sep=str(C.MEOWURI_SEPARATOR)):
    """
    Evaluates a "MeowURI" string against a list of "globs".

    Matching any of the given globs evaluates true.

    Globs substitute any of the lower case words with an asterisk,
    which means that part is ignored during the comparison. Examples:

        meowuri                     glob_list                   evaluates
        'contents.bar'              ['contents.bar']            True
        'contents.foo'              ['foo.*', 'contents.*']     True
        'foo.bar'                   ['*.*']                     True
        'filesystem.basename_full'  ['contents.*', '*.parent']  False

    Note that the separator (currently a period) is defined in 'constants.py'.

    Args:
        meowuri_string (str): A string representation of a MeowURI.
        glob_list: A list of globs as strings.
        sep (str): Separator between parts.

    Returns:
        True if any of the given globs matches, else False.
    """
    if not meowuri_string or not glob_list:
        return False

    sanity.check_isinstance(glob_list, list)

    for glob in glob_list:
        if not isinstance(glob, (str, MeowURI)):
            raise TypeError(
                'Expected "glob_list" to be a list of Unicode strings'
                ' and/or instances of the "MeowURI" class'
            )

    # Convert elements (either instances of 'MeowURI' or str) to strings.
    glob_list = [str(g) for g in glob_list]

    if meowuri_string in glob_list:
        return True

    for glob in glob_list:
        result = _evaluate_glob(glob, meowuri_string, sep)
        if result is not None:
            return result

    return False


def force_meowuri(*args):
    """
    Returns a valid MeowURI or None, ignoring any and all exceptions.
    """
    try:
        return MeowURI(args)
    except InvalidMeowURIError:
        return None
