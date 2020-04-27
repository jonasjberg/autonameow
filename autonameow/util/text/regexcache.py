# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2020 Jonas Sjöberg <autonameow@jonasjberg.com>
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


class _RegexCache(object):
    def __init__(self):
        self._compiled_regexes = dict()

    def _get_or_compile_and_store(self, pattern, flags=None):
        assert isinstance(pattern, str)
        if flags is None:
            flags = 0

        key = (pattern, flags)
        if key not in self._compiled_regexes:
            regex = re.compile(pattern, flags)
            self._compiled_regexes[key] = regex

        return self._compiled_regexes[key]

    def __call__(self, pattern, flags=None):
        return self._get_or_compile_and_store(pattern, flags)

    def __len__(self):
        return len(self._compiled_regexes)


RegexCache = _RegexCache()
