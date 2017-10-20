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

import logging
import re

from core import (
    types,
    util
)
from core import constants as C
from core.exceptions import InvalidMeowURIError


log = logging.getLogger(__name__)


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
    def __init__(self, *args):
        # This mess allows using either 'MeowURI(*args)' or 'MeowURI(args)'.
        _args_list = []
        for arg in args:
            if isinstance(arg, tuple):
                _args_list.extend([a for a in arg])
            elif isinstance(arg, list):
                log.debug('{!s} unexpectedly got list argument'.format(self))
                _args_list.extend(arg)
            else:
                _args_list.append(arg)

        # Normalize into a list of period-separated (Unicode(!)) words ..
        _raw_parts = []
        for arg in _args_list:
            if is_meowuri_parts(arg):
                _raw_parts.extend(self._split(arg))
            elif is_meowuri_part(arg):
                _raw_parts.append(arg)
            else:
                raise InvalidMeowURIError('Invalid arg: "{!s}"'.format(arg))

        if not _raw_parts:
            raise InvalidMeowURIError('Insufficient and/or invalid arguments')

        self._raw_parts = _raw_parts

        _first_part = _raw_parts.pop(0)
        try:
            self._root = MeowURIRoot(_first_part)
        except InvalidMeowURIError:
            raise

        _p = None
        try:
            _p = _raw_parts.pop()
        except IndexError:
            raise InvalidMeowURIError('MeowURI is incomplete')

        try:
            self._leaf = MeowURILeaf(_p)
        except InvalidMeowURIError:
            self._leaf = None

        self._nodes = []
        if _raw_parts:
            self._nodes = [MeowURINode(p) for p in _raw_parts]

        self._parts = [self._root] + self._nodes + [self._leaf]

        # Lazily computed.
        self.__cached_str = None

    @staticmethod
    def _split(raw_string):
        # TODO: Data has already passed through functions requiring Unicode str
        #       .. this makes no sense here.  Remove or relocate.
        string = types.force_string(raw_string)
        if not string:
            return []
        else:
            # Split the "meowURI" by periods to a list of strings.
            return meowuri_list(string)

    @classmethod
    def generic(cls, *args):
        if len(args) == 1:
            _raw_parts = cls._split(args[0])
        else:
            _raw_parts = list(args)

        if _raw_parts[0] != C.MEOWURI_ROOT_GENERIC:
            _parts = [C.MEOWURI_ROOT_GENERIC] + _raw_parts
            return cls(*_parts)
        else:
            return cls(*_raw_parts)

    @property
    def root(self):
        if self._root:
            return str(self._root)
        else:
            return C.UNDEFINED_MEOWURI_PART

    @property
    def nodes(self):
        if self._nodes:
            return [str(n) for n in self._nodes]
        else:
            return C.UNDEFINED_MEOWURI_PART

    @property
    def leaf(self):
        if self._leaf:
            return str(self._leaf)
        else:
            return C.UNDEFINED_MEOWURI_PART

    @property
    def parts(self):
        return self._parts

    def matchglobs(self, glob_list):
        """
        Evaluates this "meowURI" against a list of "globs".

        Matching any of the given globs evaluates true.

        Globs substitute any of the lower case words with an asterisk,
        which means that part is ignored during the comparison. Examples:

            meowuri                     glob_list                   evaluates
            'contents.mime_type'        ['contents.mime_type']      True
            'contents.foo'              ['foo.*', 'contents.*']     True
            'foo.bar'                   ['*.*']                     True
            'filesystem.basename.full'  ['contents.*', '*.parent']  False

        Args:
            glob_list: A list of globs as strings.

        Returns:
            True if any of the given globs matches, else False.
        """
        _meowuri_string = str(self)

        if not _meowuri_string or not glob_list:
            return False

        if not isinstance(glob_list, list):
            glob_list = [glob_list]

        if _meowuri_string in glob_list:
            return True

        for glob in glob_list:
            glob_parts = glob.split('.')

            # All wildcards match anything.
            if len([gp for gp in glob_parts if gp == '*']) == len(glob_parts):
                return True

            # No wildcards, do direct comparison.
            if '*' not in glob_parts:
                if glob_parts == self._raw_parts:
                    return True
                else:
                    continue

            if glob.startswith('*.') and glob.endswith('.*'):
                # Check if the center piece is a match.
                literal_glob_parts = [g for g in glob_parts if g != '*']
                for literal_glob_part in literal_glob_parts:
                    # Put back periods to match whole parts and not substrings.
                    glob_center_part = '.{}.'.format(literal_glob_part)
                    if glob_center_part in _meowuri_string:
                        return True

            # First part doesn't matter, check if trailing pieces match.
            if glob.startswith('*.'):
                stripped_glob = re.sub(r'^\*', '', glob)
                if _meowuri_string.endswith(stripped_glob):
                    return True

            # Last part doesn't matter, check if leading pieces match.
            if glob.endswith('.*'):
                stripped_glob = re.sub(r'\*$', '', glob)
                if _meowuri_string.startswith(stripped_glob):
                    return True

        return False

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
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            sp = len(self.parts)
            op = len(other.parts)
            if sp != op:
                return sp < op
            if self.root != other.root:
                return self.root < other.root
            if self.nodes != other.nodes:
                return self.nodes < other.nodes
            if self.leaf != other.leaf:
                return self.leaf < other.leaf
        else:
            # TODO: Else what?
            pass

    def __gt__(self, other):
        return not self < other

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        if not self.__cached_str:
            self.__cached_str = C.MEOWURI_SEPARATOR.join(str(p)
                                                         for p in self._parts)
        return self.__cached_str


class MeowURINode(object):
    def __init__(self, raw_string):
        string = _normalize_string(raw_string)
        self._validate(string)

        self._value = string

    def _validate(self, string):
        if not string:
            raise InvalidMeowURIError('Got empty string')
        if string in C.MEOWURI_ROOTS:
            raise InvalidMeowURIError(
                'Leaf must not contain root-node: "{!s}"'.format(string)
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
                'Leaf must not contain root-node: "{!s}"'.format(string)
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

    The MeowURI is

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
    # TODO: [TD0105] Consolidate this with the 'MeowURI' class.
    if not isinstance(meowuri, str):
        raise InvalidMeowURIError('meowURI must be of type "str"')
    else:
        _meowuri = meowuri.strip()
    if not _meowuri:
        raise InvalidMeowURIError('Got empty meowURI')

    if '.' in _meowuri:
        # Remove any leading/trailing periods.
        if _meowuri.startswith('.'):
            _meowuri = _meowuri.lstrip('.')
        if _meowuri.endswith('.'):
            _meowuri = _meowuri.rstrip('.')

        # Collapse any repeating periods.
        while '..' in _meowuri:
            _meowuri = _meowuri.replace('..', '.')

        # Check if input is all periods.
        stripped_period = str(_meowuri).replace('.', '')
        if not stripped_period.strip():
            raise InvalidMeowURIError('Invalid meowURI')

    parts = _meowuri.split('.')
    return [p for p in parts if p is not None]
