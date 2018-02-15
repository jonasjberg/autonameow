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
import re

from core import types
from core import constants as C
from core.exceptions import InvalidMeowURIError
from util import sanity
from util.misc import flatten_sequence_type


log = logging.getLogger(__name__)


# TODO: [TD0125] Add aliases (generics) for MeowURI leafs


class MeowURIParser(object):
    def parse(self, *args):
        # Handle all kinds of combinations of arguments, lists and tuples.
        flattened = flatten_sequence_type(args)
        args_list = list(flattened)

        # Normalize into a list of period-separated (Unicode(!)) words ..
        raw_parts = []
        for arg in args_list:
            if isinstance(arg, MeowURI):
                # TODO: This is probably extremely inefficient ..
                arg = str(arg)

            if is_meowuri_parts(arg):
                raw_parts.extend(self._split(arg))
            elif is_meowuri_part(arg):
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
        _children = []
        if raw_parts:
            _children = [MeowURIChild(n) for n in raw_parts]

        return _root, _children, _leaf

    @staticmethod
    def _split(raw_string):
        # TODO: Data has already passed through functions requiring Unicode str
        #       .. this makes no sense here.  Remove or relocate.
        string = types.force_string(raw_string)
        if string:
            # Split the "meowURI" by periods to a list of strings.
            return meowuri_list(string)
        return []


class MeowURI(object):
    """
    (Meow) _U_niform _R_esource _I_dentifier

    Instances of this class act as references to "some data".
    This convention is used throughout the application.

    The "MeowURI" consists of (lower-case?) words, separated by periods.

    Examples:   "generic.metadata.author"
                "extractor.filesystem.xplat.basename.prefix"
                "analyzer.filename.datetime"

    NOTE: Assume that instances of this class are immutable once instantiated.
    """
    MP = MeowURIParser()

    def __init__(self, *args):
        self._root, self._children, self._leaf = self.MP.parse(*args)
        self._parts = [self._root] + self._children + [self._leaf]

        # Lazily computed.
        self.__cached_str = None

    @property
    def root(self):
        if self._root:
            return str(self._root)
        return C.UNDEFINED_MEOWURI_PART

    @property
    def children(self):
        if self._children:
            return [str(n) for n in self._children]
        return C.UNDEFINED_MEOWURI_PART

    @property
    def leaf(self):
        if self._leaf:
            return str(self._leaf)
        return C.UNDEFINED_MEOWURI_PART

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

    def __contains__(self, item):
        _self_string = str(self)
        if isinstance(item, self.__class__):
            _item_string = str(item)
            return _self_string.startswith(_item_string)
        elif isinstance(item, str):
            if not item.strip():
                return False
            return _self_string.startswith(item)
        else:
            return False

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
        return str(self)


class MeowURIChild(object):
    def __init__(self, raw_string):
        string = _normalize_string(raw_string)
        self._validate(string)

        self._value = string

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
    def __init__(self, raw_string):
        string = raw_string.strip()
        self._validate(string)

        self._value = string

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
    def __init__(self, raw_string):
        string = types.force_string(raw_string)
        if string:
            string = _normalize_string(raw_string)

        self._validate(string)
        self._value = string

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


def is_meowuri_part(raw_string):
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


def is_meowuri_parts(string):
    try:
        return bool(RE_MEOWURI_PARTS.match(string))
    except (TypeError, ValueError):
        return False


def meowuri_list(meowuri):
    """
    Converts a "meowURI" to a list suited for traversing nested dicts.

    Example meowURI:    'extractor.metadata.exiftool.createdate'
    Resulting output:   ['extractor', 'metadata', 'exiftool', 'createdate']

    Args:
        meowuri: The "meowURI" to convert.

    Returns: The components of the given "meowURI" as a list.
    """
    if not isinstance(meowuri, str):
        raise InvalidMeowURIError('meowURI must be of type "str"')
    else:
        uri = meowuri.strip()
    if not uri:
        raise InvalidMeowURIError('Got empty meowURI')

    if '.' in uri:
        # Remove any leading/trailing periods.
        if uri.startswith('.'):
            uri = uri.lstrip('.')
        if uri.endswith('.'):
            uri = uri.rstrip('.')

        # Collapse any repeating periods.
        while '..' in uri:
            uri = uri.replace('..', '.')

        # Check if input is all periods.
        stripped_period = str(uri).replace('.', '')
        if not stripped_period.strip():
            raise InvalidMeowURIError('Invalid meowURI')

    parts = uri.split('.')
    return [p for p in parts if p is not None]


def evaluate_meowuri_globs(meowuri_string, glob_list):
    """
    Evaluates a "MeowURI" string against a list of "globs".

    Matching any of the given globs evaluates true.

    Globs substitute any of the lower case words with an asterisk,
    which means that part is ignored during the comparison. Examples:

        meowuri                     glob_list                   evaluates
        'contents.mime_type'        ['contents.mime_type']      True
        'contents.foo'              ['foo.*', 'contents.*']     True
        'foo.bar'                   ['*.*']                     True
        'filesystem.basename.full'  ['contents.*', '*.parent']  False

    Args:
        meowuri_string: A string representation of a MeowURI.
        glob_list: A list of globs as strings.

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
    _string_globs = [str(g) for g in glob_list]
    glob_list = _string_globs

    if meowuri_string in glob_list:
        return True

    for glob in glob_list:
        glob_parts = glob.split('.')

        # All wildcards match anything.
        if len([gp for gp in glob_parts if gp == '*']) == len(glob_parts):
            return True

        # No wildcards, do direct comparison.
        if '*' not in glob_parts:
            if glob == meowuri_string:
                return True
            else:
                continue

        if glob.startswith('*.') and glob.endswith('.*'):
            # Check if the center piece is a match.
            literal_glob_parts = [g for g in glob_parts if g != '*']
            for literal_glob_part in literal_glob_parts:
                # Put back periods to match whole parts and not substrings.
                glob_center_part = '.{}.'.format(literal_glob_part)
                if glob_center_part in meowuri_string:
                    return True

        # First part doesn't matter, check if trailing pieces match.
        if glob.startswith('*.'):
            stripped_glob = re.sub(r'^\*', '', glob)
            if meowuri_string.endswith(stripped_glob):
                return True

        # Last part doesn't matter, check if leading pieces match.
        if glob.endswith('.*'):
            stripped_glob = re.sub(r'\*$', '', glob)
            if meowuri_string.startswith(stripped_glob):
                return True

    return False


def force_meowuri(*args):
    """
    Returns a valid MeowURI or None, ignoring any and all exceptions.
    """
    try:
        return MeowURI(args)
    except InvalidMeowURIError:
        return None
