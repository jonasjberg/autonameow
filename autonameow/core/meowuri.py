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

from core import (
    types,
    util
)
from core import constants as C
from core.exceptions import InvalidMeowURIError


class MeowURI(object):
    """
    The "meowURI" consist of a lower case words, separated by periods.
    For instance; "contents.mime_type" or "filesystem.basename.extension".
    """
    def __init__(self, *args):
        if len(args) == 1:
            _raw_parts = self._split(args[0])
        else:
            _raw_parts = list(args)

        try:
            self._root = MeowURIRoot(_raw_parts.pop(0))
        except InvalidMeowURIError:
            self._root = None

        try:
            self._leaf = MeowURILeaf(_raw_parts.pop())
        except InvalidMeowURIError:
            self._leaf = None

        self._nodes = []
        if _raw_parts:
            self._nodes = [MeowURINode(p) for p in _raw_parts]

        self._parts = [self._root] + self._nodes + [self._leaf]

    @staticmethod
    def _split(string):
        try:
            s = types.AW_STRING(string)
        except types.AWTypeError:
            return []
        else:
            return util.meowuri_list(s)

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

    def eval_glob(self, glob_list):
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
        meowuri = self._raw_string

        if not meowuri or not glob_list:
            return False

        if not isinstance(glob_list, list):
            glob_list = [glob_list]

        if meowuri in glob_list:
            return True

        # Split the "meowURI" by periods to a list of strings.
        meowuri_parts = util.meowuri_list(meowuri)

        for glob in glob_list:
            glob_parts = glob.split('.')

            # All wildcards match anything.
            if len([gp for gp in glob_parts if gp == '*']) == len(glob_parts):
                return True

            # No wildcards, do direct comparison.
            if '*' not in glob_parts:
                if glob_parts == meowuri_parts:
                    return True
                else:
                    continue

            if glob.startswith('*.') and glob.endswith('.*'):
                # Check if the center piece is a match.
                literal_glob_parts = [g for g in glob_parts if g != '*']
                for literal_glob_part in literal_glob_parts:
                    # Put back periods to match whole parts and not substrings.
                    glob_center_part = '.{}.'.format(literal_glob_part)
                    if glob_center_part in meowuri:
                        return True

            # First part doesn't matter, check if trailing pieces match.
            if glob.startswith('*.'):
                stripped_glob = re.sub(r'^\*', '', glob)
                if meowuri.endswith(stripped_glob):
                    return True

            # Last part doesn't matter, check if leading pieces match.
            if glob.endswith('.*'):
                stripped_glob = re.sub(r'\*$', '', glob)
                if meowuri.startswith(stripped_glob):
                    return True

        return False

    def __str__(self):
        return C.MEOWURI_SEPARATOR.join(str(p) for p in self._parts)


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
