#!/usr/bin/env python3
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


class EventHandler(object):
    def __init__(self):
        self.callables = set()

    def add(self, func):
        assert callable(func), type(func)
        self.callables.add(func)

    def __call__(self, *args, **kwargs):
        for func in self.callables:
            func(*args, **kwargs)


class EventDispatcher(object):
    def __init__(self):
        self.on_startup = EventHandler()
        self.on_shutdown = EventHandler()


dispatcher = EventDispatcher()
