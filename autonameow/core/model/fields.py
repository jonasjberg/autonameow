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

from core.model.normalize import (
    normalize_full_human_name,
    normalize_full_title
)


class BaseField(object):
    def __init__(self, value):
        self.value = value
        self.record = None

        self._normvalue = None
        self.normalize = lambda x: x

    @property
    def normvalue(self):
        if self._normvalue is None:
            self._normvalue = self.normalize(self.value)
        return self._normvalue

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.value == other.value:
            return True
        if self.normvalue == other.normvalue:
            return True

        return False

    def __bool__(self):
        return bool(self.normvalue)

    def __len__(self):
        return len(self.normvalue) or 0


class Author(BaseField):
    def __init__(self, value):
        super().__init__(value)
        self.normalize = normalize_full_human_name


class Title(BaseField):
    def __init__(self, value):
        super().__init__(value)
        self.normalize = normalize_full_title
