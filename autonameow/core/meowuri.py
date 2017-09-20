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

from core import util


class MeowURI(object):
    def __init__(self, content_string):
        _parts = util.meowuri_list(content_string)
        _root = MeowURIRoot(_parts.pop(0))
        _leaf = MeowURILeaf(_parts.pop())

        _mids = []
        if _parts:
            _mids = [MeowURINode(p) for p in _parts]

        self._parts = [_root] + _mids + [_leaf]

    @property
    def root(self):
        return self._root

    def __getattr__(self, item):
        print('getattr: "{!s}"'.format(item))
        return 'FOO'


class MeowURINode(object):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return str(self.name) or 'NONE'


class MeowURILeaf(MeowURINode):
    def __init__(self, name):
        super(MeowURILeaf, self).__init__(name)


class MeowURIRoot(MeowURINode):
    def __init__(self, name):
        super(MeowURIRoot, self).__init__(name)
