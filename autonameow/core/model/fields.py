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


class BaseField(object):
    def __init__(self, value):
        self.value = value
        self.record = None

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.value == other.value:
            return True

        return False

    @property
    def weight(self):
        return self._calculate_weight()

    def _calculate_weight(self):
        raise NotImplementedError('Must be implemented by inheriting classes.')

    # def relative_score(self, *others):
    #     raise NotImplementedError('Must be implemented by inheriting classes.')


class Author(BaseField):
    def _calculate_weight(self):
        if not self.value:
            return 0.0

        return 1.0

    # def relative_score(self, *others):
    #     for other in others:
    #         if


class Title(BaseField):
    def _calculate_weight(self):
        if not self.value:
            return 0.0

        return 1.0
