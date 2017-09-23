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

from core import util, types
from core.exceptions import InvalidMeowURIError

VALID_MEOWURI_ROOTS = frozenset(
    ['plugin', 'contents', 'metadata', 'filesystem']
)


class MeowURI(object):
    """
    The "meowURI" consist of a lower case words, separated by periods.
    For instance; "contents.mime_type" or "filesystem.basename.extension".
    """
    def __init__(self, string):
        self._raw_string = string
        _raw_parts = util.meowuri_list(string)
        _root = MeowURIRoot(_raw_parts.pop(0))
        _leaf = MeowURILeaf(_raw_parts.pop())

        _mids = []
        if _raw_parts:
            _mids = [MeowURINode(p) for p in _raw_parts]

        self._parts = [_root] + _mids + [_leaf]

    @property
    def root(self):
        return self._root

    def __getattr__(self, item):
        print('getattr: "{!s}"'.format(item))
        return 'FOO'

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


class MeowURINode(object):
    def __init__(self, raw_string):
        string = _normalize_string(raw_string)

    def _validate(self, string):
        raise NotImplementedError

    def __str__(self):
        return str(self.string) or 'NONE'


class MeowURILeaf(object):
    def __init__(self, raw_string):
        pass


class MeowURIRoot(object):
    def __init__(self, raw_string):
        string = _normalize_string(raw_string)
        self._validate(string)

    def _validate(self, string):
        if not string:
            raise InvalidMeowURIError
        if string not in VALID_MEOWURI_ROOTS:
            raise InvalidMeowURIError


def _normalize_string(raw_string):
    try:
        string = types.AW_STRING(raw_string)
    except types.AWTypeError:
        return None
    else:
        return string.lower().strip()
